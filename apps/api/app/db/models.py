import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Index, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)

def gen_uuid():
    return str(uuid.uuid4())

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(Text, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    memberships = relationship("Membership", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    
    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")

class Membership(Base):
    __tablename__ = "memberships"
    
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(50), nullable=False, default="admin") # owner, admin, seo_manager, analyst, developer, client
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    
    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", back_populates="memberships")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    root_url = Column(Text, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    crawl_config = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    
    organization = relationship("Organization", back_populates="projects")
    audits = relationship("Audit", back_populates="project", cascade="all, delete-orphan")

class Audit(Base):
    __tablename__ = "audits"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="queued", nullable=False) # queued, discovering, crawling, validating, scoring, completed, failed, cancelled
    crawl_mode = Column(String(50), default="quick", nullable=False) # quick, standard, deep
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    config = Column(JSON, default=dict, nullable=False)
    engine_version = Column(Text, default="4.2.0", nullable=False)
    progress_pages = Column(Integer, default=0)
    
    project = relationship("Project", back_populates="audits")
    pages = relationship("Page", back_populates="audit", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="audit", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="audit", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="audit", cascade="all, delete-orphan")
    links = relationship("Link", back_populates="audit", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(String(36), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    url = Column(Text, nullable=False)
    normalized_url = Column(Text, nullable=False)
    depth = Column(Integer, default=0)
    discovered_from = Column(Integer, nullable=True)
    
    __table_args__ = (
        UniqueConstraint("audit_id", "normalized_url", name="uq_audit_page_url"),
        Index("idx_pages_audit_url", "audit_id", "normalized_url"),
    )
    
    audit = relationship("Audit", back_populates="pages")
    observation = relationship("PageObservation", back_populates="page", uselist=False, cascade="all, delete-orphan")
    outbound_links = relationship("Link", back_populates="source_page", cascade="all, delete-orphan")

class PageObservation(Base):
    __tablename__ = "page_observations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, unique=True)
    http_status = Column(Integer, nullable=True)
    content_type = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    meta_description = Column(Text, nullable=True)
    canonical_url = Column(Text, nullable=True)
    robots = Column(Text, nullable=True)
    lang = Column(String(50), nullable=True)
    word_count = Column(Integer, default=0)
    response_time_ms = Column(Integer, default=0)
    ttfb_ms = Column(Integer, default=0)
    html_hash = Column(String(64), nullable=True)
    rendered_hash = Column(String(64), nullable=True)
    observation = Column(JSON, default=dict, nullable=False)
    
    page = relationship("Page", back_populates="observation")

class Link(Base):
    __tablename__ = "links"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(String(36), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    source_page_id = Column(Integer, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    target_url = Column(Text, nullable=False)
    normalized_target_url = Column(Text, nullable=True)
    anchor_text = Column(Text, nullable=True)
    is_internal = Column(Boolean, default=True)
    rel = Column(String(100), nullable=True)
    
    __table_args__ = (
        Index("idx_links_audit_target", "audit_id", "normalized_target_url"),
    )
    
    audit = relationship("Audit", back_populates="links")
    source_page = relationship("Page", back_populates="outbound_links")

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    audit_id = Column(String(36), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(String(100), nullable=False)
    page_id = Column(Integer, ForeignKey("pages.id", ondelete="SET NULL"), nullable=True)
    severity = Column(String(50), nullable=False) # blocker, critical, high, medium, low, info
    evidence_class = Column(String(50), nullable=False) # EXACT, DERIVED, VALIDATED, OBSERVED, HEURISTIC, PREDICTIVE, UNKNOWN
    status = Column(String(50), default="failed", nullable=False) # failed, passed, warning
    confidence = Column(Float, default=1.0, nullable=False)
    evidence = Column(JSON, default=dict, nullable=False)
    fingerprint = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_findings_audit_rule", "audit_id", "rule_id"),
        Index("idx_findings_severity", "audit_id", "severity"),
        Index("idx_findings_fingerprint", "audit_id", "fingerprint"),
    )
    
    audit = relationship("Audit", back_populates="findings")

class Score(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(String(36), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    dimension = Column(String(100), nullable=False) # Technical SEO, Content, Performance, Structured Data, AEO Readiness, GEO Readiness, Overall Health
    score = Column(Float, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    evidence_class = Column(String(50), default="DERIVED", nullable=False)
    methodology_version = Column(String(50), nullable=False)
    inputs = Column(JSON, default=dict, nullable=False)
    
    __table_args__ = (
        UniqueConstraint("audit_id", "dimension", name="uq_audit_score_dimension"),
    )
    
    audit = relationship("Audit", back_populates="scores")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    audit_id = Column(String(36), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    priority_group = Column(String(50), default="now", nullable=False) # now, next, later, experiments
    priority = Column(Integer, default=1, nullable=False)
    opportunity_score = Column(Float, default=50.0, nullable=False)
    estimated_effort = Column(String(50), default="Medium")
    pros = Column(JSON, default=list, nullable=True)
    cons = Column(JSON, default=list, nullable=True)
    validation_method = Column(Text, nullable=True)
    evidence = Column(JSON, default=dict, nullable=True)
    
    audit = relationship("Audit", back_populates="recommendations")
