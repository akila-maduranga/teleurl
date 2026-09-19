# 🤖 Telegram URL Uploader Bot

Upload files up to **2 GB** to Telegram from any URL — including Instagram, TikTok, Twitter/X and 700+ more platforms. Built with [Pyrogram](https://docs.pyrogram.org/) (MTProto) for large file support.

> **Now deployable on Render free tier!** This fork adds full Render compatibility, fixes several bugs, and makes heavy services (Playwright, Node.js PO token server, aria2c) optional so the bot fits in 512 MB RAM.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📱 Telegram Mini App | Modern web interface for link scanning, quality selection, and progress tracking |
| 📤 Direct URL Upload | Send any direct download URL — bot downloads & uploads |
| 📺 yt-dlp Integration | Download from Instagram, TikTok, Twitter/X, Reddit, Facebook, Vimeo + 700 more |
| ✏️ File Renaming | Bot asks for a new filename before every upload |
| 🎬 Media / Document mode | Choose to send as streamable video or raw document |
| 🎵 Audio Extraction | Extract high-quality audio tracks directly from video links |
| 🎞️ Auto Thumbnail | ffmpeg auto-generates thumbnail from video frame |
| ⏱️ Video Metadata | ffprobe extracts duration, width, height for proper Telegram video display |
| 🌊 HLS / DASH streams | `.m3u8`, `.mpd`, `.ts` streamed via ffmpeg → saved as `.mp4` |
| 💾 Up to 2 GB | Pyrogram MTProto — not the 50 MB Bot API limit |
| 📝 Custom Captions | Per-user saved captions |
| 🖼️ Permanent Thumbnails | Stored as Telegram `file_id` — survive restarts & redeployments |
| 📊 Live Progress | Real-time progress bars in both Bot chat and Web Mini App |
| 📢 Broadcast | Send messages to all users (admin) |
| 🚫 Ban / Unban | User management (admin) |
| 💓 Keep-alive | Built-in self-ping mitigates Render's 15-min inactivity sleep |
| 🐳 Render Blueprint | One-click deploy via `render.yaml` |

---

## 🚀 Deploy to Render (free tier)

### Prerequisites

1. **MongoDB Atlas** free cluster ([create one](https://www.mongodb.com/cloud/atlas/register)) — copy the connection string.
2. **Telegram bot credentials** from [@BotFather](https://t.me/BotFather) (`BOT_TOKEN`) and [my.telegram.org](https://my.telegram.org) (`API_ID`, `API_HASH`).
3. **Your Telegram user ID** (numeric) — message [@userinfobot](https://t.me/userinfobot) to get it.
4. **A private Telegram channel** for upload logs — copy its numeric ID (starts with `-100…`).

### Method A — One-click Blueprint (recommended)

1. Fork this repo to your GitHub account.
2. Go to [Render → New → Blueprint](https://dashboard.render.com/select-blueprint) and pick your forked repo.
3. Render reads `render.yaml` and creates a free Docker web service.
4. In Render's **Environment** tab, fill in the secrets (BOT_TOKEN, API_ID, API_HASH, OWNER_ID, DATABASE_URL, LOG_CHANNEL). Leave the optional toggles at their defaults.
5. Deploy. Render assigns a URL like `https://telegram-url-uploader-xxxx.onrender.com` and auto-injects it as `RENDER_EXTERNAL_URL` — the bot picks it up automatically, so **no manual `WEBAPP_URL` setup is needed**.
6. The Mini App launch button in `/start` will work on the very first deploy. ✅

### Method B — Manual web service

1. Fork the repo.
2. Render → **New +** → **Web Service** → pick the repo.
3. **Runtime:** Docker. **Plan:** Free.
4. **Health Check Path:** `/health`.
5. Add env vars (see `.env.example`). `WEBAPP_URL` is optional — Render auto-injects `RENDER_EXTERNAL_URL`.
6. Deploy. The Mini App launch button works immediately.

### What's enabled by default?

To fit within Render's **512 MB RAM** free-tier limit, the following heavy services are **OFF** by default and can be toggled via env vars:

| Env var | Default | Effect |
|---|---|---|
| `ENABLE_PLAYWRIGHT` | `false` | Headless Chromium for sniffing direct media URLs from pages that don't expose them via yt-dlp |
| `ENABLE_PO_TOKEN_SERVER` | `false` | Node.js server for YouTube PO token generation (only needed if you ever allow YouTube — disabled in code) |
| `ENABLE_ARIA2` | `false` | aria2c RPC daemon for fast multi-connection direct downloads |
| `KEEP_ALIVE_INTERVAL` | `600` | Self-pings `/health` every 10 min to mitigate Render's 15-min inactivity sleep |

With all of the above disabled, the bot still works for: direct URL uploads, all yt-dlp-supported platforms, ffmpeg HLS/DASH, and the Mini App.

To enable Playwright + Chromium on a paid Render plan: edit `render.yaml` → set `ENABLE_PLAYWRIGHT=true` and add Docker Build Arg `BUILD_CHROMIUM=1` in Render dashboard.

---

## 🐳 Local Setup

```bash
git clone https://github.com/akilaramal69-beep/new-uploader.git
cd new-uploader

cp .env.example .env
# Fill in BOT_TOKEN, API_ID, API_HASH, OWNER_ID, DATABASE_URL, LOG_CHANNEL
# Set WEBAPP_URL=http://localhost:8080 for local testing

# System deps (Debian/Ubuntu)
sudo apt-get install -y ffmpeg aria2

pip install -r requirements.txt
python bot.py
```

Open http://localhost:8080 in a browser to test the Mini App.

> **Requires:** `ffmpeg` + `ffprobe` installed system-wide. `aria2` is optional. `playwright` is optional.

---

## 🐛 Bug Fixes in This Fork

This fork fixes the following bugs found in the upstream repo:

1. **Hardcoded port `8080`** in `app.py` and `bot.py` — now uses `PORT` env var (Render injects this automatically).
2. **Hardcoded Koyeb URL** (`swift-vilhelmina-akila-10dce4a8.koyeb.app`) in 3 places in `commands.py` — now driven by `WEBAPP_URL` env var.
3. **Route-ordering bug** in `app.py`: the catch-all `GET /{path:path}` was registered **before** the `/api/*` and `/grab` routes, which in many Starlette versions would shadow them. Now correctly registered LAST.
4. **`app.js` null-safety**: `data.action.startsWith("Error:")` would throw if `action` was `null`/`undefined`. Now properly normalized with fallbacks; `HapticFeedback` access also guarded.
5. **Missing `.env.example`** file — README referenced it but it didn't exist in the repo. Now added with all env vars documented.
6. **MongoDB cold-start flakiness**: Motor client now configured with `serverSelectionTimeoutMS=15000` and `connectTimeoutMS=10000` so Render free-tier cold starts (which can take 10–15 s for the first MongoDB Atlas connection) don't fail.
7. **Health endpoint too strict**: previously returned 503 during startup, causing Render's deploy probe to time out and roll back. Now returns 200 immediately, with a `ready` boolean in the body for diagnostics.
8. **Stale Flask references** in comments — the codebase actually uses FastAPI. Comments fixed.
9. **`aria2p` module-level client construction**: previously created a TCP connection at import time, which crashed the bot if `aria2c` wasn't running. Now lazily constructed via `get_aria2()` and gated behind `ENABLE_ARIA2=true`.
10. **Playwright import-time failure**: previously crashed the bot at startup if Playwright wasn't installed. Now lazily loaded only when `ENABLE_PLAYWRIGHT=true` is set.
11. **`asyncio.get_event_loop()` deprecation**: `bot.py` now uses `asyncio.run(main())` instead of the deprecated `loop.run_until_complete(main())` pattern.

---

## 🚀 Bot Commands

```
/start           – Check if bot is alive 🔔
/help            – Show all commands ❓
/about           – Bot info ℹ️
/upload <url>    – Upload file from URL 📤
/skip            – Keep original filename during rename

/caption <text>  – Set custom upload caption 📝
/showcaption     – View your caption
/clearcaption    – Clear caption

/setthumb        – Reply to a photo to set permanent thumbnail 🖼️
/showthumb       – Preview your thumbnail
/delthumb        – Delete thumbnail

--- Admin only ---
/broadcast <msg> – Broadcast to all users 📢
/total           – Total registered users 👥
/ban <id>        – Ban a user ⛔
/unban <id>      – Unban a user ✅
/status          – CPU / RAM / Disk stats + FFmpeg detection 🚀
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` (local dev) or set them in the Render dashboard. Full reference in `.env.example`.

### Required

| Variable | Description |
|---|---|
| `BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) |
| `API_ID` | From [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | From [my.telegram.org](https://my.telegram.org) |
| `OWNER_ID` | Your Telegram user ID (numeric) |
| `DATABASE_URL` | MongoDB connection string (Atlas or local) |
| `LOG_CHANNEL` | Private channel ID for upload logs (negative number) |

### Auto-detected on Render (no action needed)

| Variable | Description |
|---|---|
| `PORT` | Auto-injected by Render; FastAPI binds to it. |
| `WEBAPP_URL` | Auto-detected from Render's `RENDER_EXTERNAL_URL`. Set explicitly only to override. |
| `RENDER` | Set to `true` by Render; enables keep-alive by default. |

### Optional

| Variable | Default | Description |
|---|---|---|
| `BOT_USERNAME` | `UrlUploaderBot` | Bot username (without @) |
| `ADMIN` | _(none)_ | Space-separated extra admin user IDs |
| `BANNED_USERS` | _(none)_ | Space-separated user IDs to block initially |
| `UPDATES_CHANNEL` | _(none)_ | Updates channel username — button shown only if set |
| `SESSION_STRING` | _(none)_ | Pyrogram session string for 4 GB uploads (premium account) |
| `CHUNK_SIZE` | `10240` | Upload chunk size in KB (10 MB default) |
| `COOKIES_FILE` | `cookies.txt` | Path to your cookies file |
| `ALLOW_BOT_URL_UPLOAD` | `True` | Allow bot to process URLs directly in chat |
| `ADSGRAM_BLOCK_ID` | `int-23574` | Adsgram Block ID for Mini App monetization |

### Advanced / Deployment

| Variable | Default | Description |
|---|---|---|
| `COOKIES_DATA` | _(none)_ | Paste full `cookies.txt` content for cloud environments |
| `PROXY` | _(none)_ | Proxy URL: `http://user:pass@host:port` or `socks5://...` |
| `FFMPEG_PATH` | `ffmpeg` | Path to FFmpeg executable |
| `COBALT_API_URL` | _(see config)_ | Cobalt API endpoint for fallback |
| `LINK_API_URL` | _(see config)_ | Link Grabber API endpoint |
| `KEEP_ALIVE_INTERVAL` | `600` | Self-ping interval (seconds). `0` = disable. |

### Render free-tier RAM savers

| Variable | Default | Description |
|---|---|---|
| `ENABLE_PLAYWRIGHT` | `false` | Enable headless Chromium browser interception |
| `ENABLE_PO_TOKEN_SERVER` | `false` | Enable Node.js PO token server (needs Docker `BUILD_NODE=1`) |
| `ENABLE_ARIA2` | `false` | Enable aria2c RPC daemon for fast downloads |

---

## 📁 Project Structure

```
new-uploader/
├── bot.py                  # Entrypoint: Initializer & Lifecycle Manager
├── app.py                  # FastAPI Web Controller & Mini App API
├── requirements.txt
├── Dockerfile              # Render-optimized (Playwright/Node optional via BUILD_*)
├── render.yaml             # Render Blueprint for one-click deploy
├── .env.example            # Full env var reference
├── utils/
│   └── shared.py           # Unified State Singleton (Client & Progress)
├── web/                    # Mini App Frontend Assets (HTML/CSS/JS)
└── plugins/
    ├── config.py           # Environment Variable Management + Render knobs
    ├── commands.py         # Bot Handlers & WebApp Bridge Logic
    ├── admin.py            # Admin Dashboard (Broadcast, Stats)
    └── helper/
        ├── upload.py       # Core Execution Engine (yt-dlp/ffmpeg/aiohttp)
        ├── database.py     # MongoDB Persistence Layer (with cold-start retry)
        ├── extractor.py    # Link-API orchestrator
        └── browser_extractor.py  # Playwright-based media URL sniffer (optional)
```

---

## 🌐 Supported Platforms (yt-dlp)

Instagram · TikTok · Twitter / X · Facebook · Reddit · Vimeo · Dailymotion · Twitch · SoundCloud · Bilibili · Rumble · Odysee · Streamable · Mixcloud · Pinterest + [700 more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

> **YouTube is intentionally blocked** (see `app.py` and `commands.py`). This is by design to keep the bot's ToS-compliant.

---

## 💓 Keep-alive strategy

Render free-tier web services sleep after 15 minutes of inactivity. When a request hits a sleeping service, it cold-starts (10–30 s).

This fork includes a built-in self-ping loop (`KEEP_ALIVE_INTERVAL=600` by default) that hits `/health` every 10 minutes, which is enough to prevent the sleep. **Trade-off:** this consumes the 750 free hours per month quickly (~750 ÷ 1 instance running 24/7 = exactly enough).

To disable self-ping (e.g. if you only want the bot online during specific hours), set `KEEP_ALIVE_INTERVAL=0`.

**Alternative:** use a free external monitor like [UptimeRobot](https://uptimerobot.com/) (5-min HTTP checks) instead of self-pinging.

---

## 💰 Monetization (Adsgram)

The Mini App is integrated with [Adsgram](https://adsgram.ai) to display interstitial video ads before files are queued, allowing you to easily monetize your bot's web traffic.

To configure your own ad revenue stream:

1. Create an account on Adsgram and generate a new **Interstitial** Block.
2. Copy your unique Block ID (e.g., `int-98765`).
3. Set the `ADSGRAM_BLOCK_ID` environment variable in Render (or your `.env` file) to your new Block ID.
4. Restart the bot. The Mini App will automatically begin using your block ID to serve ads.

---

## 📝 Notes

- **Unified State**: The bot and web app share a single runtime state via `utils/shared.py`, ensuring a 0% progress lag and preventing "split-brain" issues.
- **Dual-engine downloads**: yt-dlp is tried first; if it fails, the bot can auto-retry via direct HTTP, Playwright (if enabled), or the cobalt API.
- **Startup validation**: The bot checks for required env vars (`BOT_TOKEN`, `API_ID`, `API_HASH`) and exits with a clear error if any are missing.
- **2 GB limit** via Pyrogram's MTProto API. The standard HTTP Bot API caps at 50 MB.
- **4 GB uploads** (Telegram Premium) require a `SESSION_STRING` of a premium account.
- **yt-dlp format selection** is adaptive: best quality streams + ffmpeg merge when available; pre-merged fallback without it.
- **HLS/DASH streams** (`.m3u8`, `.mpd`, `.ts`) are downloaded and remuxed to `.mp4` via ffmpeg.
- Files are downloaded to `./DOWNLOADS/` and deleted immediately after upload.
- **Filename safety**: Filenames are capped at 80 characters and sanitized for all filesystems.
- Thumbnails are stored as Telegram `file_id` strings in MongoDB — no local files needed.
