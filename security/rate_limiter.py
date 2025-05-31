import asyncio
import redis
from fastapi import Request
from config.config import settings
from core.exceptions import RateLimitException
from core.logging import logger
from typing import Any

# Redis client setup
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    ssl=settings.REDIS_SSL,
    decode_responses=True
)

class RedisRateLimiter:
    """
    Rate limiter using Redis. Allows limited requests per IP within a time window.
    Blocks IP temporarily or permanently on repeated offenses.
    """

    def __init__(self, calls: int, period: int, block_duration: int = 600,
                 permanent_block_threshold: int = 3, permanent_block_duration: int = 86400) -> None:
        self.calls = calls  # Maximum allowed requests
        self.period = period  # Time window in seconds
        self.block_duration = block_duration  # Temporary block duration
        self.permanent_block_threshold = permanent_block_threshold  # No. of offenses before perm block
        self.permanent_block_duration = permanent_block_duration  # Permanent block duration

    async def __call__(self, request: Request) -> str:
        """
        Enforce rate limiting by tracking request count for an IP.
        Temporarily or permanently blocks IP on repeated violations.
        """
        ip: str = request.client.host
        block_key = f"block:{ip}"
        rate_key = f"rate_limit:{ip}"
        count_key = f"block_count:{ip}"

        # Check if IP is blocked
        is_blocked: Any = await asyncio.to_thread(redis_client.get, block_key)
        if is_blocked:
            logger.warning(f"IP {ip} is currently blocked: {is_blocked}")
            raise RateLimitException(detail="Too many requests. IP blocked.")

        try:
            # Lua script for atomic increment and expiry
            script = """
            local current = redis.call('INCR', KEYS[1])
            if tonumber(current) == 1 then
                redis.call('EXPIRE', KEYS[1], ARGV[1])
            end
            return current
            """
            current = await asyncio.to_thread(redis_client.eval, script, 1, rate_key, self.period)
            logger.info(f"Rate limiter: Current count for IP {ip} is {current}")

            if int(current) > self.calls:
                logger.warning(f"Rate limiter: Limit exceeded for IP {ip}")

                # Increase block count
                block_count = await asyncio.to_thread(redis_client.incr, count_key)
                if block_count == 1:
                    await asyncio.to_thread(redis_client.expire, count_key, self.permanent_block_duration)

                # Apply permanent block if threshold exceeded
                if block_count >= self.permanent_block_threshold:
                    logger.warning(f"IP {ip} reached permanent block threshold.")
                    await asyncio.to_thread(redis_client.setex, block_key, self.permanent_block_duration, "permanent")
                else:
                    await asyncio.to_thread(redis_client.setex, block_key, self.block_duration, "temporary")

                raise RateLimitException(detail="Too many requests. IP blocked.")
        except RateLimitException:
            raise
        except Exception as e:
            logger.error(f"Rate limiter error for IP {ip}: {e}", exc_info=True)
            raise RateLimitException(detail="Rate limit exceeded due to internal error")

        return ip

# Configure rate limiter for 100 requests per 1 minute
rate_limit = RedisRateLimiter(
    calls=100,  # Max 100 requests
    period=60,  # Time window: 1 minute (60 sec)
    block_duration=600,  # Temporary block for 10 minutes
    permanent_block_threshold=3,  # After 3 offenses, permanent block
    permanent_block_duration=86400  # 24-hour permanent block
)
