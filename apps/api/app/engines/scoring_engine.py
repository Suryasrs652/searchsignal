from typing import List, Dict, Any
from app.core.config import settings
from app.rules.base import FindingItem, Severity, EvidenceClass

SEVERITY_PENALTIES = {
    Severity.BLOCKER: 25.0,
    Severity.CRITICAL: 15.0,
    Severity.HIGH: 8.0,
    Severity.MEDIUM: 4.0,
    Severity.LOW: 1.0,
    Severity.INFO: 0.0,
}

class ScoringEngine:
    @staticmethod
    def calculate_scores(
        pages: List[Dict[str, Any]],
        findings: List[FindingItem],
        aeo_page_scores: List[float],
        geo_page_scores: List[float],
    ) -> List[Dict[str, Any]]:
        total_pages = max(1, len(pages))
        
        # Categorize findings
        category_findings: Dict[str, List[FindingItem]] = {
            "Technical SEO": [],
            "Crawlability": [],
            "Indexability": [],
            "Content": [],
            "Internal Linking": [],
            "Structured Data": [],
            "Performance": [],
        }

        for f in findings:
            cat = f.category
            if cat in category_findings:
                category_findings[cat].append(f)
            elif "Metadata" in cat or "Status" in cat:
                category_findings["Technical SEO"].append(f)
            else:
                category_findings["Technical SEO"].append(f)

        # Helper to compute category score with rule-capping to prevent repetitive inflation
        def score_category(category_name: str, max_deduction: float = 100.0) -> float:
            cat_list = category_findings.get(category_name, [])
            rule_counts: Dict[str, int] = {}
            for f in cat_list:
                rule_counts[f.rule_id] = rule_counts.get(f.rule_id, 0) + 1
                
            total_penalty = 0.0
            for f in cat_list:
                sev = f.severity
                base_pen = SEVERITY_PENALTIES.get(sev, 1.0)
                # Apply diminishing returns / prevalence cap for repeated rule triggers
                count = rule_counts[f.rule_id]
                # Logarithmic prevalence attenuation so 1000 duplicate titles don't drop score to -10,000
                attenuation = 1.0 / (1.0 + 0.15 * (count - 1))
                total_penalty += base_pen * attenuation

            deduction = min(max_deduction, total_penalty)
            return round(max(0.0, 100.0 - deduction), 1)

        tech_score = score_category("Technical SEO")
        crawl_score = score_category("Crawlability")
        index_score = score_category("Indexability")
        content_score = score_category("Content")
        links_score = score_category("Internal Linking")
        schema_score = score_category("Structured Data")
        
        # Performance baseline derived from observed response time & lab speed
        avg_resp_ms = sum(p.get("response_time_ms", 300) for p in pages) / total_pages
        perf_deduction = min(40.0, (avg_resp_ms / 2000.0) * 30.0)
        perf_score = round(max(40.0, 100.0 - perf_deduction), 1)

        # AEO and GEO are heuristics averaged across crawled pages
        avg_aeo = round(sum(aeo_page_scores) / max(1, len(aeo_page_scores)), 1) if aeo_page_scores else 70.0
        avg_geo = round(sum(geo_page_scores) / max(1, len(geo_page_scores)), 1) if geo_page_scores else 65.0

        # Weighted Site Health (Deterministic SEO components)
        site_health = round(
            (tech_score * 0.25) +
            (crawl_score * 0.15) +
            (index_score * 0.15) +
            (content_score * 0.15) +
            (links_score * 0.10) +
            (schema_score * 0.10) +
            (perf_score * 0.10),
            1
        )

        results = [
            {
                "dimension": "SEO Health",
                "score": site_health,
                "confidence": 0.95,
                "evidence_class": EvidenceClass.DERIVED.value,
                "methodology_version": settings.SCORING_VERSION,
                "inputs": {"pages_analyzed": total_pages, "findings_count": len(findings)},
            },
            {
                "dimension": "Technical SEO",
                "score": tech_score,
                "confidence": 1.0,
                "evidence_class": EvidenceClass.EXACT.value,
                "methodology_version": settings.SCORING_VERSION,
                "inputs": {"findings_count": len(category_findings["Technical SEO"])},
            },
            {
                "dimension": "Crawlability & Indexability",
                "score": round((crawl_score + index_score) / 2.0, 1),
                "confidence": 1.0,
                "evidence_class": EvidenceClass.EXACT.value,
                "methodology_version": settings.SCORING_VERSION,
                "inputs": {"crawl_score": crawl_score, "index_score": index_score},
            },
            {
                "dimension": "Content Quality",
                "score": content_score,
                "confidence": 0.95,
                "evidence_class": EvidenceClass.EXACT.value,
                "methodology_version": settings.SCORING_VERSION,
                "inputs": {"findings_count": len(category_findings["Content"])},
            },
            {
                "dimension": "Internal Linking",
                "score": links_score,
                "confidence": 0.95,
                "evidence_class": EvidenceClass.DERIVED.value,
                "methodology_version": settings.SCORING_VERSION,
                "inputs": {"findings_count": len(category_findings["Internal Linking"])},
            },
            {
                "dimension": "Structured Data",
                "score": schema_score,
                "confidence": 0.90,
                "evidence_class": EvidenceClass.VALIDATED.value,
                "methodology_version": settings.SCORING_VERSION,
                "inputs": {"findings_count": len(category_findings["Structured Data"])},
            },
            {
                "dimension": "Performance",
                "score": perf_score,
                "confidence": 0.85,
                "evidence_class": EvidenceClass.OBSERVED.value,
                "methodology_version": settings.SCORING_VERSION,
                "inputs": {"avg_response_ms": avg_resp_ms},
            },
            {
                "dimension": "AEO Readiness",
                "score": avg_aeo,
                "confidence": 0.80,
                "evidence_class": EvidenceClass.HEURISTIC.value,
                "methodology_version": settings.AEO_MODEL_VERSION,
                "inputs": {"disclaimer": "HEURISTIC — not an official search-engine metric"},
            },
            {
                "dimension": "GEO Readiness",
                "score": avg_geo,
                "confidence": 0.80,
                "evidence_class": EvidenceClass.HEURISTIC.value,
                "methodology_version": settings.GEO_MODEL_VERSION,
                "inputs": {"disclaimer": "HEURISTIC — not an official search-engine metric"},
            },
        ]
        return results
