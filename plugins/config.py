import os
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO,
)


def _str_to_bool(val, default=False):
    if not val:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on", "y")


class Config:
    # ── Telegram ──────────────────────────────────────
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
    API_ID: int = int(os.environ.get("API_ID", 0) or 0)
    API_HASH: str = os.environ.get("API_HASH", "")
    BOT_USERNAME: str = os.environ.get("BOT_USERNAME", "UrlUploaderBot")

    # ── Owner / Admins ────────────────────────────────
    OWNER_ID: int = int(os.environ.get("OWNER_ID", 0) or 0)
    ADMIN: set = set(
        int(x) for x in os.environ.get("ADMIN", "").split() if x.isdigit()
    )
    BANNED_USERS: set = set(
        int(x) for x in os.environ.get("BANNED_USERS", "").split() if x.isdigit()
    )

    # ── Channels ──────────────────────────────────────
    LOG_CHANNEL: int = int(os.environ.get("LOG_CHANNEL", 0) or 0)
    UPDATES_CHANNEL: str = os.environ.get("UPDATES_CHANNEL", "")

    # ── Database ──────────────────────────────────────
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

    # ── File handling ─────────────────────────────────
    DOWNLOAD_LOCATION: str = os.path.abspath(
        os.environ.get("DOWNLOAD_LOCATION", "./DOWNLOADS")
    )
    MAX_FILE_SIZE: int = 2_097_152_000          # ~2 GB (Pyrogram MTProto limit)
    CHUNK_SIZE: int = int(os.environ.get("CHUNK_SIZE", 10240)) * 1024  # KB → bytes

    # ── Misc ──────────────────────────────────────────
    LOGGER = logging
    DEF_WATER_MARK_FILE: str = "@" + BOT_USERNAME
    PROCESS_MAX_TIMEOUT: int = 3600
    SESSION_STRING: str = os.environ.get("SESSION_STRING", "")  # optional premium session for 4 GB
    COOKIES_FILE: str = os.environ.get("COOKIES_FILE", "cookies.txt")
    PROXY: str = os.environ.get("PROXY", "")
    FFMPEG_PATH: str = os.environ.get("FFMPEG_PATH", "ffmpeg")
    SESSION_NAME: str = "url_uploader_bot"

    # ── External API endpoints ────────────────────────
    COBALT_API_URL: str = os.environ.get(
        "COBALT_API_URL", "https://arrogant-karrah-akila-4c42ca1e.koyeb.app"
    )
    LINK_API_URL: str = os.environ.get(
        "LINK_API_URL", "https://native-serene-maduranga11-43790d26.koyeb.app"
    )
    ALLOW_BOT_URL_UPLOAD: bool = _str_to_bool(
        os.environ.get("ALLOW_BOT_URL_UPLOAD", "True"), default=True
    )
    ADSGRAM_BLOCK_ID = os.environ.get("ADSGRAM_BLOCK_ID", "int-23574")

    # ── Render / PaaS deployment knobs ────────────────
    # Render injects PORT; fall back to 8080 for local dev.
    PORT: int = int(os.environ.get("PORT", 8080) or 8080)
    # Public base URL of this deployment (used to build the Telegram WebApp URL).
    # On Render, set this to https://<your-service>.onrender.com
    WEBAPP_URL: str = os.environ.get("WEBAPP_URL", "").rstrip("/")

    # ── Optional heavy services (disabled by default on Render free tier) ──
    # Each of these consumes significant RAM and is not strictly required
    # for the core download/upload flow.
    ENABLE_PLAYWRIGHT: bool = _str_to_bool(
        os.environ.get("ENABLE_PLAYWRIGHT", "false"), default=False
    )
    ENABLE_PO_TOKEN_SERVER: bool = _str_to_bool(
        os.environ.get("ENABLE_PO_TOKEN_SERVER", "false"), default=False
    )
    ENABLE_ARIA2: bool = _str_to_bool(
        os.environ.get("ENABLE_ARIA2", "false"), default=False
    )
    # Self-ping the /health endpoint every N seconds to mitigate Render's
    # 15-minute inactivity sleep. Set KEEP_ALIVE_INTERVAL=0 to disable.
    KEEP_ALIVE_INTERVAL: int = int(os.environ.get("KEEP_ALIVE_INTERVAL", "600") or 0)
