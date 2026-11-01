from __future__ import annotations

import asyncio
import logging

from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.types import FSInputFile, Message

from downloader import (
    DownloadFailed,
    MediaTooLarge,
    UnsupportedMedia,
    cleanup,
    download_media,
    explain,
    find_media_url,
)

logger = logging.getLogger("mediasaver-bot")

router = Router()


def has_media_link(message: Message) -> bool:
    return find_media_url(message.text) is not None


@router.message(has_media_link)
async def handle_media_link(message: Message) -> None:
    url = find_media_url(message.text)
    if url is None:
        return
    logger.info("Media request: %s", url)

    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    try:
        path, kind, caption = await asyncio.to_thread(download_media, url)
    except MediaTooLarge:
        await message.reply("The file exceeds Telegram's 50 MB limit.")
        return
    except UnsupportedMedia as exc:
        await message.reply(str(exc))
        return
    except DownloadFailed as exc:
        reason = explain(str(exc), url)
        if reason:
            logger.warning("Failed to download %s: %s | %s", url, reason, str(exc).splitlines()[0])
        else:
            logger.exception("Failed to download %s", url)
        await message.reply(reason or "Couldn't download media from this link.")
        return

    try:
        media = FSInputFile(path)
        if kind == "photo":
            await message.reply_photo(media, caption=caption)
        elif kind == "document":
            await message.reply_document(media, caption=caption)
        else:
            await message.reply_video(media, caption=caption)
    except Exception:
        logger.exception("Failed to send media to Telegram")
        await message.reply("The media was downloaded but couldn't be sent to the chat.")
    finally:
        cleanup(path)
