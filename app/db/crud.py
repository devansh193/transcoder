import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import PublicKey
from upstash_redis import Redis
import json
redis = Redis.from_env()

async def get_public_key_by_id(db: AsyncSession, key_id: str):
    cached_key = await redis.get(key_id)
    if cached_key:
        return json.load(cached_key)
    result = await db.execute(
        select(PublicKey).where(PublicKey.id == key_id, PublicKey.is_active == True)
    )
    public_key = result.scalars().first()
    if public_key:
        await redis.set(key_id, json.dump(public_key.dist()), ex=36000)

    return public_key
