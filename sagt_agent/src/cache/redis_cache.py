import os
import json
from typing import Optional

import redis
from src.utils.agent_logger import get_logger

logger = get_logger("redis_cache")

# 业务缓存统一前缀，避免与 LangGraph 平台自身（checkpointer 等）的 key 冲突
CACHE_PREFIX = "sagt:cache:"

# Redis 连接池（懒初始化，首次使用时创建）
_pool: Optional[redis.ConnectionPool] = None
_client: Optional[redis.Redis] = None
_redis_disabled = False


def _get_client() -> Optional[redis.Redis]:
    """
    返回同步 Redis 客户端（单例 + 连接池）。
    复用 docker-compose 注入的 REDIS_URI 环境变量（langgraph-redis 实例）。
    若 Redis 不可用，返回 None，调用方降级为直查数据库。
    """
    global _pool, _client, _redis_disabled
    if _redis_disabled:
        return None
    if _client is not None:
        return _client

    redis_uri = os.environ.get("REDIS_URI")
    if not redis_uri:
        logger.warning("未配置 REDIS_URI，业务缓存降级为直查（无缓存）")
        _redis_disabled = True
        return None

    try:
        _pool = redis.ConnectionPool.from_url(
            redis_uri,
            decode_responses=True,
            socket_connect_timeout=1.0,
            socket_timeout=1.0,
        )
        _client = redis.Redis(connection_pool=_pool)
        # 探活
        _client.ping()
        logger.info("业务缓存 Redis 客户端初始化成功")
        return _client
    except Exception as e:
        logger.warning(f"业务缓存 Redis 初始化失败，降级为直查：{e}")
        _redis_disabled = True
        _client = None
        return None


def build_key(namespace: str, *parts: str) -> str:
    """构造带前缀的缓存 key，如 sagt:cache:tag_setting:global"""
    return CACHE_PREFIX + namespace + ":" + ":".join(str(p) for p in parts)


def get_json(key: str) -> Optional[dict]:
    """读取缓存，命中返回 dict，未命中/异常返回 None"""
    client = _get_client()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if raw is None:
            return None
        cache_data = json.loads(raw)
        logger.info(f"查询缓存成功,key:{key}, cache_data:{cache_data}")
        return cache_data
    except Exception as e:
        logger.warning(f"读取缓存失败 key={key}: {e}")
        return None


def set_json(key: str, value: dict, ttl: int) -> None:
    """写入缓存，ttl 秒；异常静默忽略（不影响主流程）"""
    client = _get_client()
    if client is None:
        return
    try:
        client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
        logger.info(f"写入缓存成功:key:{key},ttl:{ttl}")
    except Exception as e:
        logger.warning(f"写入缓存失败 key={key}: {e}")


def delete_key(key: str) -> None:
    """删除指定缓存 key"""
    client = _get_client()
    if client is None:
        return
    try:
        client.delete(key)
        logger.info(f"删除缓存成功,key:{key}")
    except Exception as e:
        logger.warning(f"删除缓存失败 key={key}: {e}")
