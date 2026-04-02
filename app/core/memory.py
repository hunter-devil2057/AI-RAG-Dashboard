import redis
import json
from typing import List, Dict
from app.core.config import settings

class ChatMemory:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.use_redis = True
        self._memory_fallback = {} # In-memory fallback if Redis is unreachable
        self.ttl = 3600 # 1 hour expiry
        
        try:
            self.redis.ping()
            print(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            print(f"Redis unreachable ({e}). Falling back to in-memory history.")
            self.use_redis = False

    def add_message(self, session_id: str, role: str, content: str):
        message = {"role": role, "content": content}
        if self.use_redis:
            key = f"chat_history:{session_id}"
            self.redis.rpush(key, json.dumps(message))
            self.redis.expire(key, self.ttl)
        else:
            if session_id not in self._memory_fallback:
                self._memory_fallback[session_id] = []
            self._memory_fallback[session_id].append(message)

    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        if self.use_redis:
            key = f"chat_history:{session_id}"
            messages = self.redis.lrange(key, -limit, -1)
            return [json.loads(m) for m in messages]
        else:
            history = self._memory_fallback.get(session_id, [])
            return history[-limit:]

    def clear(self, session_id: str):
        if self.use_redis:
            key = f"chat_history:{session_id}"
            self.redis.delete(key)
        else:
            if session_id in self._memory_fallback:
                del self._memory_fallback[session_id]

chat_memory = ChatMemory()
