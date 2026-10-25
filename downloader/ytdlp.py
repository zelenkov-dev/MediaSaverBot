from __future__ import annotations

import os

from yt_dlp import YoutubeDL

from config import COOKIES_FILE, DOWNLOAD_DIR

from .common import TELEGRAM_VIDEO_LIMIT, finalize
from .errors import DownloadFailed, MediaTooLarge


class _SilentLogger:
    def debug(self, msg: str) -> None:
        pass

    info = warning = error = debug


def options() -> dict:
    options = {
        "format": "best[ext=mp4]/mp4/best",
        "outtmpl": str(DOWNLOAD_DIR / "%(extractor)s-%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": _SilentLogger(),
        "noplaylist": True,
        "max_filesize": TELEGRAM_VIDEO_LIMIT,
        "retries": 3,
        "socket_timeout": 30,
    }
    if COOKIES_FILE:
        options["cookiefile"] = COOKIES_FILE
    return options


def download(url: str) -> tuple[str, str]:
    with YoutubeDL(options()) as ydl:
        info = ydl.extract_info(url, download=True)

    downloads = (info or {}).get("requested_downloads") or []
    if not downloads:
        raise MediaTooLarge(url)

    path = downloads[0].get("filepath")
    if not path or not os.path.exists(path):
        raise DownloadFailed("yt-dlp did not produce a file")
    return finalize(path, url)
