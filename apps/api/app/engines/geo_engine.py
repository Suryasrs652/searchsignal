import uuid
import re
from typing import Dict, Any, List, Tuple
from app.core.config import settings
from app.rules.base import FindingItem, EvidenceClass, Severity, generate_fingerprint

class GEOEngine:
    @staticmethod
    def evaluate_page(page: Dict[str, Any], audit_id: str) -> Tuple[Dict[str, Any], List[FindingItem]]:
        obs = page.get("observation") or {}
        url = page["url"]
        norm_url = page["normalized_url"]
        page_id = page.get("id")
        
        text = obs.get("visible_text_snippet", "").lower()
        paragraphs = obs.get("paragraphs", [])
        h2_tags = [h.lower() for h in obs.get("h2_tags", [])]
        json_ld = obs.get("json_ld_schemas", [])
        
        findings: List[FindingItem] = []

        # 1. Source Clarity & Attribution (20%)
        # Look for author info, Organization schema, or bylines
        has_author = bool(re.search(r"\b(author|written by|by |reviewed by)\b", text))
        has_org_schema = any(isinstance(s, dict) and s.get("@type") in ("Organization", "Person", "NewsArticle", "TechArticle") for s in json_ld)
        source_clarity_score = 90 if (has_author and has_org_schema) else (70 if (has_author or has_org_schema) else 35)

        # 2. Factual Specificity & Density (20%)
        # High ratio of factual assertions, metrics, numbers, percentages
        numbers = re.findall(r"\b\d+(\.\d+)?(%|ms|s|min|kb|mb|gb|\$|€|£)?\b", text)
        factual_score = min(100, int((len(numbers) / 8) * 100))
        if factual_score < 40:
            factual_score = 40

        # 3. Answer Extractability (15%)
        # Concise independently understandable claims
        extractable_claims = [p for p in paragraphs if 20 <= len(p.split()) <= 70 and "." in p]
        extractability_score = 85 if len(extractable_claims) >= 3 else (60 if len(extractable_claims) >= 1 else 35)

        # 4. Entity Consistency (15%)
        # Defined schema types with matching entity names
        has_named_entities = bool(obs.get("title") and len(json_ld) > 0)
        entity_consistency_score = 85 if has_named_entities else 50

        # 5. Evidence Quality & References (10%)
        # Outbound links or cited sources
        links = obs.get("links", [])
        has_external_links = any(not l.get("is_internal") for l in links)
        evidence_quality_score = 80 if has_external_links else 50

        # 6. Comparative Usefulness (10%)
        # Clear tradeoffs, pros, cons, alternatives, "vs"
        has_comparison = bool(re.search(r"\b(vs|versus|compared to|pros and cons|alternatives|difference)\b", text))
        has_comp_heading = any("vs" in h or "compar" in h or "difference" in h for h in h2_tags)
        comparative_score = 90 if (has_comparison and has_comp_heading) else (70 if has_comparison else 40)

        # 7. Freshness (10%)
        # Updated/published dates or current year
        has_freshness = bool(re.search(r"\b(2025|2026|updated|published|last modified)\b", text))
        freshness_score = 90 if has_freshness else 45

        # Weighted GEO Readiness Score (Spec Section 30)
        geo_composite = (
            (source_clarity_score * 0.20) +
            (factual_score * 0.20) +
            (extractability_score * 0.15) +
            (entity_consistency_score * 0.15) +
            (evidence_quality_score * 0.10) +
            (comparative_score * 0.10) +
            (freshness_score * 0.10)
        )
        geo_composite = round(min(100.0, max(0.0, geo_composite)), 1)

        # Generate GEO Findings with strict Section 31 disclaimers
        if not (has_author or has_org_schema):
            findings.append(FindingItem(
                finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                audit_id=audit_id,
                rule_id="GEO-SOURCE-001",
                page_id=page_id,
                url=url,
                normalized_url=norm_url,
                severity=Severity.LOW,
                evidence_class=EvidenceClass.HEURISTIC,
                status="warning",
                confidence=0.80,
                evidence={
                    "author_byline": False,
                    "organization_schema": False,
                    "disclaimer": "HEURISTIC — not an official search-engine metric",
                    "model_version": settings.GEO_MODEL_VERSION
                },
                fingerprint=generate_fingerprint("GEO-SOURCE-001", norm_url, "source"),
                title="GEO Source Quality: Missing Clear Author or Organization Attribution",
                category="GEO Readiness",
                why_it_matters="Generative search systems favor content with clearly attributable origins, documented authors, or established organizational provenance.",
                remediation="Add an explicit author byline or publisher attribution, accompanied by Organization/Person Schema.org markup. Note: Google states there is no special schema required for AI Overviews, but explicit author transparency aids machine readability.",
                pros=["Strengthens transparency and source clarity", "Supports general E-E-A-T best practices"],
                cons=["Heuristic model; requires editorial workflow update"],
                validation_method="Confirm author name or organization schema is present on page."
            ))

        if comparative_score < 50:
            findings.append(FindingItem(
                finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                audit_id=audit_id,
                rule_id="GEO-COMP-001",
                page_id=page_id,
                url=url,
                normalized_url=norm_url,
                severity=Severity.INFO,
                evidence_class=EvidenceClass.HEURISTIC,
                status="warning",
                confidence=0.75,
                evidence={
                    "comparative_score": comparative_score,
                    "disclaimer": "HEURISTIC — not an official search-engine metric",
                    "model_version": settings.GEO_MODEL_VERSION
                },
                fingerprint=generate_fingerprint("GEO-COMP-001", norm_url, "comp"),
                title="GEO Opportunity: Add Comparative Analysis & Tradeoff Detail",
                category="GEO Readiness",
                why_it_matters="Generative AI search queries frequently seek comparisons (e.g. 'X vs Y', 'pros and cons of X'). Adding comparative context increases topical utility.",
                remediation="Include a section comparing this solution with common alternatives, articulating concrete tradeoffs and ideal use-cases.",
                pros=["Expands query fan-out coverage for comparative queries"],
                cons=["Must maintain objective comparison accuracy"],
                validation_method="Verify page includes an objective comparison or tradeoffs section."
            ))

        return {
            "geo_score": geo_composite,
            "components": {
                "source_clarity": source_clarity_score,
                "factual_specificity": factual_score,
                "answer_extractability": extractability_score,
                "entity_consistency": entity_consistency_score,
                "evidence_quality": evidence_quality_score,
                "comparative_utility": comparative_score,
                "freshness": freshness_score,
            },
            "methodology_version": settings.GEO_MODEL_VERSION,
        }, findings
