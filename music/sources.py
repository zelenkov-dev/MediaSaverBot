from __future__ import annotations

import json
import re

import httpx
from yt_dlp import YoutubeDL

from downloader import ytdlp

_SOURCES = (
    ("Spotify", re.compile(r"open\.spotify\.com/(?:intl-[a-z-]+/)?track/(\w+)")),
    ("Apple Music", re.compile(r"music\.apple\.com/.*?(?:[?&]i=|/song/[^/?]+/)(\d+)")),
    ("Deezer", re.compile(r"deezer\.com/(?:[a-z]{2}/)?track/(\d+)")),
    ("YouTube Music", re.compile(r"music\.youtube\.com/watch\?(?:.*&)?v=([\w-]+)")),
)

_NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)


def match(url: str) -> tuple[str, str] | None:
    for source, pattern in _SOURCES:
        found = pattern.search(url)
        if found:
            return source, found.group(1)
    return None


def identify(client: httpx.Client, source: str, item_id: str) -> tuple[str, str]:
    return _RESOLVERS[source](client, item_id)


def _spotify(client: httpx.Client, track_id: str) -> tuple[str, str]:
    page = client.get(f"https://open.spotify.com/embed/track/{track_id}").text
    data = json.loads(_NEXT_DATA_RE.search(page).group(1))
    track = data["props"]["pageProps"]["state"]["data"]["entity"]
    return ", ".join(artist["name"] for artist in track["artists"]), track["name"]


def _apple_music(client: httpx.Client, track_id: str) -> tuple[str, str]:
    track = client.get("https://itunes.apple.com/lookup", params={"id": track_id}).json()["results"][0]
    return track["artistName"], track["trackName"]


def _deezer(client: httpx.Client, track_id: str) -> tuple[str, str]:
    track = client.get(f"https://api.deezer.com/track/{track_id}").json()
    return track["artist"]["name"], track["title"]


def _youtube_music(client: httpx.Client, video_id: str) -> tuple[str, str]:
    with YoutubeDL(ytdlp.options()) as ydl:
        url = f"https://music.youtube.com/watch?v={video_id}"
        info = ydl.extract_info(url, download=False, process=False)
    artists = info.get("artists") or [info.get("uploader") or ""]
    return ", ".join(artists), info.get("track") or info["title"]


_RESOLVERS = {
    "Spotify": _spotify,
    "Apple Music": _apple_music,
    "Deezer": _deezer,
    "YouTube Music": _youtube_music,
}
