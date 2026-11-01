from __future__ import annotations

import asyncio
import logging

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import LinkPreviewOptions, Message

from music import fetch_song, find_music_url

logger = logging.getLogger("mediasaver-bot")

router = Router()


def has_music_link(message: Message) -> bool:
    return find_music_url(message.text) is not None


@router.message(has_music_link)
async def handle_music_link(message: Message) -> None:
    url = find_music_url(message.text)
    if url is None:
        return
    logger.info("Music request: %s", url)

    try:
        song = await asyncio.to_thread(fetch_song, url)
    except Exception:
        logger.exception("Failed to recognize song %s", url)
        await message.reply("Couldn't recognize this song.")
        return

    await message.reply(
        song.caption,
        parse_mode=ParseMode.HTML,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
