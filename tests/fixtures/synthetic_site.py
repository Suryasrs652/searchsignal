from starlette.applications import Starlette
from starlette.responses import Response, HTMLResponse, PlainTextResponse, RedirectResponse
from starlette.routing import Route
import json

async def robots_txt(request):
    content = """User-agent: *
Disallow: /robots-blocked
Allow: /
Sitemap: http://127.0.0.1:8089/sitemap.xml
"""
    return PlainTextResponse(content)

async def sitemap_xml(request):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>http://127.0.0.1:8089/</loc></url>
  <url><loc>http://127.0.0.1:8089/200</loc></url>
  <url><loc>http://127.0.0.1:8089/schema-valid</loc></url>
  <url><loc>http://127.0.0.1:8089/aeo-faq</loc></url>
</urlset>
"""
    return Response(content, media_type="application/xml")

async def homepage(request):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Synthetic Test Site - Home of SEO Intelligence</title>
  <meta name="description" content="A comprehensive synthetic test site fixture to validate SEO, GEO, and AEO rules deterministically.">
  <link rel="canonical" href="http://127.0.0.1:8089/">
</head>
<body>
  <h1>SearchSignal Synthetic Benchmark Suite</h1>
  <p>Welcome to the synthetic test site designed for automated crawler regression tests.</p>
  <nav>
    <a href="/200">Standard 200 Page</a>
    <a href="/404">Broken 404 Page</a>
    <a href="/301">Redirect 301 Page</a>
    <a href="/missing-title">Missing Title Page</a>
    <a href="/duplicate-title-1">Duplicate Title 1</a>
    <a href="/duplicate-title-2">Duplicate Title 2</a>
    <a href="/noindex">Noindex Directives</a>
    <a href="/canonical-mismatch">Canonical Mismatch</a>
    <a href="/schema-valid">Valid Schema Page</a>
    <a href="/schema-invalid">Invalid Schema Page</a>
    <a href="/schema-price-conflict">Schema Price Conflict</a>
    <a href="/robots-blocked">Robots Blocked URL</a>
    <a href="/aeo-faq">AEO Optimized FAQ Page</a>
  </nav>
</body>
</html>"""
    return HTMLResponse(html)

async def page_200(request):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>High Quality Clean Page - Product Specs 2026</title>
  <meta name="description" content="Clean valid page meeting all foundational technical SEO best practices.">
  <link rel="canonical" href="http://127.0.0.1:8089/200">
</head>
<body>
  <h1>Detailed Product Specifications</h1>
  <p>This page features clean semantic headings, detailed technical specifications, and clear author attribution.</p>
  <p>Written by Alex Morgan, Lead Architect on September 2026.</p>
</body>
</html>"""
    return HTMLResponse(html)

async def page_404(request):
    return HTMLResponse("<h1>404 Not Found</h1>", status_code=404)

async def page_301(request):
    return RedirectResponse(url="/200", status_code=301)

async def page_missing_title(request):
    html = """<!DOCTYPE html>
<html>
<head>
  <meta name="description" content="This page intentionally lacks a title tag.">
</head>
<body>
  <h1>Page With Missing Title</h1>
  <p>Testing that the SEO-TITLE-001 rule correctly flags missing title tags.</p>
</body>
</html>"""
    return HTMLResponse(html)

async def page_dup_title_1(request):
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Identical Duplicate Page Title for Shoes</title>
</head>
<body>
  <h1>Shoe Catalog Page 1</h1>
  <p>Testing duplicate title derivation across different URLs.</p>
</body>
</html>"""
    return HTMLResponse(html)

async def page_dup_title_2(request):
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Identical Duplicate Page Title for Shoes</title>
</head>
<body>
  <h1>Shoe Catalog Page 2</h1>
  <p>Testing duplicate title derivation across different URLs.</p>
</body>
</html>"""
    return HTMLResponse(html)

async def page_noindex(request):
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Private Staging Section</title>
  <meta name="robots" content="noindex, nofollow">
</head>
<body>
  <h1>Internal Staging Portal</h1>
</body>
</html>"""
    return HTMLResponse(html)

async def page_canonical_mismatch(request):
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Canonical Conflict Page</title>
  <link rel="canonical" href="http://127.0.0.1:8089/200">
</head>
<body>
  <h1>Faceted Filter URL</h1>
  <p>Points canonical back to /200.</p>
</body>
</html>"""
    return HTMLResponse(html)

async def page_schema_valid(request):
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "SearchSignal Engine Pro",
        "description": "High throughput audit scanner",
        "offers": {
            "@type": "Offer",
            "price": "49.00",
            "priceCurrency": "USD"
        }
    }
    html = f"""<!DOCTYPE html>
<html>
<head>
  <title>SearchSignal Engine Pro - Pricing $49.00</title>
  <script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body>
  <h1>SearchSignal Engine Pro</h1>
  <p>Starting at $49.00 per month with complete multi-site audit capabilities.</p>
</body>
</html>"""
    return HTMLResponse(html)

async def page_schema_invalid(request):
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Page with Broken Schema</title>
  <script type="application/ld+json">{"@type": "Product", "name": "Broken", broken_syntax</script>
</head>
<body>
  <h1>Broken Schema Test</h1>
</body>
</html>"""
    return HTMLResponse(html)

async def page_schema_price_conflict(request):
    # Schema says $19.99, but page says $99.99!
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Conflicting Widget",
        "offers": {
            "@type": "Offer",
            "price": "19.99",
            "priceCurrency": "USD"
        }
    }
    html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Conflicting Widget - Premium Edition</title>
  <script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body>
  <h1>Conflicting Widget</h1>
  <p>Our official price on the website is $99.99 per unit.</p>
</body>
</html>"""
    return HTMLResponse(html)

async def page_robots_blocked(request):
    return HTMLResponse("<h1>This should not be crawled if respect_robots is true</h1>")

async def page_aeo_faq(request):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Frequently Asked Questions: SearchSignal Pricing & Features</title>
  <meta name="description" content="Everything you need to know about SearchSignal platform features and pricing.">
</head>
<body>
  <h1>SearchSignal Knowledge Base & FAQ</h1>
  
  <h2>What is SearchSignal?</h2>
  <p>SearchSignal is a multi-site intelligence platform that crawls, audits, validates, scores, explains, and prioritizes website improvements across SEO, GEO, and AEO.</p>
  
  <h2>How much does SearchSignal cost?</h2>
  <p>SearchSignal starts at $29 per user per month with unlimited audit scans and automated export reports.</p>
  
  <h2>How does SearchSignal compare vs legacy tools?</h2>
  <p>Compared to legacy crawlers, SearchSignal separates deterministic SEO observations from heuristic GEO/AEO estimates so that no model estimate is ever presented as a search engine fact.</p>

  <h2>What are the system requirements?</h2>
  <p>SearchSignal requires Docker, Python 3.12+, or any standard cloud container environment with minimum 2GB RAM.</p>
</body>
</html>"""
    return HTMLResponse(html)

routes = [
    Route("/robots.txt", robots_txt),
    Route("/sitemap.xml", sitemap_xml),
    Route("/", homepage),
    Route("/200", page_200),
    Route("/404", page_404),
    Route("/301", page_301),
    Route("/missing-title", page_missing_title),
    Route("/duplicate-title-1", page_dup_title_1),
    Route("/duplicate-title-2", page_dup_title_2),
    Route("/noindex", page_noindex),
    Route("/canonical-mismatch", page_canonical_mismatch),
    Route("/schema-valid", page_schema_valid),
    Route("/schema-invalid", page_schema_invalid),
    Route("/schema-price-conflict", page_schema_price_conflict),
    Route("/robots-blocked", page_robots_blocked),
    Route("/aeo-faq", page_aeo_faq),
]

synthetic_app = Starlette(debug=True, routes=routes)
