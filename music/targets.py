from __future__ import annotations

import re
from collections.abc import Callable
from urllib.parse import quote, quote_plus

import httpx


_TITLE_NOISE_RE = re.compile(r"\s*[(\[].*?[)\]]|\s+-\s+.*$")


def find_links(client: httpx.Client, artist: str, title: str) -> dict[str, str]:
    query = f"{artist.split(',')[0]} {_TITLE_NOISE_RE.sub('', title)}"
    links = {
        "Spotify": f"https://open.spotify.com/search/{quote(query)}",
        "Apple Music": _try(_apple_music, client, query),
        "YouTube Music": f"https://music.youtube.com/search?q={quote_plus(query)}",
        "Deezer": _try(_deezer, client, query),
    }
    return {name: url for name, url in links.items() if url}


def _try(search: Callable[[httpx.Client, str], str], client: httpx.Client, query: str) -> str | None:
    try:
        return search(client, query)
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        return None


def _apple_music(client: httpx.Client, query: str) -> str:
    params = {"term": query, "entity": "song", "limit": 1, "country": "UA"}
    track = client.get("https://itunes.apple.com/search", params=params).json()["results"][0]
    return re.sub(r"[?&]uo=\d+", "", track["trackViewUrl"])


def _deezer(client: httpx.Client, query: str) -> str:
    response = client.get("https://api.deezer.com/search", params={"q": query, "limit": 1})
    return response.json()["data"][0]["link"]
