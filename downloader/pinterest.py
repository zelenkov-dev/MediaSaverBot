from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import httpx

from config import DOWNLOAD_DIR

from .common import BROWSER_UA, IMAGE_EXTS, compact_json, finalize, save_stream
from .errors import DownloadFailed, as_download_failed

_PIN_ID_RE = re.compile(r"/pin/(?:[\w-]+--)?(\d+)")
_API_URL = "https://www.pinterest.com/resource/PinResource/get/"


def download(url: str) -> tuple[str, str]:
    headers = {"User-Agent": BROWSER_UA}
    with as_download_failed(), httpx.Client(follow_redirects=True, timeout=30, headers=headers) as client:
        pin_id = _resolve_pin_id(client, url)
        media_url, is_video = _pick_media(_fetch_pin(client, pin_id))
        path = DOWNLOAD_DIR / f"pinterest-{pin_id}{_extension(media_url, is_video)}"
        save_stream(client, media_url, path)
    return finalize(path, url)


def _resolve_pin_id(client: httpx.Client, url: str) -> str:
    match = _PIN_ID_RE.search(url)
    if not match:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            match = _PIN_ID_RE.search(str(response.url))
    if not match:
        raise DownloadFailed("could not determine pin ID")
    return match.group(1)


def _fetch_pin(client: httpx.Client, pin_id: str) -> dict:
    options = {"field_set_key": "unauth_react_main_pin", "id": pin_id}
    response = client.get(
        _API_URL,
        params={"data": compact_json({"options": options})},
        headers={"X-Pinterest-PWS-Handler": "www/[username].js"},
    )
    response.raise_for_status()
    pin = (response.json().get("resource_response") or {}).get("data")
    if not isinstance(pin, dict):
        raise DownloadFailed("Pinterest did not return the pin (private or deleted)")
    return pin


def _pick_media(pin: dict) -> tuple[str, bool]:
    video_url = _best_video(pin.get("videos"))
    if video_url:
        return video_url, True
    image_url = _best_image(_first_slot(pin).get("images"))
    if image_url:
        return image_url, False
    raise DownloadFailed("pin has no downloadable media")


def _best_video(videos: object) -> str | None:
    if not isinstance(videos, dict):
        return None
    formats = [
        f for f in (videos.get("video_list") or {}).values()
        if isinstance(f, dict) and f.get("url") and not f["url"].lower().endswith(".m3u8")
    ]
    return _largest(formats, "height")


def _best_image(images: object) -> str | None:
    if not isinstance(images, dict):
        return None
    original = images.get("orig")
    if isinstance(original, dict) and original.get("url"):
        return original["url"]
    candidates = [i for i in images.values() if isinstance(i, dict) and i.get("url")]
    return _largest(candidates, "width")


def _largest(items: list[dict], size_key: str) -> str | None:
    best = max(items, key=lambda item: item.get(size_key) or 0, default=None)
    return best["url"] if best else None


def _first_slot(pin: dict) -> dict:
    slots = (pin.get("carousel_data") or {}).get("carousel_slots")
    if isinstance(slots, list) and slots and isinstance(slots[0], dict):
        return slots[0]
    return pin


def _extension(media_url: str, is_video: bool) -> str:
    if is_video:
        return ".mp4"
    ext = Path(urlparse(media_url).path).suffix.lower()
    return ext if ext in IMAGE_EXTS else ".jpg"
