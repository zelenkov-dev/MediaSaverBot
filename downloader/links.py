from __future__ import annotations

import re
from urllib.parse import urlparse

_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_TRAILING_PUNCTUATION = ").,!?…»"
_INSTAGRAM_PATHS = ("/reel/", "/reels/", "/p/")


def platform_of(url: str) -> str | None:
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.lower()

    if host.endswith("tiktok.com"):
        return "tiktok"
    if host == "youtu.be" or (host.endswith("youtube.com") and "/shorts/" in path):
        return "youtube"
    if host.endswith("instagram.com") and any(p in path for p in _INSTAGRAM_PATHS):
        return "instagram"
    if host == "pin.it" or ("pinterest." in host and "/pin/" in path):
        return "pinterest"
    return None


def find_media_url(text: str | None) -> str | None:
    for match in _URL_RE.findall(text or ""):
        url = match.rstrip(_TRAILING_PUNCTUATION)
        if platform_of(url):
            return url
    return None
