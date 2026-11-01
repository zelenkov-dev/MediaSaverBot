from __future__ import annotations

from dataclasses import dataclass, field
from html import escape


@dataclass
class Song:
    artist: str
    title: str
    links: dict[str, str] = field(default_factory=dict)

    @property
    def caption(self) -> str:
        links = " · ".join(
            f'<a href="{escape(url)}">{escape(name)}</a>' for name, url in self.links.items()
        )
        return f"🎵 <b>{escape(self.artist)} — {escape(self.title)}</b>\n{links}"
