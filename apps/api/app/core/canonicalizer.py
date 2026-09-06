import posixpath
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "msclkid", "mc_cid", "mc_eid"
}

def normalize_url(url: str, strip_tracking: bool = True) -> str:
    """
    Deterministically normalizes a URL according to Section 12:
    - Downcases scheme and host
    - Removes default ports
    - Removes fragment
    - Normalizes path slashes
    - Sorts query parameters and removes standard marketing tracking params
    """
    if not url:
        return ""
    
    url = url.strip()
    parsed = urlparse(url)
    
    scheme = parsed.scheme.lower() if parsed.scheme else "http"
    netloc = parsed.netloc.lower() if parsed.netloc else ""
    
    # Strip default ports
    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]
        
    # Clean and normalize path
    path = parsed.path
    if not path:
        path = "/"
    else:
        # Collapse multiple slashes
        parts = [p for p in path.split("/") if p]
        has_trailing = path.endswith("/")
        path = "/" + "/".join(parts)
        if has_trailing and path != "/":
            path += "/"
            
    # Clean query parameters
    query = ""
    if parsed.query:
        pairs = parse_qsl(parsed.query, keep_blank_values=True)
        filtered = []
        for k, v in pairs:
            if strip_tracking and k.lower() in TRACKING_PARAMS:
                continue
            filtered.append((k, v))
        filtered.sort(key=lambda x: x[0])
        query = urlencode(filtered)
        
    # No fragments preserved in normalized URLs
    return urlunparse((scheme, netloc, path, "", query, ""))

def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.hostname.lower() if parsed.hostname else ""
