import uuid
import re
from typing import List, Dict, Any
from app.rules.base import FindingItem, EvidenceClass, Severity, generate_fingerprint

class SEORuleEngine:
    @staticmethod
    def evaluate(audit_id: str, pages: List[Dict[str, Any]], links: List[Dict[str, Any]]) -> List[FindingItem]:
        findings: List[FindingItem] = []
        
        # Build URL lookups and graph for DERIVED analysis
        page_by_norm_url: Dict[str, Dict[str, Any]] = {p["normalized_url"]: p for p in pages}
        inbound_links_count: Dict[str, int] = {p["normalized_url"]: 0 for p in pages}
        titles_map: Dict[str, List[str]] = {}
        descriptions_map: Dict[str, List[str]] = {}

        for link in links:
            target_norm = link.get("normalized_target_url")
            if target_norm in inbound_links_count:
                inbound_links_count[target_norm] += 1

        # First Pass: Group titles & descriptions for duplicate detection
        for p in pages:
            title = (p.get("title") or "").strip()
            if title and p.get("http_status") == 200:
                titles_map.setdefault(title, []).append(p["url"])
            
            desc = (p.get("meta_description") or "").strip()
            if desc and p.get("http_status") == 200:
                descriptions_map.setdefault(desc, []).append(p["url"])

        # Second Pass: Page-level checks
        for p in pages:
            url = p["url"]
            norm_url = p["normalized_url"]
            status_code = p.get("http_status") or 0
            obs = p.get("observation") or {}
            page_id = p.get("id")

            # 1. HTTP Status Codes
            if status_code >= 400:
                severity = Severity.BLOCKER if status_code >= 500 else Severity.CRITICAL
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-HTTP-001",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=severity,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"http_status": status_code, "response_time_ms": p.get("response_time_ms")},
                    fingerprint=generate_fingerprint("SEO-HTTP-001", norm_url, str(status_code)),
                    title=f"HTTP {status_code} Client/Server Error",
                    category="Technical SEO",
                    why_it_matters="Search engine crawlers and users cannot access this page. Broken pages waste crawl budget and cause immediate ranking/indexing drops.",
                    remediation=f"Inspect server logs for {url}. Either restore the resource, fix internal linking, or return an appropriate 301 redirect.",
                    pros=["Restores indexability", "Eliminates user-facing broken experiences"],
                    cons=["Requires web server routing or CMS page review"],
                    validation_method=f"Run curl -I {url} and assert HTTP 200."
                ))
                # Skip HTML checks for non-200 pages
                continue

            if obs.get("robots_blocked"):
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-ROBOTS-001",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.HIGH,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"directive": "Disallow in robots.txt", "url": url},
                    fingerprint=generate_fingerprint("SEO-ROBOTS-001", norm_url, "disallow"),
                    title="URL Blocked by robots.txt Exclusion",
                    category="Crawlability",
                    why_it_matters="Robots.txt disallow prevents search engine crawlers from fetching and parsing the page content.",
                    remediation="If this page should be indexed, adjust the robots.txt disallow pattern to allow Googlebot and other crawlers.",
                    pros=["Allows full search indexing and snippet generation"],
                    cons=["Increases crawl requests to the server"],
                    validation_method="Test URL against Google Search Console robots.txt tester or local RFC 9309 parser."
                ))

            # 2. Metadata: Title
            title = (p.get("title") or "").strip()
            if not title:
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-TITLE-001",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.CRITICAL,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"selector": "head > title", "observed_value": ""},
                    fingerprint=generate_fingerprint("SEO-TITLE-001", norm_url, "missing"),
                    title="Missing <title> Element",
                    category="Metadata",
                    why_it_matters="The <title> tag is one of the most critical on-page ranking and click-through signals. Missing titles lead to poor search engine snippet generation.",
                    remediation="Add a concise, descriptive <title> tag inside the <head> element highlighting the primary intent.",
                    pros=["High positive impact on CTR and SERP visibility", "Simple HTML fix"],
                    cons=["Requires copy review for the page"],
                    validation_method="Inspect rendered DOM and confirm <title> contains non-empty text."
                ))
            elif len(titles_map.get(title, [])) > 1:
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-TITLE-002",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.HIGH,
                    evidence_class=EvidenceClass.DERIVED,
                    status="failed",
                    confidence=1.0,
                    evidence={"title": title, "duplicate_pages_count": len(titles_map[title]), "sample_duplicates": titles_map[title][:3]},
                    fingerprint=generate_fingerprint("SEO-TITLE-002", norm_url, title),
                    title="Duplicate <title> Across Multiple Pages",
                    category="Metadata",
                    why_it_matters="Identical title tags make it difficult for search engines to distinguish which page best satisfies a specific query.",
                    remediation="Customize the title tag to uniquely identify this specific page's product, topic, or section.",
                    pros=["Clarifies topical relevance and prevents keyword self-cannibalization"],
                    cons=["Requires maintaining distinct titles across catalog/pagination"],
                    validation_method="Verify each duplicate URL now yields a unique title in crawl."
                ))

            # Title length advisory
            if title and (len(title) < 20 or len(title) > 70):
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-TITLE-003",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.LOW,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"title_length": len(title), "title": title},
                    fingerprint=generate_fingerprint("SEO-TITLE-003", norm_url, str(len(title))),
                    title="Advisory: Title Length Outside Standard Display Range (30-65 chars)",
                    category="Metadata",
                    why_it_matters="Advisory notice: Very short titles may miss relevant query terms, while very long titles may get truncated in SERP snippets. (Note: character limits are visual guidelines, not Google ranking rules).",
                    remediation="Review title length for optimal SERP display readability.",
                    pros=["Optimizes search snippet preview presentation"],
                    cons=["Low technical priority"],
                    validation_method="Assert title length is between 30 and 65 characters."
                ))

            # 3. Meta Description
            meta_desc = (p.get("meta_description") or "").strip()
            if not meta_desc:
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-DESC-001",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.MEDIUM,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"selector": "meta[name='description']", "observed_value": ""},
                    fingerprint=generate_fingerprint("SEO-DESC-001", norm_url, "missing"),
                    title="Missing Meta Description",
                    category="Metadata",
                    why_it_matters="While not a direct ranking factor, meta descriptions often form the SERP snippet and directly influence organic click-through rates.",
                    remediation="Add a compelling 120-160 character meta description outlining the page value proposition.",
                    pros=["Improves SERP CTR"],
                    cons=["Requires copywriting effort"],
                    validation_method="Check meta[name='description'] tag in DOM."
                ))

            # 4. Meta Robots Noindex
            meta_robots = (p.get("robots") or "").lower()
            if "noindex" in meta_robots:
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-ROBOTS-002",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.HIGH,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"meta_robots": meta_robots},
                    fingerprint=generate_fingerprint("SEO-ROBOTS-002", norm_url, meta_robots),
                    title="Page Marked with 'noindex' Directive",
                    category="Indexability",
                    why_it_matters="The 'noindex' tag instructs search engines NOT to index this page in search results.",
                    remediation="If this page is intended to rank in organic search, remove the 'noindex' directive from meta robots or X-Robots-Tag.",
                    pros=["Enables search engines to index the page"],
                    cons=["None if intended to be public; intentional if staging or private portal"],
                    validation_method="Verify meta[name='robots'] does not contain 'noindex'."
                ))

            # 5. Headings: H1 presence and structure
            h1_tags = obs.get("h1_tags") or []
            if len(h1_tags) == 0:
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-H1-001",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.HIGH,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"h1_count": 0, "selector": "h1"},
                    fingerprint=generate_fingerprint("SEO-H1-001", norm_url, "0"),
                    title="Missing Primary <h1> Heading",
                    category="Content",
                    why_it_matters="An <h1> heading gives both search engines and users a clear summary of the page's core subject.",
                    remediation="Include a single, prominent <h1> tag that describes the main topic of the page.",
                    pros=["Improves semantic hierarchy and accessibility"],
                    cons=["Requires layout styling adjustment"],
                    validation_method="Assert document.querySelectorAll('h1').length === 1."
                ))
            elif len(h1_tags) > 1:
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-H1-002",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.LOW,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"h1_count": len(h1_tags), "h1_samples": h1_tags[:3]},
                    fingerprint=generate_fingerprint("SEO-H1-002", norm_url, str(len(h1_tags))),
                    title="Multiple <h1> Headings Found",
                    category="Content",
                    why_it_matters="Having multiple <h1> elements can dilute the primary topical focus and complicate document outline hierarchy.",
                    remediation="Convert secondary <h1> headings into <h2> or <h3> subheadings.",
                    pros=["Cleaner document outline for search and screen readers"],
                    cons=["CSS styling changes"],
                    validation_method="Confirm only one <h1> tag exists per page template."
                ))

            # 6. Content Word Count
            word_count = p.get("word_count") or 0
            if word_count < 150:
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-CONTENT-001",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.MEDIUM,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"word_count": word_count, "minimum_recommended": 200},
                    fingerprint=generate_fingerprint("SEO-CONTENT-001", norm_url, str(word_count)),
                    title="Low Word Count / Thin Content",
                    category="Content",
                    why_it_matters="Pages with very little textual content often struggle to satisfy user search intent or convey sufficient topical depth.",
                    remediation="Expand page content with comprehensive explanations, answers to common user questions, and specific entity details.",
                    pros=["Increases topical coverage and dwell time"],
                    cons=["Requires content writing resources"],
                    validation_method="Confirm word count exceeds 200 words on informative pages."
                ))

            # 7. Canonical Tag Audit
            canonical = (p.get("canonical_url") or "").strip()
            if not canonical:
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-CANONICAL-001",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.MEDIUM,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"selector": "link[rel='canonical']", "observed_value": None},
                    fingerprint=generate_fingerprint("SEO-CANONICAL-001", norm_url, "missing"),
                    title="Missing Self-Referencing Canonical Tag",
                    category="Indexability",
                    why_it_matters="Without a canonical tag, URL parameters or tracking parameters can generate duplicate indexed URLs in search results.",
                    remediation="Add a <link rel='canonical' href='...' /> pointing explicitly to the definitive URL for this page.",
                    pros=["Prevents accidental URL parameter duplication in index"],
                    cons=["Simple head tag addition"],
                    validation_method="Confirm canonical tag matches desired canonical URL."
                ))
            else:
                from app.core.canonicalizer import normalize_url
                norm_canonical = normalize_url(canonical)
                if norm_canonical != norm_url:
                    findings.append(FindingItem(
                        finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                        audit_id=audit_id,
                        rule_id="SEO-CANONICAL-002",
                        page_id=page_id,
                        url=url,
                        normalized_url=norm_url,
                        severity=Severity.HIGH,
                        evidence_class=EvidenceClass.EXACT,
                        status="failed",
                        confidence=1.0,
                        evidence={"observed_url": url, "canonical_target": canonical},
                        fingerprint=generate_fingerprint("SEO-CANONICAL-002", norm_url, norm_canonical),
                        title="Canonical Points to a Different URL",
                        category="Indexability",
                        why_it_matters="This page specifies another URL as its canonical master. Search engines will attribute indexability and ranking equity to the target URL rather than this page.",
                        remediation="Verify whether this non-self canonical is intentional (e.g. syndicated content or faceted navigation parameter). If not, update it to point to this URL.",
                        pros=["Ensures proper ranking equity consolidation"],
                        cons=["May de-index this URL if pointing elsewhere"],
                        validation_method="Inspect canonical href and confirm intended target."
                    ))

            # 8. Internal Linking: Orphan Page Detection & Link Depth
            inbound_count = inbound_links_count.get(norm_url, 0)
            if inbound_count == 0 and p.get("depth", 0) > 0:
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-LINK-001",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.HIGH,
                    evidence_class=EvidenceClass.DERIVED,
                    status="failed",
                    confidence=1.0,
                    evidence={"inbound_internal_links": 0, "crawl_depth": p.get("depth")},
                    fingerprint=generate_fingerprint("SEO-LINK-001", norm_url, "orphan"),
                    title="Orphan Page: No Inbound Internal Links Found",
                    category="Internal Linking",
                    why_it_matters="Orphan pages have zero internal links pointing to them from other pages on the site, making them virtually undiscoverable to crawlers and users without a sitemap.",
                    remediation="Add contextual internal links to this page from relevant parent category pages or related articles.",
                    pros=["Passes internal PageRank and discovery signals"],
                    cons=["Requires finding natural contextual anchor placement"],
                    validation_method="Assert inbound link count > 0 in next crawl."
                ))

            # 9. Structured Data & Truthfulness Check (Section 21 & 22)
            json_ld = obs.get("json_ld_schemas") or []
            if not json_ld:
                findings.append(FindingItem(
                    finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                    audit_id=audit_id,
                    rule_id="SEO-SCHEMA-001",
                    page_id=page_id,
                    url=url,
                    normalized_url=norm_url,
                    severity=Severity.LOW,
                    evidence_class=EvidenceClass.EXACT,
                    status="failed",
                    confidence=1.0,
                    evidence={"json_ld_blocks_count": 0},
                    fingerprint=generate_fingerprint("SEO-SCHEMA-001", norm_url, "missing"),
                    title="No JSON-LD Structured Data Detected",
                    category="Structured Data",
                    why_it_matters="Structured data helps search engines understand entities, products, organizations, and articles, qualifying pages for rich snippets in SERPs.",
                    remediation="Add Schema.org JSON-LD markup appropriate for the page type (e.g. WebSite, Organization, Article, or Product).",
                    pros=["Enhances SERP rich snippets and entity clarity"],
                    cons=["Requires structured data maintenance"],
                    validation_method="Validate JSON-LD syntax using Google Rich Results Test."
                ))
            else:
                for schema in json_ld:
                    if "_parse_error" in schema:
                        findings.append(FindingItem(
                            finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                            audit_id=audit_id,
                            rule_id="SEO-SCHEMA-002",
                            page_id=page_id,
                            url=url,
                            normalized_url=norm_url,
                            severity=Severity.CRITICAL,
                            evidence_class=EvidenceClass.VALIDATED,
                            status="failed",
                            confidence=1.0,
                            evidence={"error": schema["_parse_error"], "raw_snippet": schema.get("_raw")},
                            fingerprint=generate_fingerprint("SEO-SCHEMA-002", norm_url, schema["_parse_error"]),
                            title="Invalid JSON-LD Syntax Error",
                            category="Structured Data",
                            why_it_matters="Syntax errors in JSON-LD prevent search engines from parsing the structured data completely.",
                            remediation="Correct JSON syntax (missing quotes, trailing commas, or brackets).",
                            pros=["Restores rich snippet eligibility"],
                            cons=["None"],
                            validation_method="JSON.parse() must succeed without error."
                        ))
                    else:
                        # Truthfulness check (Section 22): compare schema price with visible DOM
                        if isinstance(schema, dict) and schema.get("@type") == "Product":
                            offers = schema.get("offers", {})
                            if isinstance(offers, dict) and "price" in offers:
                                schema_price = str(offers["price"]).strip()
                                visible_text = obs.get("visible_text_snippet", "")
                                # If schema specifies a price like '19.99' but visible page has '$29.99' and doesn't mention '$19.99'
                                if "$" in visible_text and schema_price not in visible_text:
                                    findings.append(FindingItem(
                                        finding_id=f"FND-{uuid.uuid4().hex[:6].upper()}",
                                        audit_id=audit_id,
                                        rule_id="SEO-SCHEMA-003",
                                        page_id=page_id,
                                        url=url,
                                        normalized_url=norm_url,
                                        severity=Severity.CRITICAL,
                                        evidence_class=EvidenceClass.VALIDATED,
                                        status="failed",
                                        confidence=0.95,
                                        evidence={"schema_price": schema_price, "visible_snippet": visible_text[:300]},
                                        fingerprint=generate_fingerprint("SEO-SCHEMA-003", norm_url, schema_price),
                                        title="Structured Data Truthfulness: Schema Price Conflicts with Visible Content",
                                        category="Structured Data",
                                        why_it_matters="Google explicitly penalizes structured data that contradicts visible user-facing page information.",
                                        remediation="Synchronize structured data properties with the exact visible content shown to users.",
                                        pros=["Protects against manual actions and spam penalties"],
                                        cons=["Requires automated sync between price service and schema tags"],
                                        validation_method="Assert schema price equals visible text price."
                                    ))

        return findings
