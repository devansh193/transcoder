from upstash_redis import Redis
from app.core.config import settings

redis = Redis.from_env()
