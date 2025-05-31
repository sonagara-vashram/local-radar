import hmac
import hashlib
import time
from fastapi import Request, HTTPException, status
from core.logging import logger
from typing import Any
from config.config import settings

# For demonstration, a static dictionary of valid API keys and their secrets.
# Consider moving these to secure environment variables or a secrets manager for production.
VALID_API_KEYS: dict[str, str] = {
    "secure_api_key": settings.SECURE_API
}

# Allowed time drift (in seconds) to prevent replay attacks (e.g., 5 minutes)
ALLOWED_TIME_DRIFT: int = 300

async def validate_api_key(request: Request) -> bool:
    """
    Validate API key headers in the incoming request.
    
    The function checks for the presence of X-API-KEY, X-Signature, and X-Timestamp headers.
    It verifies that the API key exists, that the timestamp is valid, and that the provided
    signature matches the computed HMAC-SHA256 signature based on the request method, URL path, and timestamp.
    Returns:
        bool: True if the API key validation is successful.
    Raises:
        HTTPException: If any validation step fails.
    """
    try:
        api_key: Any = request.headers.get("X-API-KEY")
        signature: Any = request.headers.get("X-Signature")
        timestamp: Any = request.headers.get("X-Timestamp")

        if not api_key or not signature or not timestamp:
            logger.warning("Missing authentication headers in API key validation.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication headers"
            ) from None

        secret: Any = VALID_API_KEYS.get(api_key)
        if not secret:
            logger.warning(f"Invalid API Key provided: {api_key}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key"
            ) from None

        try:
            request_time: int = int(timestamp)
        except ValueError:
            logger.error("Invalid timestamp format in API key validation.", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid timestamp format"
            ) from None

        current_time: int = int(time.time())
        if abs(current_time - request_time) > ALLOWED_TIME_DRIFT:
            logger.warning("Timestamp drift too large in API key validation.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Timestamp is too old or too far in the future"
            ) from None

        # Prepare data to sign
        data_to_sign: bytes = f"{request.method}{request.url.path}{timestamp}".encode()
        computed_signature: str = hmac.new(secret.encode(), data_to_sign, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(computed_signature, signature):
            logger.warning("Invalid signature in API key validation.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            ) from None

        logger.info("API key validation successful.")
        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in API key validation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during API key validation"
        ) from None