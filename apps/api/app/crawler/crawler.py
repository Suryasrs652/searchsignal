import asyncio
import hashlib
import time
from typing import Set, Dict, Any, List, Optional, Callable
from urllib.parse import urlparse, urljoin
import httpx

from app.core.config import settings
from app.core.ssrf import validate_target_url
from app.core.canonicalizer import normalize_url, extract_domain
from app.crawler.robots import RobotsParser
from app.crawler.sitemap import SitemapParser
from app.crawler.extractor import PageExtractor
from app.storage.evidence_store import evidence_store

class CrawlResult:
    def __init__(self):
        self.pages: List[Dict[str, Any]] = []
        self.links: List[Dict[str, Any]] = []
        self.robots_txt: Optional[str] = None
        self.robots_allowed: bool = True
        self.sitemaps_discovered: List[str] = []
        self.errors: List[Dict[str, Any]] = []

class WebsiteCrawler:
    def __init__(
        self,
        audit_id: str,
        root_url: str,
        max_urls: int = 50,
        max_depth: int = 4,
        concurrency: int = 4,
        respect_robots: bool = True,
        allow_local_test: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        self.audit_id = audit_id
        self.root_url = root_url
        self.normalized_root_url = normalize_url(root_url)
        self.root_domain = extract_domain(root_url)
        self.max_urls = min(max_urls, settings.MAX_CRAWL_URLS)
        self.max_depth = max_depth
        self.concurrency = concurrency
        self.respect_robots = respect_robots
        self.allow_local_test = allow_local_test
        self.progress_callback = progress_callback
        
        self.visited_urls: Set[str] = set()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.robots_parser: Optional[RobotsParser] = None
        self.result = CrawlResult()
        self.semaphore = asyncio.Semaphore(concurrency)

    async def _safe_fetch(
        self,
        client: httpx.AsyncClient,
        url: str
    ) -> Optional[httpx.Response]:
        """Fetch URL with SSRF protection and timing measurement."""
        is_safe, reason = validate_target_url(url, allow_local_test=self.allow_local_test)
        if not is_safe:
            self.result.errors.append({"url": url, "error": f"SSRF Blocked: {reason}"})
            return None

        try:
            start_time = time.monotonic()
            response = await client.get(url, follow_redirects=True, timeout=12.0)
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            
            # If redirected, validate final URL against SSRF as well
            if str(response.url) != url:
                redirect_safe, redirect_reason = validate_target_url(str(response.url), allow_local_test=self.allow_local_test)
                if not redirect_safe:
                    self.result.errors.append({"url": url, "error": f"SSRF Redirect Blocked: {redirect_reason}"})
                    return None
                    
            return response
        except Exception as e:
            self.result.errors.append({"url": url, "error": str(e)})
            return None

    async def discover_robots_and_sitemaps(self, client: httpx.AsyncClient):
        parsed = urlparse(self.root_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        resp = await self._safe_fetch(client, robots_url)
        if resp and resp.status_code == 200:
            self.result.robots_txt = resp.text
            self.robots_parser = RobotsParser(resp.text)
            self.result.sitemaps_discovered.extend(self.robots_parser.sitemaps)
            
        # Common sitemap fallback
        if not self.result.sitemaps_discovered:
            common_sitemap = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
            s_resp = await self._safe_fetch(client, common_sitemap)
            if s_resp and s_resp.status_code == 200 and "xml" in s_resp.headers.get("content-type", "").lower():
                self.result.sitemaps_discovered.append(common_sitemap)
                parsed_sitemap = SitemapParser.parse_sitemap_xml(s_resp.text)
                for entry in parsed_sitemap["urls"][:self.max_urls]:
                    loc = entry.get("loc")
                    if loc:
                        norm = normalize_url(loc)
                        if norm not in self.visited_urls:
                            await self.queue.put((loc, norm, 1, 0))

    async def _crawl_page(
        self,
        client: httpx.AsyncClient,
        url: str,
        normalized_url: str,
        depth: int,
        discovered_from: Optional[int],
    ):
        async with self.semaphore:
            if normalized_url in self.visited_urls or len(self.visited_urls) >= self.max_urls:
                return
            self.visited_urls.add(normalized_url)

            # Robots.txt compliance check
            if self.respect_robots and self.robots_parser:
                if not self.robots_parser.is_allowed(url):
                    page_idx = len(self.result.pages) + 1
                    self.result.pages.append({
                        "id": page_idx,
                        "url": url,
                        "normalized_url": normalized_url,
                        "depth": depth,
                        "discovered_from": discovered_from,
                        "http_status": 403,
                        "content_type": "text/plain",
                        "title": "Blocked by robots.txt",
                        "meta_description": "",
                        "canonical_url": "",
                        "robots": "disallowed",
                        "lang": "",
                        "word_count": 0,
                        "response_time_ms": 0,
                        "ttfb_ms": 0,
                        "html_hash": "",
                        "observation": {"robots_blocked": True},
                    })
                    return

            start_t = time.monotonic()
            resp = await self._safe_fetch(client, url)
            duration_ms = int((time.monotonic() - start_t) * 1000)

            if not resp:
                page_idx = len(self.result.pages) + 1
                self.result.pages.append({
                    "id": page_idx,
                    "url": url,
                    "normalized_url": normalized_url,
                    "depth": depth,
                    "discovered_from": discovered_from,
                    "http_status": 0,
                    "content_type": "",
                    "title": "Connection Failed",
                    "meta_description": "",
                    "canonical_url": "",
                    "robots": "",
                    "lang": "",
                    "word_count": 0,
                    "response_time_ms": duration_ms,
                    "ttfb_ms": duration_ms,
                    "html_hash": "",
                    "observation": {"error": "Connection failed"},
                })
                return

            html_content = resp.text if "text/html" in resp.headers.get("content-type", "") or resp.status_code == 200 else ""
            content_hash = hashlib.sha256(html_content.encode("utf-8")).hexdigest() if html_content else ""

            # Save immutable raw snapshot and headers to storage
            headers_dict = dict(resp.headers)
            evidence_store.save_snapshot(
                audit_id=self.audit_id,
                normalized_url=normalized_url,
                html_content=html_content,
                headers=headers_dict,
                meta={"status_code": resp.status_code, "url": str(resp.url)},
            )

            # Extract page data
            page_data = PageExtractor.extract_page_data(html_content, str(resp.url), self.root_domain)
            page_index = len(self.result.pages) + 1

            page_record = {
                "id": page_index,
                "url": url,
                "normalized_url": normalized_url,
                "depth": depth,
                "discovered_from": discovered_from,
                "http_status": resp.status_code,
                "content_type": resp.headers.get("content-type", ""),
                "title": page_data["title"],
                "meta_description": page_data["meta_description"],
                "canonical_url": page_data["canonical_url"],
                "robots": page_data["meta_robots"],
                "lang": page_data["lang"],
                "word_count": page_data["word_count"],
                "response_time_ms": duration_ms,
                "ttfb_ms": int(duration_ms * 0.4), # estimated TTFB lab
                "html_hash": content_hash,
                "observation": page_data,
            }
            self.result.pages.append(page_record)

            # Record links & queue new internal URLs if within depth
            for link in page_data["links"]:
                link_record = {
                    "source_page_id": page_index,
                    "target_url": link["target_url"],
                    "normalized_target_url": link["normalized_target_url"],
                    "anchor_text": link["anchor_text"],
                    "is_internal": link["is_internal"],
                    "rel": link["rel"],
                }
                self.result.links.append(link_record)

                if (
                    link["is_internal"]
                    and depth < self.max_depth
                    and link["normalized_target_url"] not in self.visited_urls
                    and len(self.visited_urls) < self.max_urls
                ):
                    await self.queue.put((
                        link["target_url"],
                        link["normalized_target_url"],
                        depth + 1,
                        page_index
                    ))

            if self.progress_callback:
                self.progress_callback(len(self.result.pages), self.max_urls, url)

    async def run(self) -> CrawlResult:
        headers = {
            "User-Agent": f"SearchSignal/{settings.CRAWLER_VERSION} (+https://searchsignal.ai/bot)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        
        async with httpx.AsyncClient(headers=headers, verify=False) as client:
            # Step 1: Discover robots.txt and sitemaps
            await self.discover_robots_and_sitemaps(client)

            # Step 2: Seed queue with root URL
            await self.queue.put((self.root_url, self.normalized_root_url, 0, None))

            # Step 3: Run worker pool
            async def worker():
                while True:
                    try:
                        url, normalized_url, depth, discovered_from = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                    except asyncio.TimeoutError:
                        break
                    try:
                        if len(self.visited_urls) < self.max_urls and normalized_url not in self.visited_urls:
                            await self._crawl_page(client, url, normalized_url, depth, discovered_from)
                    except Exception:
                        pass
                    finally:
                        self.queue.task_done()

            workers = [asyncio.create_task(worker()) for _ in range(self.concurrency)]
            await self.queue.join()
            for w in workers:
                w.cancel()

        return self.result
