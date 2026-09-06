import json
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from app.core.canonicalizer import normalize_url, extract_domain

class PageExtractor:
    @staticmethod
    def extract_page_data(
        html: str,
        current_url: str,
        root_domain: str,
    ) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        
        # Title
        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else ""
        
        # Meta description
        meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        description = meta_desc.get("content", "").strip() if meta_desc else ""
        
        # Meta robots
        meta_robots_tag = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
        meta_robots = meta_robots_tag.get("content", "").strip().lower() if meta_robots_tag else ""
        
        # Canonical link
        canonical_tag = soup.find("link", attrs={"rel": re.compile(r"^canonical$", re.I)})
        canonical_url = canonical_tag.get("href", "").strip() if canonical_tag else ""
        if canonical_url:
            canonical_url = urljoin(current_url, canonical_url)
            
        # Language
        html_tag = soup.find("html")
        lang = html_tag.get("lang", "").strip() if html_tag else ""
        
        # Headings
        h1_tags = [h.get_text().strip() for h in soup.find_all("h1") if h.get_text().strip()]
        h2_tags = [h.get_text().strip() for h in soup.find_all("h2") if h.get_text().strip()]
        h3_tags = [h.get_text().strip() for h in soup.find_all("h3") if h.get_text().strip()]
        
        # Extract JSON-LD BEFORE decomposing script tags
        json_ld_schemas = []
        for script in soup.find_all("script", type="application/ld+json"):
            content = script.string or script.get_text()
            if content and content.strip():
                try:
                    data = json.loads(content.strip())
                    if isinstance(data, list):
                        json_ld_schemas.extend(data)
                    else:
                        json_ld_schemas.append(data)
                except Exception as e:
                    json_ld_schemas.append({"_parse_error": str(e), "_raw": content.strip()[:500]})

        # Visible Text & Word Count
        # Strip script and style elements
        for element in soup(["script", "style", "noscript", "svg"]):
            element.decompose()
        visible_text = soup.get_text(separator=" ", strip=True)
        words = re.findall(r"\b\w+\b", visible_text)
        word_count = len(words)
        
        raw_html_len = len(html)
        text_ratio = round(len(visible_text) / (raw_html_len or 1), 4)
        
        # Extract Links
        links: List[Dict[str, Any]] = []
        for a in soup.find_all("a", href=True):
            raw_href = a["href"].strip()
            if not raw_href or raw_href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            
            absolute_href = urljoin(current_url, raw_href)
            normalized_href = normalize_url(absolute_href)
            target_domain = extract_domain(absolute_href)
            is_internal = (target_domain == root_domain) or (target_domain.endswith("." + root_domain))
            
            rel = a.get("rel", [])
            rel_str = " ".join(rel) if isinstance(rel, list) else str(rel)
            
            links.append({
                "target_url": absolute_href,
                "normalized_target_url": normalized_href,
                "anchor_text": a.get_text().strip()[:200],
                "is_internal": is_internal,
                "rel": rel_str,
            })
            
        # Extract OpenGraph
        og_data = {}
        for tag in soup.find_all("meta", property=re.compile(r"^og:", re.I)):
            prop = tag.get("property", "").lower()
            val = tag.get("content", "").strip()
            if prop and val:
                og_data[prop] = val

        # Paragraphs for AEO extraction
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 20]
        
        return {
            "title": title,
            "meta_description": description,
            "meta_robots": meta_robots,
            "canonical_url": canonical_url,
            "lang": lang,
            "h1_tags": h1_tags,
            "h2_tags": h2_tags,
            "h3_tags": h3_tags,
            "word_count": word_count,
            "text_ratio": text_ratio,
            "visible_text_snippet": visible_text[:1000],
            "paragraphs": paragraphs[:30],
            "links": links,
            "json_ld_schemas": json_ld_schemas,
            "og_data": og_data,
        }
