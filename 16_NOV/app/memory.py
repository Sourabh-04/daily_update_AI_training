import json

import redis

from app import config

r = redis.Redis.from_url(config.REDIS_URL, decode_responses=True)


def _key(session_id: str) -> str:
    return f"chat:{session_id}"          # one key per session -> isolation


def get_history(session_id: str) -> list[dict]:
    """Return past messages as [{"role": "user"/"assistant", "content": "..."}]."""
    return [json.loads(m) for m in r.lrange(_key(session_id), 0, -1)]


def add_turn(session_id: str, question: str, answer: str) -> None:
    key = _key(session_id)
    r.rpush(key,
            json.dumps({"role": "user", "content": question}),
            json.dumps({"role": "assistant", "content": answer}))
    r.ltrim(key, -config.SESSION_MAX_MESSAGES, -1)   # keep only the last N messages
    r.expire(key, config.SESSION_TTL_SECONDS)        # auto-delete idle sessions
