import uuid
from typing import List, Dict, Any
from app.rules.base import FindingItem, Severity

class GrowthEngine:
    @staticmethod
    def generate_recommendations(findings: List[FindingItem], total_pages: int) -> List[Dict[str, Any]]:
        # Group findings by rule_id to aggregate reach and compute opportunity
        grouped: Dict[str, List[FindingItem]] = {}
        for f in findings:
            grouped.setdefault(f.rule_id, []).append(f)

        recommendations: List[Dict[str, Any]] = []

        for rule_id, items in grouped.items():
            first = items[0]
            affected_count = len(items)
            reach_ratio = min(1.0, affected_count / max(1, total_pages))
            reach = max(20.0, reach_ratio * 100.0)

            # Impact based on severity
            if first.severity == Severity.BLOCKER:
                impact = 95.0
                effort = 20.0
                strategic = 90.0
                group = "now"
                effort_label = "Low"
            elif first.severity == Severity.CRITICAL:
                impact = 85.0
                effort = 25.0
                strategic = 85.0
                group = "now"
                effort_label = "Low to Medium"
            elif first.severity == Severity.HIGH:
                impact = 70.0
                effort = 35.0
                strategic = 75.0
                group = "next"
                effort_label = "Medium"
            elif first.severity == Severity.MEDIUM:
                impact = 50.0
                effort = 40.0
                strategic = 60.0
                group = "later"
                effort_label = "Medium"
            elif "AEO" in rule_id or "GEO" in rule_id:
                impact = 55.0
                effort = 50.0
                strategic = 65.0
                group = "experiments"
                effort_label = "Medium"
            else:
                impact = 30.0
                effort = 30.0
                strategic = 40.0
                group = "later"
                effort_label = "Low"

            confidence = first.confidence * 100.0

            # Opportunity formula (Section 39):
            # Raw = (Impact * Reach * Confidence * Strategic) / (Effort * 1000)
            raw_opportunity = (impact * reach * (confidence / 100.0) * strategic) / (effort * 10.0)
            opportunity_score = round(min(99.0, max(15.0, raw_opportunity / 10.0)), 1)

            rec = {
                "id": f"REC-{uuid.uuid4().hex[:6].upper()}",
                "title": f"Resolve {first.title} ({affected_count} URLs affected)",
                "description": first.why_it_matters + " " + first.remediation,
                "category": first.category,
                "priority_group": group,
                "priority": int(100 - opportunity_score),
                "opportunity_score": opportunity_score,
                "estimated_effort": effort_label,
                "pros": first.pros,
                "cons": first.cons,
                "validation_method": first.validation_method,
                "evidence": {
                    "rule_id": rule_id,
                    "affected_urls_count": affected_count,
                    "sample_urls": [item.url for item in items[:5]],
                    "evidence_class": first.evidence_class.value,
                    "severity": first.severity.value,
                    "confidence": first.confidence,
                }
            }
            recommendations.append(rec)

        # Sort recommendations by opportunity score descending
        recommendations.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return recommendations
