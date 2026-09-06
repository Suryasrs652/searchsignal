import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

class SitemapParser:
    @staticmethod
    def parse_sitemap_xml(xml_content: str) -> Dict[str, Any]:
        """
        Parses standard XML sitemaps or sitemap index files.
        Extracts loc, lastmod, changefreq, priority.
        """
        urls: List[Dict[str, str]] = []
        sub_sitemaps: List[str] = []
        
        if not xml_content or not xml_content.strip():
            return {"urls": [], "sitemaps": [], "is_valid": False, "error": "Empty sitemap"}

        try:
            # Strip namespaces for simple universal querying
            root = ET.fromstring(xml_content)
            tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

            if tag == "sitemapindex":
                for sitemap in root:
                    for child in sitemap:
                        ctag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                        if ctag == "loc" and child.text:
                            sub_sitemaps.append(child.text.strip())
            elif tag == "urlset":
                for url_elem in root:
                    url_data = {}
                    for child in url_elem:
                        ctag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                        if child.text:
                            url_data[ctag] = child.text.strip()
                    if "loc" in url_data:
                        urls.append(url_data)

            return {
                "urls": urls,
                "sitemaps": sub_sitemaps,
                "is_valid": True,
                "error": None,
            }
        except Exception as e:
            return {
                "urls": [],
                "sitemaps": [],
                "is_valid": False,
                "error": f"Malformed XML: {e}",
            }
