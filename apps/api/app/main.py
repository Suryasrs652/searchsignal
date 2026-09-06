from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import init_db, AsyncSessionLocal
from app.db.models import Organization, Project
from app.api.v1.routes import router as api_v1_router
from sqlalchemy import select
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schemas on startup
    await init_db()
    
    # Seed initial demo data if database is fresh
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Organization))
        if not res.scalars().first():
            org = Organization(id=str(uuid.uuid4()), name="Acme Growth Agency", slug="acme-agency")
            db.add(org)
            await db.flush()

            proj = Project(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                name="Example Store & Blog",
                root_url="https://example.com",
                crawl_config={"max_urls": 50, "respect_robots": True},
            )
            db.add(proj)
            await db.commit()

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-site SEO, GEO, and AEO Intelligence & Growth Platform. Never present a heuristic as an observed fact.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "status": "online",
        "crawler_version": settings.CRAWLER_VERSION,
        "rule_pack_version": settings.RULE_PACK_VERSION,
        "scoring_version": settings.SCORING_VERSION,
        "geo_model_version": settings.GEO_MODEL_VERSION,
        "aeo_model_version": settings.AEO_MODEL_VERSION,
        "docs_url": "/docs",
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
