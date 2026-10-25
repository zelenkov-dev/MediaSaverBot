from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ChatAction
from aiogram.types import FSInputFile, Message

from config import BOT_TOKEN
from downloader import DownloadFailed, MediaTooLarge, cleanup, download_media, find_media_url

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
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
        path, kind = await asyncio.to_thread(download_media, url)
    except MediaTooLarge:
        await message.reply("The file exceeds Telegram's 50 MB limit.")
        return
    except DownloadFailed:
        logger.exception("Failed to download %s", url)
        await message.reply("Couldn't download media from this link.")
        return

    try:
        media = FSInputFile(path)
        if kind == "photo":
            await message.reply_photo(media)
        elif kind == "document":
            await message.reply_document(media)
        else:
            await message.reply_video(media)
    except Exception:
        logger.exception("Failed to send media to Telegram")
        await message.reply("The media was downloaded but couldn't be sent to the chat.")
    finally:
        cleanup(path)


async def main() -> None:
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    me = await bot.get_me()
    logger.info("Bot @%s started. Press Ctrl+C to stop.", me.username)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
