import redis
import json
import os

redis_cache = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/1"))


def get_from_cached(task_id: str):
    data = redis_cache.get(f"task:{task_id}")
    return json.loads(data) if data else None


def save_to_cache(task_id: str, status: str, result: str = None, error: str = None, ttl: int = 3600):
    cache_data = {
        "status": status,
        "result": result,
        "error": error
    }
    redis_cache.setex(f"task:{task_id}", ttl, json.dumps(cache_data))


def delete_from_cache(task_id: str):
    redis_cache.delete(f"task:{task_id}")