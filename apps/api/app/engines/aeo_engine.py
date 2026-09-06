import uuid
import re
from typing import Dict, Any, List, Tuple
from app.core.config import settings
from app.rules.base import FindingItem, EvidenceClass, Severity, generate_fingerprint

QUESTION_PATTERNS = [
    (r"\bwhat is\b", "What is X?"),
    (r"\bhow (does|to|can)\b", "How does X work / How to?"),
    (r"\bhow much|cost|pricing|price\b", "How much does X cost?"),
    (r"\bwho (is|for)\b", "Who is X for?"),
    (r"\brequirements?|prerequisites?\b", "What are the requirements?"),
    (r"\bdifference between|vs|versus\b", "How is X different from Y?"),
    (r"\badvantages?|benefits?|pros\b", "What are the advantages?"),
    (r"\blimitations?|cons|drawbacks\b", "What are the limitations?"),
]

class AEOEngine:
    @staticmethod
    def evaluate_page(page: Dict[str, Any], audit_id: str) -> Tuple[Dict[str, Any], List[FindingItem]]:
        obs = page.get("observation") or {}
        url = page["url"]
        norm_url = page["normalized_url"]
        page_id = page.get("id")
        
        text = obs.get("visible_text_snippet", "").lower()
        paragraphs = obs.get("paragraphs", [])
        h2_tags = [h.lower() for h in obs.get("h2_tags", [])]
        h3_tags = [h.lower() for h in obs.get("h3_tags", [])]
        all_headings = h2_tags + h3_tags
        
        findings: List[FindingItem] = []
        
        # 1. Question Coverage (20%)
        matched_questions = []
        for pat, label in QUESTION_PATTERNS:
            found_in_heading = any(re.search(pat, h) for h in all_headings)
            found_in_text = bool(re.search(pat, text))
            if found_in_heading or found_in_text:
                matched_questions.append({
                    "pattern": label,
                    "location": "heading" if found_in_heading else "body"
                })
        question_coverage_score = min(100, int((len(matched_questions) / 5) * 100))
        
        # 2. Answer Explicitness & Extractability (20%)
        # Look for concise answer candidate passages (15-90 words) following question-like text
        candidate_answers = []
        for p in paragraphs:
            words = p.split()
            if 15 <= len(words) <= 90:
                if any(k in p.lower() for k in ["is a", "is an", "provides", "costs", "allows", "designed for", "built to"]):
                    candidate_answers.append(p)
                    
        answer_explicitness_score = 85 if len(candidate_answers) >= 2 else (60 if len(candidate_answers) == 1 else 30)
        
        # 3. Structural Clarity (15%)
        # Headings, lists, structured sections
        has_headings = len(obs.get("h2_tags", [])) >= 2
        has_paragraphs = len(paragraphs) >= 3
        structural_clarity_score = 90 if (has_headings and has_paragraphs) else (60 if has_headings else 40)
        
        # 4. Factual & Entity Completeness (15%)
        has_pricing = bool(re.search(r"(\$|€|£|\bprice\b|\bcost\b|\bfree\b|\bmonth\b)", text))
        has_specs = bool(re.search(r"\b(features|specifications|requirements|compatible|version)\b", text))
        entity_score = 85 if (has_pricing and has_specs) else (60 if (has_pricing or has_specs) else 40)
        
        # 5. Evidence / Reference Quality (10%)
        # Links, data points, citations
        has_data_points = bool(re.search(r"\b\d+(\.\d+)?%\b|\b\d{4}\b", text))
        evidence_quality_score = 80 if has_data_points else 50
        
        # 6. Snippet-Ready Passages (10%)
        snippet_ready_score = 90 if len(candidate_answers) >= 1 else 40
        
        # 7. Technical Accessibility (10%)
        tech_score = 95 if page.get("http_status") == 200 and page.get("word_count", 0) > 150 else 30
        
        # Weighted Composite AEO Score (Spec Section 26)
        aeo_composite = (
            (question_coverage_score * 0.20) +
            (answer_explicitness_score * 0.20) +
            (structural_clarity_score * 0.15) +
            (entity_score * 0.15) +
            (evidence_quality_score * 0.10) +
            (snippet_ready_score * 0.10) +
            (tech_score * 0.10)
        )
        aeo_composite = round(min(100.0, max(0.0, aeo_composite)), 1)
        
        # Generate informative AEO heuristic finding if low score
        if aeo_composite < 60:
            findings.append(FindingItem(
                finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                audit_id=audit_id,
                rule_id="AEO-READINESS-001",
                page_id=page_id,
                url=url,
                normalized_url=norm_url,
                severity=Severity.MEDIUM,
                evidence_class=EvidenceClass.HEURISTIC,
                status="failed",
                confidence=0.85,
                evidence={
                    "aeo_score": aeo_composite,
                    "matched_questions": len(matched_questions),
                    "candidate_answers": len(candidate_answers),
                    "disclaimer": "HEURISTIC — not an official search-engine metric",
                    "model_version": settings.AEO_MODEL_VERSION
                },
                fingerprint=generate_fingerprint("AEO-READINESS-001", norm_url, str(int(aeo_composite))),
                title="Low AEO Answer Extractability Readiness",
                category="AEO Readiness",
                why_it_matters="AI assistants and answer engines look for direct, concise answers to specific user questions. This page currently lacks explicit Q&A structure or extractable summary passages.",
                remediation="Add clear question-formatted subheadings (e.g. 'How does X work?') followed immediately by a concise 40-70 word definitive answer passage. Note: this is a heuristic recommendation and does not guarantee AI citation.",
                pros=["Significantly improves direct answer extractability", "Enhances user skim-readability"],
                cons=["Heuristic model; requires editorial formatting adjustments"],
                validation_method="Re-evaluate page to ensure at least 2 clear question headings with immediate answers."
            ))
        elif candidate_answers:
            findings.append(FindingItem(
                finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                audit_id=audit_id,
                rule_id="AEO-PASSAGE-001",
                page_id=page_id,
                url=url,
                normalized_url=norm_url,
                severity=Severity.INFO,
                evidence_class=EvidenceClass.HEURISTIC,
                status="passed",
                confidence=0.90,
                evidence={
                    "candidate_sample": candidate_answers[0][:160] + "...",
                    "disclaimer": "HEURISTIC — not an official search-engine metric",
                    "model_version": settings.AEO_MODEL_VERSION
                },
                fingerprint=generate_fingerprint("AEO-PASSAGE-001", norm_url, "candidate"),
                title="Strong AEO Answer Candidate Passage Detected",
                category="AEO Readiness",
                why_it_matters="Identified a concise, snippet-ready passage that directly defines or explains key concepts.",
                remediation="Keep this passage clear, accurate, and up to date.",
                pros=["High answerability readiness"],
                cons=[],
                validation_method="Periodic review of answer passage accuracy."
            ))

        return {
            "aeo_score": aeo_composite,
            "components": {
                "question_coverage": question_coverage_score,
                "answer_explicitness": answer_explicitness_score,
                "structural_clarity": structural_clarity_score,
                "entity_completeness": entity_score,
                "evidence_quality": evidence_quality_score,
                "snippet_ready": snippet_ready_score,
                "technical_accessibility": tech_score,
            },
            "matched_questions": matched_questions,
            "candidate_answers": candidate_answers[:3],
            "methodology_version": settings.AEO_MODEL_VERSION,
        }, findings
