# MediaSaver

A Telegram bot for group chats:

- when someone posts a link to **YouTube Shorts / TikTok / Instagram /
  Pinterest**, it downloads the video or image and sends it straight to the chat;
- when someone posts an **AUTO.RIA** car listing, it replies with an album of
  up to 5 photos, the price and key specs;
- when someone posts a song from **Spotify / Apple Music / YouTube Music /
  Deezer**, it replies with links to the same song on the other services.

## Structure

| File                         | Purpose                                              |
|------------------------------|------------------------------------------------------|
| `bot.py`                     | Entry point: logging and startup                     |
| `config.py`                  | Loads settings from `.env`                           |
| `handlers/media.py`          | Replies to media links with the downloaded file      |
| `handlers/listing.py`        | Replies to listing links with a photo album          |
| `handlers/music.py`          | Replies to song links with links on other services   |
| `music/sources.py`           | Gets artist and title from the shared song link      |
| `music/targets.py`           | Finds the song on Apple Music / Deezer, search links |
| `music/song.py`              | `Song` model and reply format                        |
| `listings/autoria.py`        | Parses an AUTO.RIA listing page (specs and photos)   |
| `listings/listing.py`        | `Listing` model and caption format                   |
| `downloader/__init__.py`     | `download_media()`: yt-dlp first, then fallbacks     |
| `downloader/links.py`        | Finds supported links and detects the platform       |
| `downloader/ytdlp.py`        | Video download via yt-dlp                            |
| `downloader/instagram.py`    | Instagram fallback for photo posts (via yt-dlp)      |
| `downloader/pinterest.py`    | Pinterest fallback (image pins) via public API       |
| `downloader/common.py`       | Shared helpers: file type, size limits, cleanup      |
| `downloader/errors.py`       | `DownloadFailed` / `MediaTooLarge` exceptions        |
| `downloader/reasons.py`      | Turns download errors into a reason users understand |

## Setup

### 1. Create the bot and disable Privacy Mode

1. In [@BotFather](https://t.me/BotFather), run `/newbot` and get the **token**.
2. **Important:** `/mybots` → your bot → *Bot Settings* → *Group Privacy* →
   **Turn off**. Otherwise the bot only sees commands in groups and won't
   react to links.
3. Add the bot to your group.

### 2. `.env` file

Copy `.env.example` to `.env` and fill in your token:

```
BOT_TOKEN=your_token_from_BotFather
```

### 3. Install dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Some videos need **ffmpeg** to merge video and audio streams. The bot
> downloads ready-made mp4 files and usually works without it, but for
> maximum compatibility install ffmpeg and add it to your `PATH`.

### 4. Run

```powershell
python bot.py
```

The bot runs as long as the script is running. Stop it with `Ctrl+C`.

## Deployment (VPS with Docker)

```bash
git clone <your-repo-url> mediasaver && cd mediasaver
cp .env.example .env && nano .env
docker compose up -d --build
docker compose logs -f
```

To update yt-dlp (platforms change often), rebuild without cache:
`docker compose build --no-cache && docker compose up -d`.

## Notes

- **Video size limit is 50 MB** (Telegram Bot API restriction). Larger videos
  are skipped with an error message.
- **Instagram captions:** posts are sent with their original description, cut
  to Telegram's 1024-character caption limit.
- **Instagram:** public photo posts are fetched without login. Videos and
  private/restricted content may require authentication — export a
  `cookies.txt` file (Netscape format) and set its path in `.env` via the
  `COOKIES_FILE` variable.
- Don't commit `.env`, `cookies.txt` or the `downloads/` folder — they are
  already in `.gitignore`.
