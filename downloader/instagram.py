from __future__ import annotations

import httpx
from yt_dlp import YoutubeDL

from config import DOWNLOAD_DIR

from . import ytdlp
from .common import BROWSER_UA, Downloaded, finalize, save_stream
from .errors import DownloadFailed, as_download_failed


def download(url: str) -> Downloaded:
    with as_download_failed():
        info = _extract_metadata(url)
        post = _first_entry(info)
        image_url = post.get("thumbnail")
        if not image_url:
            raise DownloadFailed("post has no media")

        path = DOWNLOAD_DIR / f"instagram-{info.get('id')}.jpg"
        headers = {"User-Agent": BROWSER_UA}
        with httpx.Client(follow_redirects=True, timeout=30, headers=headers) as client:
            save_stream(client, image_url, path)
    return finalize(path, url, info.get("description") or post.get("description"))


def _extract_metadata(url: str) -> dict:
    options = {**ytdlp.options(), "ignore_no_formats_error": True}
    with YoutubeDL(options) as ydl:
        return ydl.extract_info(url, download=False) or {}


def _first_entry(info: dict) -> dict:
    return next(iter(info.get("entries") or []), None) or info
