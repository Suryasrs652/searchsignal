import uuid
import csv
import io
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Organization, Project, Audit, Page, PageObservation, Finding, Score, Recommendation, User
from app.crawler.audit_manager import AuditManager
from app.storage.evidence_store import evidence_store
from app.core.config import settings

router = APIRouter()

def api_response(data: Any = None, errors: Optional[List[Dict[str, Any]]] = None, status_code: int = 200):
    return {
        "data": data,
        "meta": {
            "request_id": f"req_{uuid.uuid4().hex[:8]}",
            "api_version": "v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "errors": errors or [],
    }

# ----------------- AUTH (Demo / Local Mode) -----------------
class LoginRequest(BaseModel):
    email: str = "admin@searchsignal.ai"
    password: str = "admin"

@router.post("/auth/login")
async def login(req: LoginRequest):
    return api_response({
        "access_token": f"mock_jwt_token_{uuid.uuid4().hex}",
        "token_type": "bearer",
        "user": {
            "email": req.email,
            "name": "Admin User",
            "role": "owner"
        }
    })

@router.get("/auth/me")
async def me():
    return api_response({
        "email": "admin@searchsignal.ai",
        "name": "Admin User",
        "role": "owner",
        "permissions": [
            "project.read", "project.write", "audit.run", "audit.cancel",
            "finding.write", "report.export", "organization.manage"
        ]
    })

# ----------------- ORGANIZATIONS -----------------
class OrgCreate(BaseModel):
    name: str = "Default Agency"
    slug: str = "default-agency"

@router.get("/organizations")
async def list_orgs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization))
    orgs = result.scalars().all()
    if not orgs:
        # Seed default org if empty
        default_org = Organization(id=str(uuid.uuid4()), name="Demo Organization", slug="demo-org")
        db.add(default_org)
        await db.commit()
        await db.refresh(default_org)
        orgs = [default_org]
    return api_response([{"id": o.id, "name": o.name, "slug": o.slug} for o in orgs])

# ----------------- PROJECTS -----------------
class ProjectCreate(BaseModel):
    organization_id: Optional[str] = None
    name: str
    root_url: str
    crawl_config: Dict[str, Any] = Field(default_factory=dict)

@router.get("/projects")
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).order_by(desc(Project.created_at)))
    projects = result.scalars().all()
    return api_response([{
        "id": p.id,
        "organization_id": p.organization_id,
        "name": p.name,
        "root_url": p.root_url,
        "status": p.status,
        "crawl_config": p.crawl_config,
        "created_at": p.created_at.isoformat(),
    } for p in projects])

@router.post("/projects")
async def create_project(req: ProjectCreate, db: AsyncSession = Depends(get_db)):
    org_id = req.organization_id
    if not org_id:
        org_res = await db.execute(select(Organization))
        first_org = org_res.scalars().first()
        if not first_org:
            first_org = Organization(id=str(uuid.uuid4()), name="Demo Organization", slug="demo-org")
            db.add(first_org)
            await db.commit()
            await db.refresh(first_org)
        org_id = first_org.id

    project = Project(
        name=req.name,
        root_url=req.root_url,
        organization_id=org_id,
        crawl_config=req.crawl_config,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return api_response({
        "id": project.id,
        "organization_id": project.organization_id,
        "name": project.name,
        "root_url": project.root_url,
        "status": project.status,
        "crawl_config": project.crawl_config,
        "created_at": project.created_at.isoformat(),
    })

# ----------------- AUDITS -----------------
class AuditLaunchRequest(BaseModel):
    crawl_mode: str = "quick" # quick, standard, deep
    max_urls: Optional[int] = 50
    respect_robots: Optional[bool] = True

@router.post("/projects/{project_id}/audits")
async def launch_audit(
    project_id: str,
    req: AuditLaunchRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    proj = (await db.execute(select(Project).where(Project.id == project_id))).scalars().first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    audit = Audit(
        id=str(uuid.uuid4()),
        project_id=project_id,
        status="queued",
        crawl_mode=req.crawl_mode,
        engine_version=settings.CRAWLER_VERSION,
        config={
            "max_urls": req.max_urls or 50,
            "respect_robots": req.respect_robots if req.respect_robots is not None else True,
            "allow_local_test": settings.ALLOW_LOCAL_TEST_HOSTS,
        }
    )
    db.add(audit)
    await db.commit()
    await db.refresh(audit)

    # Launch background audit runner
    background_tasks.add_task(
        AuditManager.run_audit,
        audit_id=audit.id,
        root_url=proj.root_url,
        crawl_mode=audit.crawl_mode,
        crawl_config=audit.config
    )

    return api_response({
        "audit_id": audit.id,
        "project_id": audit.project_id,
        "status": audit.status,
        "crawl_mode": audit.crawl_mode,
        "engine_version": audit.engine_version,
    })

@router.get("/projects/{project_id}/audits")
async def list_project_audits(project_id: str, db: AsyncSession = Depends(get_db)):
    audits = (await db.execute(
        select(Audit).where(Audit.project_id == project_id).order_by(desc(Audit.started_at))
    )).scalars().all()
    return api_response([{
        "id": a.id,
        "project_id": a.project_id,
        "status": a.status,
        "crawl_mode": a.crawl_mode,
        "started_at": a.started_at.isoformat() if a.started_at else None,
        "completed_at": a.completed_at.isoformat() if a.completed_at else None,
        "progress_pages": a.progress_pages,
        "engine_version": a.engine_version,
    } for a in audits])

@router.get("/audits/{audit_id}")
async def get_audit(audit_id: str, db: AsyncSession = Depends(get_db)):
    audit = (await db.execute(select(Audit).where(Audit.id == audit_id))).scalars().first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    proj = (await db.execute(select(Project).where(Project.id == audit.project_id))).scalars().first()

    return api_response({
        "id": audit.id,
        "project_id": audit.project_id,
        "project_name": proj.name if proj else "",
        "root_url": proj.root_url if proj else "",
        "status": audit.status,
        "crawl_mode": audit.crawl_mode,
        "started_at": audit.started_at.isoformat() if audit.started_at else None,
        "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
        "progress_pages": audit.progress_pages,
        "engine_version": audit.engine_version,
        "config": audit.config,
    })

# ----------------- SCORES -----------------
@router.get("/audits/{audit_id}/scores")
async def get_audit_scores(audit_id: str, db: AsyncSession = Depends(get_db)):
    scores = (await db.execute(select(Score).where(Score.audit_id == audit_id))).scalars().all()
    return api_response([{
        "dimension": s.dimension,
        "score": s.score,
        "confidence": s.confidence,
        "evidence_class": s.evidence_class,
        "methodology_version": s.methodology_version,
        "inputs": s.inputs,
    } for s in scores])

# ----------------- FINDINGS & EVIDENCE VIEWER -----------------
@router.get("/audits/{audit_id}/findings")
async def get_audit_findings(
    audit_id: str,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    evidence_class: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Finding).where(Finding.audit_id == audit_id)
    if severity:
        query = query.where(Finding.severity == severity.lower())
    if evidence_class:
        query = query.where(Finding.evidence_class == evidence_class.upper())
    
    findings = (await db.execute(query)).scalars().all()

    # Join page URLs if available
    page_ids = [f.page_id for f in findings if f.page_id]
    pages_map = {}
    if page_ids:
        pages = (await db.execute(select(Page).where(Page.id.in_(page_ids)))).scalars().all()
        pages_map = {p.id: p.url for p in pages}

    return api_response([{
        "id": f.id,
        "rule_id": f.rule_id,
        "url": pages_map.get(f.page_id, "sitewide"),
        "severity": f.severity,
        "evidence_class": f.evidence_class,
        "status": f.status,
        "confidence": f.confidence,
        "fingerprint": f.fingerprint,
        "evidence": f.evidence,
        "created_at": f.created_at.isoformat(),
    } for f in findings])

@router.get("/audits/{audit_id}/findings/{finding_id}")
async def get_finding_detail(audit_id: str, finding_id: str, db: AsyncSession = Depends(get_db)):
    f = (await db.execute(
        select(Finding).where(Finding.audit_id == audit_id, Finding.id == finding_id)
    )).scalars().first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")

    page_url = "sitewide"
    headers = None
    html_snapshot_snippet = None

    if f.page_id:
        p = (await db.execute(select(Page).where(Page.id == f.page_id))).scalars().first()
        if p:
            page_url = p.url
            headers = evidence_store.get_headers(audit_id, p.normalized_url)
            snapshot = evidence_store.get_snapshot(audit_id, p.normalized_url)
            if snapshot:
                html_snapshot_snippet = snapshot[:4000]

    return api_response({
        "finding_id": f.id,
        "rule_id": f.rule_id,
        "url": page_url,
        "severity": f.severity,
        "evidence_class": f.evidence_class,
        "status": f.status,
        "confidence": f.confidence,
        "evidence": f.evidence,
        "fingerprint": f.fingerprint,
        "headers": headers,
        "html_snapshot": html_snapshot_snippet,
        "observed_at": f.created_at.isoformat(),
    })

# ----------------- PAGES -----------------
@router.get("/audits/{audit_id}/pages")
async def get_audit_pages(audit_id: str, db: AsyncSession = Depends(get_db)):
    pages = (await db.execute(select(Page).where(Page.audit_id == audit_id))).scalars().all()
    observations = (await db.execute(
        select(PageObservation).where(PageObservation.page_id.in_([p.id for p in pages]))
    )).scalars().all()
    obs_map = {o.page_id: o for o in observations}

    return api_response([{
        "id": p.id,
        "url": p.url,
        "normalized_url": p.normalized_url,
        "depth": p.depth,
        "http_status": obs_map[p.id].http_status if p.id in obs_map else None,
        "title": obs_map[p.id].title if p.id in obs_map else "",
        "word_count": obs_map[p.id].word_count if p.id in obs_map else 0,
        "response_time_ms": obs_map[p.id].response_time_ms if p.id in obs_map else 0,
    } for p in pages])

# ----------------- RECOMMENDATIONS (ROADMAP) -----------------
@router.get("/audits/{audit_id}/recommendations")
async def get_recommendations(audit_id: str, db: AsyncSession = Depends(get_db)):
    recs = (await db.execute(
        select(Recommendation).where(Recommendation.audit_id == audit_id).order_by(desc(Recommendation.opportunity_score))
    )).scalars().all()

    return api_response([{
        "id": r.id,
        "title": r.title,
        "description": r.description,
        "category": r.category,
        "priority_group": r.priority_group,
        "priority": r.priority,
        "opportunity_score": r.opportunity_score,
        "estimated_effort": r.estimated_effort,
        "pros": r.pros,
        "cons": r.cons,
        "validation_method": r.validation_method,
        "evidence": r.evidence,
    } for r in recs])

# ----------------- AUDIT COMPARISON (DIFF MODE) -----------------
@router.get("/audits/{audit_id}/compare/{other_audit_id}")
async def compare_audits_endpoint(audit_id: str, other_audit_id: str):
    diff = await AuditManager.compare_audits(audit_id, other_audit_id)
    return api_response(diff)

# ----------------- REPORT EXPORT (JSON & CSV) -----------------
@router.get("/audits/{audit_id}/report/json")
async def export_json_report(audit_id: str, db: AsyncSession = Depends(get_db)):
    scores = (await db.execute(select(Score).where(Score.audit_id == audit_id))).scalars().all()
    findings = (await db.execute(select(Finding).where(Finding.audit_id == audit_id))).scalars().all()
    recs = (await db.execute(select(Recommendation).where(Recommendation.audit_id == audit_id))).scalars().all()
    audit = (await db.execute(select(Audit).where(Audit.id == audit_id))).scalars().first()

    report_payload = {
        "report_type": "SearchSignal Audit Report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audit": {
            "id": audit.id if audit else audit_id,
            "engine_version": audit.engine_version if audit else settings.CRAWLER_VERSION,
            "started_at": audit.started_at.isoformat() if audit and audit.started_at else None,
            "completed_at": audit.completed_at.isoformat() if audit and audit.completed_at else None,
        },
        "scores": [{s.dimension: {"score": s.score, "classification": s.evidence_class}} for s in scores],
        "findings_summary": {
            "total": len(findings),
            "by_evidence_class": {
                ec: len([f for f in findings if f.evidence_class == ec])
                for ec in ["EXACT", "DERIVED", "VALIDATED", "OBSERVED", "HEURISTIC"]
            }
        },
        "recommendations": [
            {"title": r.title, "priority_group": r.priority_group, "opportunity_score": r.opportunity_score}
            for r in recs
        ]
    }
    return api_response(report_payload)

@router.get("/audits/{audit_id}/report/csv")
async def export_csv_report(audit_id: str, db: AsyncSession = Depends(get_db)):
    findings = (await db.execute(select(Finding).where(Finding.audit_id == audit_id))).scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Finding ID", "Rule ID", "Severity", "Evidence Class", "Confidence", "Evidence Details"])
    for f in findings:
        writer.writerow([
            f.id,
            f.rule_id,
            f.severity,
            f.evidence_class,
            f.confidence,
            str(f.evidence)
        ])
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=searchsignal_audit_{audit_id[:8]}.csv"}
    )
