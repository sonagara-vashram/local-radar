import redis
import json
from datetime import datetime
from config.config import settings
from core.logging import logger
from typing import Any, Union

# Initialize Redis client with connection parameters from settings.
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        ssl=settings.REDIS_SSL,
        decode_responses=True  # Automatically decode stored strings
    )
    logger.info("Connected to Redis successfully.")
except Exception as e:
    logger.error("Failed to connect to Redis", exc_info=True)
    raise e from None

def json_serializer(obj: Any) -> str:
    """
    Serialize datetime objects into an ISO format string before JSON dumping.
    Args:
        obj (Any): Object to be serialized.
    Returns:
        str: ISO formatted string if the object is a datetime.
    Raises:
        TypeError: If the object is not JSON serializable.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not JSON serializable") from None

def json_deserializer(obj: Union[list, dict]) -> Union[list, dict]:
    """
    Deserialize JSON-loaded data by converting string timestamps in 'last_updated'
    fields back to datetime objects.
    Args:
        obj (Union[list, dict]): The data structure (list or dict) containing
                                timestamp strings.
    Returns:
        Union[list, dict]: The data with 'last_updated' fields converted to datetime.
    """
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict) and "last_updated" in item and isinstance(item["last_updated"], str):
                try:
                    item["last_updated"] = datetime.fromisoformat(item["last_updated"])
                except Exception as e:
                    logger.error(f"Error deserializing datetime: {e}", exc_info=True)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if key == "last_updated" and isinstance(value, str):
                try:
                    obj[key] = datetime.fromisoformat(value)
                except Exception as e:
                    logger.error(f"Error deserializing datetime for key '{key}': {e}", exc_info=True)
    return obj

def set_cache(key: str, value: list, ttl: int = 3600) -> None:
    """
    Cache the provided data in Redis with a specified TTL (time-to-live).
    The data is serialized as JSON before storing.
    Args:
        key (str): The Redis key under which the data will be stored.
        value (list): The data to be cached.
        ttl (int, optional): Time-to-live in seconds. Defaults to 3600 seconds.
    """
    try:
        serialized_data = json.dumps(value, default=json_serializer)
        redis_client.setex(key, ttl, serialized_data)
        logger.info(f"Cache set for key: {key} with TTL: {ttl} seconds.")
    except Exception as e:
        logger.error(f"Error setting cache for key {key}: {e}", exc_info=True)

def get_cache(key: str) -> Any:
    """
    Retrieve cached data from Redis and deserialize it.
    Args:
        key (str): The Redis key from which data is retrieved.
    Returns:
        Any: The deserialized data if available, otherwise None.
    """
    try:
        cached_data = redis_client.get(key)
        if cached_data:
            data = json.loads(cached_data)
            logger.info(f"Cache hit for key: {key}")
            return json_deserializer(data)
        else:
            logger.info(f"Cache miss for key: {key}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving cache for key {key}: {e}", exc_info=True)
        return None