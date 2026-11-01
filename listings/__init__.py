from __future__ import annotations

from downloader.links import iter_urls

from . import autoria
from .listing import Listing

__all__ = ["Listing", "fetch_listing", "find_listing_url"]


def find_listing_url(text: str | None) -> str | None:
    return next((url for url in iter_urls(text) if autoria.matches(url)), None)


def fetch_listing(url: str) -> Listing:
    return autoria.fetch(url)
