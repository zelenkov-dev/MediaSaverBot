from __future__ import annotations

import httpx

from downloader.common import BROWSER_UA
from downloader.links import iter_urls

from . import sources, targets
from .song import Song

__all__ = ["Song", "fetch_song", "find_music_url"]


def find_music_url(text: str | None) -> str | None:
    return next((url for url in iter_urls(text) if sources.match(url)), None)


def fetch_song(url: str) -> Song:
    source, item_id = sources.match(url)
    headers = {"User-Agent": BROWSER_UA}
    with httpx.Client(follow_redirects=True, timeout=20, headers=headers) as client:
        artist, title = sources.identify(client, source, item_id)
        links = targets.find_links(client, artist, title)
    links[source] = url
    return Song(artist, title, links)
