from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Listing:
    title: str
    price: str
    url: str
    specs: list[str] = field(default_factory=list)
    photos: list[bytes] = field(default_factory=list)

    @property
    def caption(self) -> str:
        return "\n".join([f"🚗 {self.title}", f"💰 {self.price}", *self.specs, f"🔗 {self.url}"])
