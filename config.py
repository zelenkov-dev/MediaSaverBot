from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
COOKIES_FILE: str | None = os.getenv("COOKIES_FILE", "").strip() or None
DOWNLOAD_DIR = Path(__file__).parent / "downloads"

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set. Copy .env.example to .env and add your token from @BotFather."
    )
