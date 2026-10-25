from __future__ import annotations

from config import DOWNLOAD_DIR

from . import instagram, pinterest, ytdlp
from .common import cleanup
from .errors import DownloadFailed, MediaTooLarge
from .links import find_media_url, platform_of

__all__ = ["DownloadFailed", "MediaTooLarge", "cleanup", "download_media", "find_media_url"]

_FALLBACKS = {
    "instagram": instagram.download,
    "pinterest": pinterest.download,
}


def download_media(url: str) -> tuple[str, str]:
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    try:
        return ytdlp.download(url)
    except (DownloadFailed, MediaTooLarge):
        raise
    except Exception as exc:
        fallback = _FALLBACKS.get(platform_of(url))
        if fallback is None:
            raise DownloadFailed(str(exc)) from exc
        return fallback(url)
