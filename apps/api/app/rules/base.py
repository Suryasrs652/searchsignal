import hashlib
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class EvidenceClass(str, Enum):
    EXACT = "EXACT"
    DERIVED = "DERIVED"
    VALIDATED = "VALIDATED"
    OBSERVED = "OBSERVED"
    HEURISTIC = "HEURISTIC"
    PREDICTIVE = "PREDICTIVE"
    UNKNOWN = "UNKNOWN"

class Severity(str, Enum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class FindingItem(BaseModel):
    finding_id: str
    audit_id: str
    rule_id: str
    page_id: Optional[int] = None
    url: str
    normalized_url: str
    severity: Severity
    evidence_class: EvidenceClass
    status: str = "failed"
    confidence: float = 1.0
    evidence: Dict[str, Any] = Field(default_factory=dict)
    fingerprint: str
    title: str
    category: str
    why_it_matters: str
    remediation: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    validation_method: str = ""

def generate_fingerprint(rule_id: str, normalized_url: str, evidence_key: str = "") -> str:
    payload = f"{rule_id}:{normalized_url}:{evidence_key}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
