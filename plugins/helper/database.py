import motor.motor_asyncio
from plugins.config import Config

_client = None
_db = None
_connect_attempts = 0
_MAX_CONNECT_ATTEMPTS = 3


def get_db():
    """
    Return the cached Motor database handle, creating the client if needed.
    On Render free tier, the first connection after a cold start may take a
    few seconds; we let Motor handle this lazily (it retries on first op).
    """
    global _client, _db
    if _db is None and Config.DATABASE_URL:
        try:
            _client = motor.motor_asyncio.AsyncIOMotorClient(
                Config.DATABASE_URL,
                serverSelectionTimeoutMS=15000,  # 15s for cold-start Atlas
                connectTimeoutMS=10000,
                retryWrites=True,
            )
            _db = _client["url_uploader"]
        except Exception as e:
            Config.LOGGER.error(f"MongoDB client init failed: {e}")
            _client = None
            _db = None
    return _db


async def ping_db() -> bool:
    """Quick liveness check — used by /health if we ever want to expose it."""
    db = get_db()
    if db is None:
        return False
    try:
        await db.command("ping")
        return True
    except Exception:
        return False


async def add_user(user_id: int, username: str | None = None) -> None:
    db = get_db()
    if db is None:
        return
    await db.users.update_one(
        {"_id": user_id},
        {"$setOnInsert": {"_id": user_id, "username": username, "banned": False, "caption": "", "thumb": None}},
        upsert=True,
    )


async def get_user(user_id: int) -> dict | None:
    db = get_db()
    if db is None:
        return None
    return await db.users.find_one({"_id": user_id})


async def update_user(user_id: int, data: dict) -> None:
    db = get_db()
    if db is None:
        return
    await db.users.update_one({"_id": user_id}, {"$set": data}, upsert=True)


async def get_all_users() -> list[dict]:
    db = get_db()
    if db is None:
        return []
    return await db.users.find({}).to_list(length=None)


async def total_users_count() -> int:
    db = get_db()
    if db is None:
        return 0
    return await db.users.count_documents({})


async def is_banned(user_id: int) -> bool:
    user = await get_user(user_id)
    return bool(user and user.get("banned"))


async def ban_user(user_id: int) -> None:
    await update_user(user_id, {"banned": True})


async def unban_user(user_id: int) -> None:
    await update_user(user_id, {"banned": False})
