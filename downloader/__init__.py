from __future__ import annotations

from config import DOWNLOAD_DIR

from . import instagram, pinterest, ytdlp
from .common import Downloaded, cleanup
from .errors import DownloadFailed, MediaTooLarge, UnsupportedMedia
from .links import find_media_url, platform_of
from .reasons import explain

__all__ = [
    "DownloadFailed",
    "MediaTooLarge",
    "UnsupportedMedia",
    "cleanup",
    "download_media",
    "explain",
    "find_media_url",
]

_FALLBACKS = {
    "instagram": instagram.download,
    "pinterest": pinterest.download,
}


def download_media(url: str) -> Downloaded:
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    try:
        return ytdlp.download(url)
    except (DownloadFailed, MediaTooLarge):
        raise
    except Exception as exc:
        if platform_of(url) == "tiktok" and "/photo/" in f"{url} {exc}":
            raise UnsupportedMedia("TikTok photo posts aren't supported yet.") from exc
        fallback = _FALLBACKS.get(platform_of(url))
        if fallback is None:
            raise DownloadFailed(str(exc)) from exc
        return fallback(url)
