import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.db.models import Audit, Page, PageObservation, Link, Finding, Score, Recommendation
from app.crawler.crawler import WebsiteCrawler
from app.rules.seo_rules import SEORuleEngine
from app.engines.aeo_engine import AEOEngine
from app.engines.geo_engine import GEOEngine
from app.engines.scoring_engine import ScoringEngine
from app.engines.growth_engine import GrowthEngine

class AuditManager:
    @staticmethod
    async def run_audit(audit_id: str, root_url: str, crawl_mode: str = "quick", crawl_config: Optional[Dict[str, Any]] = None):
        cfg = crawl_config or {}
        max_urls = cfg.get("max_urls", 50 if crawl_mode == "quick" else 200)
        max_depth = cfg.get("max_depth", 3)
        respect_robots = cfg.get("respect_robots", True)
        allow_local_test = cfg.get("allow_local_test", True)

        async with AsyncSessionLocal() as db:
            # 1. initializing
            await db.execute(
                update(Audit)
                .where(Audit.id == audit_id)
                .values(status="initializing", started_at=datetime.now(timezone.utc))
            )
            await db.commit()

        try:
            # 2. crawling (includes discovering)
            async with AsyncSessionLocal() as db:
                await db.execute(update(Audit).where(Audit.id == audit_id).values(status="crawling"))
                await db.commit()

            crawler = WebsiteCrawler(
                audit_id=audit_id,
                root_url=root_url,
                max_urls=max_urls,
                max_depth=max_depth,
                respect_robots=respect_robots,
                allow_local_test=allow_local_test,
            )
            crawl_result = await crawler.run()

            # 3. validating (deterministic rules + AEO + GEO)
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(Audit)
                    .where(Audit.id == audit_id)
                    .values(status="validating", progress_pages=len(crawl_result.pages))
                )
                await db.commit()

            # Deterministic SEO rules
            seo_findings = SEORuleEngine.evaluate(
                audit_id=audit_id,
                pages=crawl_result.pages,
                links=crawl_result.links
            )

            # Heuristic AEO & GEO evaluations
            aeo_scores = []
            geo_scores = []
            aeo_findings = []
            geo_findings = []

            for p in crawl_result.pages:
                if p.get("http_status") == 200:
                    aeo_res, aeo_f = AEOEngine.evaluate_page(p, audit_id)
                    aeo_scores.append(aeo_res["aeo_score"])
                    aeo_findings.extend(aeo_f)

                    geo_res, geo_f = GEOEngine.evaluate_page(p, audit_id)
                    geo_scores.append(geo_res["geo_score"])
                    geo_findings.extend(geo_f)

            all_findings = seo_findings + aeo_findings + geo_findings

            # 4. scoring
            async with AsyncSessionLocal() as db:
                await db.execute(update(Audit).where(Audit.id == audit_id).values(status="scoring"))
                await db.commit()

            calculated_scores = ScoringEngine.calculate_scores(
                pages=crawl_result.pages,
                findings=all_findings,
                aeo_page_scores=aeo_scores,
                geo_page_scores=geo_scores
            )

            # 5. strategizing
            async with AsyncSessionLocal() as db:
                await db.execute(update(Audit).where(Audit.id == audit_id).values(status="strategizing"))
                await db.commit()

            recommendations = GrowthEngine.generate_recommendations(
                findings=all_findings,
                total_pages=len(crawl_result.pages)
            )

            # 6. persist all audit data to DB
            async with AsyncSessionLocal() as db:
                # Save Pages & Observations
                page_id_mapping = {}
                for idx, p in enumerate(crawl_result.pages):
                    new_page = Page(
                        audit_id=audit_id,
                        url=p["url"],
                        normalized_url=p["normalized_url"],
                        depth=p["depth"],
                        discovered_from=p["discovered_from"],
                    )
                    db.add(new_page)
                    await db.flush()
                    p_key = p.get("id", idx + 1)
                    page_id_mapping[p_key] = new_page.id

                    obs = PageObservation(
                        page_id=new_page.id,
                        http_status=p["http_status"],
                        content_type=p["content_type"],
                        title=p["title"],
                        meta_description=p["meta_description"],
                        canonical_url=p["canonical_url"],
                        robots=p["robots"],
                        lang=p["lang"],
                        word_count=p["word_count"],
                        response_time_ms=p["response_time_ms"],
                        ttfb_ms=p["ttfb_ms"],
                        html_hash=p["html_hash"],
                        observation=p.get("observation", {}),
                    )
                    db.add(obs)

                # Save Links
                for l in crawl_result.links:
                    mapped_source_id = page_id_mapping.get(l["source_page_id"])
                    if mapped_source_id:
                        db_link = Link(
                            audit_id=audit_id,
                            source_page_id=mapped_source_id,
                            target_url=l["target_url"],
                            normalized_target_url=l["normalized_target_url"],
                            anchor_text=l["anchor_text"],
                            is_internal=l["is_internal"],
                            rel=l["rel"],
                        )
                        db.add(db_link)

                # Save Findings
                for f in all_findings:
                    db_f = Finding(
                        id=f.finding_id,
                        audit_id=audit_id,
                        rule_id=f.rule_id,
                        page_id=page_id_mapping.get(f.page_id) if f.page_id else None,
                        severity=f.severity.value,
                        evidence_class=f.evidence_class.value,
                        status=f.status,
                        confidence=f.confidence,
                        evidence=f.evidence,
                        fingerprint=f.fingerprint,
                    )
                    db.add(db_f)

                # Save Scores
                for s in calculated_scores:
                    db_s = Score(
                        audit_id=audit_id,
                        dimension=s["dimension"],
                        score=s["score"],
                        confidence=s["confidence"],
                        evidence_class=s["evidence_class"],
                        methodology_version=s["methodology_version"],
                        inputs=s["inputs"],
                    )
                    db.add(db_s)

                # Save Recommendations
                for r in recommendations:
                    db_r = Recommendation(
                        id=r["id"],
                        audit_id=audit_id,
                        title=r["title"],
                        description=r["description"],
                        category=r["category"],
                        priority_group=r["priority_group"],
                        priority=r["priority"],
                        opportunity_score=r["opportunity_score"],
                        estimated_effort=r["estimated_effort"],
                        pros=r["pros"],
                        cons=r["cons"],
                        validation_method=r["validation_method"],
                        evidence=r["evidence"],
                    )
                    db.add(db_r)

                # Mark audit completed
                await db.execute(
                    update(Audit)
                    .where(Audit.id == audit_id)
                    .values(
                        status="completed",
                        completed_at=datetime.now(timezone.utc),
                        progress_pages=len(crawl_result.pages),
                    )
                )
                await db.commit()

        except Exception as e:
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(Audit)
                    .where(Audit.id == audit_id)
                    .values(
                        status="failed",
                        completed_at=datetime.now(timezone.utc),
                        config={**cfg, "error": str(e)},
                    )
                )
                await db.commit()
            raise e

    @staticmethod
    async def compare_audits(audit_a_id: str, audit_b_id: str) -> Dict[str, Any]:
        """
        Compare two audits using fingerprints (Spec Section 60):
        - New issues
        - Resolved issues
        - Changed issues
        - Score movements
        """
        async with AsyncSessionLocal() as db:
            findings_a = (await db.execute(select(Finding).where(Finding.audit_id == audit_a_id))).scalars().all()
            findings_b = (await db.execute(select(Finding).where(Finding.audit_id == audit_b_id))).scalars().all()
            scores_a = (await db.execute(select(Score).where(Score.audit_id == audit_a_id))).scalars().all()
            scores_b = (await db.execute(select(Score).where(Score.audit_id == audit_b_id))).scalars().all()
            pages_a = (await db.execute(select(Page).where(Page.audit_id == audit_a_id))).scalars().all()
            pages_b = (await db.execute(select(Page).where(Page.audit_id == audit_b_id))).scalars().all()

        fp_a = {f.fingerprint: f for f in findings_a}
        fp_b = {f.fingerprint: f for f in findings_b}

        new_issues = [f for fp, f in fp_b.items() if fp not in fp_a]
        resolved_issues = [f for fp, f in fp_a.items() if fp not in fp_b]
        persisting_issues = [f for fp, f in fp_b.items() if fp in fp_a]

        score_map_a = {s.dimension: s.score for s in scores_a}
        score_deltas = {}
        for sb in scores_b:
            prev = score_map_a.get(sb.dimension)
            score_deltas[sb.dimension] = {
                "before": prev,
                "current": sb.score,
                "delta": round(sb.score - prev, 1) if prev is not None else 0.0,
            }

        return {
            "audit_a_id": audit_a_id,
            "audit_b_id": audit_b_id,
            "new_issues_count": len(new_issues),
            "resolved_issues_count": len(resolved_issues),
            "persisting_issues_count": len(persisting_issues),
            "new_issues": [
                {"rule_id": f.rule_id, "severity": f.severity, "evidence_class": f.evidence_class, "evidence": f.evidence}
                for f in new_issues[:20]
            ],
            "resolved_issues": [
                {"rule_id": f.rule_id, "severity": f.severity, "evidence_class": f.evidence_class, "evidence": f.evidence}
                for f in resolved_issues[:20]
            ],
            "score_deltas": score_deltas,
            "pages_count_delta": len(pages_b) - len(pages_a),
        }
