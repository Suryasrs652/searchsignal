import pytest
from app.rules.base import EvidenceClass, Severity
from app.rules.seo_rules import SEORuleEngine
from app.engines.aeo_engine import AEOEngine
from app.engines.geo_engine import GEOEngine
from app.engines.scoring_engine import ScoringEngine
from app.engines.growth_engine import GrowthEngine

def test_seo_rules_detection_and_classification():
    mock_pages = [
        {
            "id": 1,
            "url": "http://127.0.0.1:8089/",
            "normalized_url": "http://127.0.0.1:8089/",
            "http_status": 200,
            "title": "Home Page",
            "meta_description": "Welcome",
            "canonical_url": "http://127.0.0.1:8089/",
            "robots": "",
            "word_count": 350,
            "depth": 0,
            "observation": {
                "h1_tags": ["Welcome"],
                "json_ld_schemas": [{"@context": "https://schema.org", "@type": "WebSite"}],
                "visible_text_snippet": "Welcome to our platform",
            }
        },
        {
            "id": 2,
            "url": "http://127.0.0.1:8089/missing-title",
            "normalized_url": "http://127.0.0.1:8089/missing-title",
            "http_status": 200,
            "title": "",
            "meta_description": "",
            "canonical_url": "",
            "robots": "",
            "word_count": 80,
            "depth": 1,
            "observation": {
                "h1_tags": [],
                "json_ld_schemas": [],
                "visible_text_snippet": "Just a small test page",
            }
        },
        {
            "id": 3,
            "url": "http://127.0.0.1:8089/404-broken",
            "normalized_url": "http://127.0.0.1:8089/404-broken",
            "http_status": 404,
            "title": "",
            "meta_description": "",
            "canonical_url": "",
            "robots": "",
            "word_count": 0,
            "depth": 1,
            "observation": {}
        },
        {
            "id": 4,
            "url": "http://127.0.0.1:8089/conflict",
            "normalized_url": "http://127.0.0.1:8089/conflict",
            "http_status": 200,
            "title": "Conflicting Product",
            "meta_description": "Great item",
            "canonical_url": "http://127.0.0.1:8089/conflict",
            "robots": "",
            "word_count": 250,
            "depth": 1,
            "observation": {
                "h1_tags": ["Conflicting Product"],
                "json_ld_schemas": [{
                    "@context": "https://schema.org",
                    "@type": "Product",
                    "offers": {"price": "19.99"}
                }],
                "visible_text_snippet": "The retail price is $99.99 for this item",
            }
        }
    ]

    mock_links = [
        {"source_page_id": 1, "target_url": "http://127.0.0.1:8089/missing-title", "normalized_target_url": "http://127.0.0.1:8089/missing-title", "is_internal": True},
        {"source_page_id": 1, "target_url": "http://127.0.0.1:8089/404-broken", "normalized_target_url": "http://127.0.0.1:8089/404-broken", "is_internal": True},
    ]

    findings = SEORuleEngine.evaluate("audit-123", mock_pages, mock_links)
    
    # 1. Verify HTTP 404 is detected with EXACT class
    http_findings = [f for f in findings if f.rule_id == "SEO-HTTP-001"]
    assert len(http_findings) == 1
    assert http_findings[0].evidence_class == EvidenceClass.EXACT
    assert http_findings[0].severity == Severity.CRITICAL

    # 2. Verify Missing Title is detected with EXACT class
    title_findings = [f for f in findings if f.rule_id == "SEO-TITLE-001"]
    assert len(title_findings) == 1
    assert title_findings[0].evidence_class == EvidenceClass.EXACT

    # 3. Verify Structured Data Truthfulness Conflict is detected with VALIDATED class
    truth_findings = [f for f in findings if f.rule_id == "SEO-SCHEMA-003"]
    assert len(truth_findings) == 1
    assert truth_findings[0].evidence_class == EvidenceClass.VALIDATED
    assert truth_findings[0].severity == Severity.CRITICAL

def test_aeo_and_geo_heuristics():
    faq_page = {
        "id": 10,
        "url": "http://127.0.0.1:8089/faq",
        "normalized_url": "http://127.0.0.1:8089/faq",
        "http_status": 200,
        "title": "FAQ on Pricing",
        "word_count": 400,
        "observation": {
            "h2_tags": ["What is SearchSignal?", "How much does SearchSignal cost?"],
            "paragraphs": [
                "SearchSignal is an intelligence platform designed to audit and score websites across SEO, GEO, and AEO.",
                "SearchSignal costs $29 per month with unlimited projects and audits."
            ],
            "visible_text_snippet": "What is SearchSignal? It is a platform. How much does it cost? $29/month. Written by Alex.",
            "json_ld_schemas": [{"@type": "Organization", "name": "SearchSignal"}]
        }
    }

    aeo_res, aeo_findings = AEOEngine.evaluate_page(faq_page, "audit-123")
    assert aeo_res["aeo_score"] >= 60
    for f in aeo_findings:
        assert f.evidence_class == EvidenceClass.HEURISTIC
        assert "HEURISTIC — not an official search-engine metric" in f.evidence["disclaimer"]

    geo_res, geo_findings = GEOEngine.evaluate_page(faq_page, "audit-123")
    assert geo_res["geo_score"] >= 50
    for f in geo_findings:
        assert f.evidence_class == EvidenceClass.HEURISTIC

def test_scoring_and_growth_engine():
    pages = [{"id": 1, "http_status": 200, "response_time_ms": 350}]
    findings = []
    
    scores = ScoringEngine.calculate_scores(pages, findings, [80.0], [75.0])
    score_map = {s["dimension"]: s["score"] for s in scores}
    assert score_map["SEO Health"] >= 95.0
    assert score_map["AEO Readiness"] == 80.0
    assert score_map["GEO Readiness"] == 75.0

    # Test growth roadmap prioritization
    f_blocker = SEORuleEngine.evaluate("audit-123", [{"id": 1, "url": "http://test.com", "normalized_url": "http://test.com", "http_status": 500, "observation": {}}], [])
    recs = GrowthEngine.generate_recommendations(f_blocker, total_pages=1)
    assert len(recs) > 0
    assert recs[0]["priority_group"] == "now"
    assert recs[0]["opportunity_score"] > 80
