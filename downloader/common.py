from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

from .errors import MediaTooLarge

TELEGRAM_VIDEO_LIMIT = 50 * 1024 * 1024
TELEGRAM_PHOTO_LIMIT = 10 * 1024 * 1024

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic"}

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def compact_json(data: dict) -> str:
    return json.dumps(data, separators=(",", ":"))


def save_stream(client: httpx.Client, media_url: str, path: Path) -> None:
    with client.stream("GET", media_url) as response:
        response.raise_for_status()
        with open(path, "wb") as f:
            for chunk in response.iter_bytes(65536):
                f.write(chunk)


def classify(path: str) -> str:
    if Path(path).suffix.lower() not in IMAGE_EXTS:
        return "video"
    return "photo" if os.path.getsize(path) <= TELEGRAM_PHOTO_LIMIT else "document"


def finalize(path: str | Path, source_url: str) -> tuple[str, str]:
    path = str(path)
    kind = classify(path)
    if kind == "video" and os.path.getsize(path) > TELEGRAM_VIDEO_LIMIT:
        cleanup(path)
        raise MediaTooLarge(source_url)
    return path, kind


def cleanup(path: str | None) -> None:
    if not path:
        return
    try:
        os.remove(path)
    except OSError:
        pass
