import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
from app.core.config import settings

class EvidenceStore:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.STORAGE_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_audit_dir(self, audit_id: str) -> Path:
        audit_dir = self.base_dir / audit_id
        audit_dir.mkdir(parents=True, exist_ok=True)
        return audit_dir

    def _url_hash(self, normalized_url: str) -> str:
        return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()[:16]

    def save_snapshot(
        self,
        audit_id: str,
        normalized_url: str,
        html_content: str,
        headers: Dict[str, str],
        meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Stores immutable raw HTML snapshot and HTTP headers."""
        audit_dir = self._get_audit_dir(audit_id)
        u_hash = self._url_hash(normalized_url)
        
        snapshot_path = audit_dir / f"{u_hash}.html"
        snapshot_path.write_text(html_content or "", encoding="utf-8", errors="replace")
        
        headers_path = audit_dir / f"{u_hash}_headers.json"
        headers_payload = {
            "url": normalized_url,
            "headers": headers,
            "meta": meta or {},
        }
        headers_path.write_text(json.dumps(headers_payload, indent=2), encoding="utf-8")
        
        return str(snapshot_path)

    def get_snapshot(self, audit_id: str, normalized_url: str) -> Optional[str]:
        audit_dir = self._get_audit_dir(audit_id)
        u_hash = self._url_hash(normalized_url)
        snapshot_path = audit_dir / f"{u_hash}.html"
        if snapshot_path.exists():
            return snapshot_path.read_text(encoding="utf-8", errors="replace")
        return None

    def get_headers(self, audit_id: str, normalized_url: str) -> Optional[Dict[str, Any]]:
        audit_dir = self._get_audit_dir(audit_id)
        u_hash = self._url_hash(normalized_url)
        headers_path = audit_dir / f"{u_hash}_headers.json"
        if headers_path.exists():
            try:
                return json.loads(headers_path.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

evidence_store = EvidenceStore()
