from __future__ import annotations

import asyncio
import logging

from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile, InputMediaPhoto, Message

from listings import Listing, fetch_listing, find_listing_url

logger = logging.getLogger("mediasaver-bot")

router = Router()


def has_listing_link(message: Message) -> bool:
    return find_listing_url(message.text) is not None


@router.message(has_listing_link)
async def handle_listing_link(message: Message) -> None:
    url = find_listing_url(message.text)
    if url is None:
        return
    logger.info("Listing request: %s", url)

    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

    try:
        listing = await asyncio.to_thread(fetch_listing, url)
        await _send(message, listing)
    except Exception:
        logger.exception("Failed to load listing %s", url)
        await message.reply("Couldn't load this listing.")


async def _send(message: Message, listing: Listing) -> None:
    photos = [BufferedInputFile(data, f"photo{i}.jpg") for i, data in enumerate(listing.photos)]
    if not photos:
        await message.reply(listing.caption)
    elif len(photos) == 1:
        await message.reply_photo(photos[0], caption=listing.caption)
    else:
        captions = [listing.caption] + [None] * (len(photos) - 1)
        album = [InputMediaPhoto(media=p, caption=c) for p, c in zip(photos, captions)]
        await message.reply_media_group(album)
