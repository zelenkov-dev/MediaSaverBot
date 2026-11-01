from __future__ import annotations

import json
import re

import httpx

from downloader.common import BROWSER_UA

from .listing import Listing

MAX_PHOTOS = 5

_LISTING_RE = re.compile(r"auto\.ria\.com/(?:[a-z]{2}/)?auto_[\w-]+_\d+\.html", re.IGNORECASE)
_LD_JSON_RE = re.compile(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
_GALLERY_RE = re.compile(r'aria-label="Gallery".*?</section>', re.S)
_PHOTO_RE = re.compile(r"photosnew/auto/photo/([a-z0-9_-]+)__(\d+)")
_PHOTO_URL = "https://cdn0.riastatic.com/photosnew/auto/photo/{slug}__{photo_id}hd.jpg"

_PAGE_SPECS = (
    ("⛽", "descEngineEngine"),
    ("⚙️", "descTransmissionTransmission"),
    ("🛞", "descDriveTypeDriveType"),
    ("🎨", "descColorColor"),
)


def matches(url: str) -> bool:
    return bool(_LISTING_RE.search(url))


def fetch(url: str) -> Listing:
    headers = {"User-Agent": BROWSER_UA}
    with httpx.Client(follow_redirects=True, timeout=30, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
        page = response.text
        vehicle = _vehicle(page)
        return Listing(
            title=vehicle["name"],
            price=_price(vehicle.get("offers") or {}),
            url=vehicle.get("url") or url,
            specs=_specs(vehicle, page),
            photos=_photos(client, page),
        )


def _vehicle(page: str) -> dict:
    for block in _LD_JSON_RE.findall(page):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "Vehicle" and data.get("name"):
            return data
    raise ValueError("listing data not found on the page")


def _price(offer: dict) -> str:
    price, currency = offer.get("price"), offer.get("priceCurrency", "")
    if not price:
        return "price on request"
    amount = _spaced(price)
    return f"${amount}" if currency == "USD" else f"{amount} {currency}"


def _specs(vehicle: dict, page: str) -> list[str]:
    specs = []
    mileage = (vehicle.get("mileageFromOdometer") or {}).get("value")
    if mileage is not None:
        specs.append(f"📏 {_spaced(mileage)} km")
    for emoji, block_id in _PAGE_SPECS:
        value = _page_text(page, block_id)
        if value:
            specs.append(f"{emoji} {value}")
    return specs


def _page_text(page: str, block_id: str) -> str | None:
    match = re.search(rf'"id":"{block_id}"[^\]]*?"content":"((?:[^"\\]|\\.)*)"', page)
    return json.loads(f'"{match.group(1)}"') if match else None


def _photos(client: httpx.Client, page: str) -> list[bytes]:
    gallery = _GALLERY_RE.search(page)
    if not gallery:
        return []
    photo_ids = list(dict.fromkeys(_PHOTO_RE.findall(gallery.group(0))))[:MAX_PHOTOS]
    photos = []
    for slug, photo_id in photo_ids:
        response = client.get(_PHOTO_URL.format(slug=slug, photo_id=photo_id))
        if response.is_success:
            photos.append(response.content)
    return photos


def _spaced(number: int | float | str) -> str:
    return f"{int(number):,}".replace(",", " ")
