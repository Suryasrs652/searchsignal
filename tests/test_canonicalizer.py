import pytest
from app.core.canonicalizer import normalize_url, extract_domain
from app.crawler.robots import RobotsParser

def test_url_normalization():
    # Downcase scheme and host, remove default port 80, strip fragment, remove utm
    raw = "HTTP://EXAMPLE.COM:80/products/shoes/?utm_source=google&b=2&a=1#section3"
    norm = normalize_url(raw)
    assert norm == "http://example.com/products/shoes/?a=1&b=2"

    # Preserves trailing slash consistency
    raw2 = "https://example.com/about/"
    assert normalize_url(raw2) == "https://example.com/about/"

    assert extract_domain("https://sub.domain.com/path") == "sub.domain.com"

def test_robots_parser_rfc9309():
    txt = """
User-agent: *
Disallow: /admin
Disallow: /private/
Allow: /private/public-doc
Sitemap: https://example.com/sitemap.xml
"""
    parser = RobotsParser(txt, user_agent="SearchSignal")
    assert parser.is_allowed("https://example.com/") is True
    assert parser.is_allowed("https://example.com/admin") is False
    assert parser.is_allowed("https://example.com/private/secret") is False
    # Longest match allow overrides disallow
    assert parser.is_allowed("https://example.com/private/public-doc") is True
    assert parser.sitemaps == ["https://example.com/sitemap.xml"]
