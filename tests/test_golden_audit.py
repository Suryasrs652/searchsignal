import pytest
import uvicorn
import asyncio
import uuid
from app.crawler.audit_manager import AuditManager
from app.db.session import init_db, AsyncSessionLocal
from app.db.models import Audit, Project, Organization, Finding, Score, Recommendation
from tests.fixtures.synthetic_site import synthetic_app
from sqlalchemy import select

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_synthetic_site_golden_audit():
    await init_db()

    # Launch in-process synthetic test server on port 8089
    config = uvicorn.Config(synthetic_app, host="127.0.0.1", port=8089, log_level="error")
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())
    await asyncio.sleep(0.5)  # Wait for server to start

    try:
        # Create Project in DB
        async with AsyncSessionLocal() as db:
            unique_slug = f"golden-org-{uuid.uuid4().hex[:6]}"
            org = Organization(id=str(uuid.uuid4()), name="Golden Org", slug=unique_slug)
            db.add(org)
            await db.flush()

            proj = Project(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                name="Golden Benchmark Test",
                root_url="http://127.0.0.1:8089",
            )
            db.add(proj)

            audit_1_id = str(uuid.uuid4())
            audit_1 = Audit(
                id=audit_1_id,
                project_id=proj.id,
                status="queued",
                crawl_mode="quick",
                config={"max_urls": 30, "max_depth": 3, "respect_robots": True, "allow_local_test": True}
            )
            db.add(audit_1)
            await db.commit()

        # Run first audit
        await AuditManager.run_audit(
            audit_id=audit_1_id,
            root_url="http://127.0.0.1:8089",
            crawl_mode="quick",
            crawl_config={"max_urls": 30, "max_depth": 3, "respect_robots": True, "allow_local_test": True}
        )

        # Verify findings in DB
        async with AsyncSessionLocal() as db:
            audit = (await db.execute(select(Audit).where(Audit.id == audit_1_id))).scalars().first()
            assert audit.status == "completed"
            assert audit.progress_pages >= 10

            findings = (await db.execute(select(Finding).where(Finding.audit_id == audit_1_id))).scalars().all()
            scores = (await db.execute(select(Score).where(Score.audit_id == audit_1_id))).scalars().all()
            recs = (await db.execute(select(Recommendation).where(Recommendation.audit_id == audit_1_id))).scalars().all()

        # Golden assertions
        rule_ids = {f.rule_id for f in findings}
        evidence_classes = {f.evidence_class for f in findings}

        # 1. EXACT findings (404 error, missing title)
        assert "SEO-HTTP-001" in rule_ids, f"Should detect 404 broken page. Got: {rule_ids}"
        assert "SEO-TITLE-001" in rule_ids, f"Should detect missing title tag. Got: {rule_ids}"
        assert "EXACT" in evidence_classes

        # 2. DERIVED findings (duplicate titles across pages)
        assert "SEO-TITLE-002" in rule_ids, f"Should detect duplicate titles derived across pages. Got: {rule_ids}"
        assert "DERIVED" in evidence_classes

        # 3. VALIDATED findings (Schema.org price truthfulness or syntax)
        assert "SEO-SCHEMA-003" in rule_ids or "SEO-SCHEMA-002" in rule_ids, f"Should detect schema validation error. Got: {rule_ids}"
        assert "VALIDATED" in evidence_classes

        # 4. HEURISTIC findings & scores
        score_dims = {s.dimension: s for s in scores}
        assert "SEO Health" in score_dims
        assert "AEO Readiness" in score_dims
        assert "GEO Readiness" in score_dims
        assert score_dims["AEO Readiness"].evidence_class == "HEURISTIC"
        assert score_dims["GEO Readiness"].evidence_class == "HEURISTIC"

        # 5. Opportunity Roadmap
        assert len(recs) > 0
        now_recs = [r for r in recs if r.priority_group == "now"]
        assert len(now_recs) > 0, "Should have critical/blocker recommendations in 'now' group"

        # Run Audit Comparison test (Spec Section 60)
        async with AsyncSessionLocal() as db:
            audit_2_id = str(uuid.uuid4())
            audit_2 = Audit(
                id=audit_2_id,
                project_id=proj.id,
                status="queued",
                crawl_mode="quick",
                config={"max_urls": 30, "max_depth": 3, "respect_robots": True, "allow_local_test": True}
            )
            db.add(audit_2)
            await db.commit()

        await AuditManager.run_audit(
            audit_id=audit_2_id,
            root_url="http://127.0.0.1:8089",
            crawl_mode="quick",
            crawl_config={"max_urls": 30, "max_depth": 3, "respect_robots": True, "allow_local_test": True}
        )

        comparison = await AuditManager.compare_audits(audit_1_id, audit_2_id)
        assert "persisting_issues_count" in comparison
        assert comparison["persisting_issues_count"] > 0
        assert comparison["score_deltas"]["SEO Health"]["delta"] == 0.0, "Reproducible score verification"

    finally:
        server.should_exit = True
        await asyncio.sleep(0.3)
