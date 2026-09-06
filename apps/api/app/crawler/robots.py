import re
from urllib.parse import urlparse
from typing import List, Dict, Tuple, Optional

class RobotsParser:
    def __init__(self, content: str, user_agent: str = "SearchSignal"):
        self.user_agent = user_agent.lower()
        self.rules: List[Tuple[str, str, bool]] = []  # (ua, path_pattern, is_allow)
        self.sitemaps: List[str] = []
        self._parse(content)

    def _parse(self, content: str):
        current_uas = []
        for raw_line in content.splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue

            if ":" not in line:
                continue

            directive, value = line.split(":", 1)
            directive = directive.strip().lower()
            value = value.strip()

            if directive == "user-agent":
                ua = value.lower()
                current_uas.append(ua)
            elif directive == "disallow":
                if not value:  # Empty disallow means allow all
                    for ua in current_uas:
                        self.rules.append((ua, "/", True))
                else:
                    for ua in current_uas:
                        self.rules.append((ua, value, False))
            elif directive == "allow":
                if value:
                    for ua in current_uas:
                        self.rules.append((ua, value, True))
            elif directive == "sitemap":
                if value:
                    self.sitemaps.append(value)
            else:
                # Reset current_uas if non-ua directive encountered
                pass

    def _pattern_to_regex(self, pattern: str) -> re.Pattern:
        # RFC 9309 regex conversion with * and $
        escaped = re.escape(pattern)
        escaped = escaped.replace(r"\*", ".*")
        if escaped.endswith(r"\$"):
            escaped = escaped[:-2] + "$"
        else:
            escaped = escaped + ".*"
        return re.compile("^" + escaped)

    def is_allowed(self, url: str) -> bool:
        """Determines if the given URL is allowed according to RFC 9309 longest-match rule."""
        parsed = urlparse(url)
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"

        # Filter rules relevant to our user_agent or fallback to '*'
        applicable_rules = []
        for ua, pattern, is_allow in self.rules:
            if ua == self.user_agent or ua == "*":
                applicable_rules.append((ua == self.user_agent, len(pattern), pattern, is_allow))

        if not applicable_rules:
            return True

        # Sort by: 1) exact user agent match, 2) longest pattern length, 3) allow over disallow on equal length
        applicable_rules.sort(key=lambda r: (1 if r[0] else 0, r[1], 1 if r[3] else 0), reverse=True)

        for _, _, pattern, is_allow in applicable_rules:
            regex = self._pattern_to_regex(pattern)
            if regex.match(path):
                return is_allow

        return True
