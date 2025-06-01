import re
from fastapi import Request, HTTPException, status
from starlette.responses import Response
from core.logging import logger

# Pre-compile banned user agent patterns for efficiency.
# Removed 'postmanruntime' for easier testing with Postman.
BANNED_USER_AGENTS = [
    # re.compile(r"python-requests", re.IGNORECASE),
    # re.compile(r"curl", re.IGNORECASE),
    re.compile(r"wget", re.IGNORECASE),
    re.compile(r"scrapy", re.IGNORECASE),
    re.compile(r"bot", re.IGNORECASE),
]

# List of headers that indicate usage of proxy.
# TEMPORARILY COMMENTED OUT FOR DEPLOYMENT/TESTING ON RENDER
# PROXY_HEADERS = [
#     "X-Forwarded-For",
#     "X-Real-IP",
#     "Via"
# ]

# Additional headers that should be present in legitimate browser requests.
# TEMPORARILY COMMENTED OUT FOR EASIER TESTING
# REQUIRED_HEADERS = [
#     "Accept-Language",
#     "Referer"
# ]

async def header_validator(request: Request, call_next) -> Response:
    """
    Middleware that validates request headers to block suspicious requests.

    Checks include:
      - User-Agent against banned patterns.
      - Presence of proxy-related headers. (TEMPORARILY DISABLED)
      - Presence of additional required headers (e.g., Accept-Language, Referer). (TEMPORARILY DISABLED)

    Args:
        request (Request): The incoming HTTP request.
        call_next: A callable that receives the request and returns a Response.

    Returns:
        Response: The HTTP response from the next middleware or endpoint.

    Raises:
        HTTPException: If any of the validations fail.
    """

    # Validate User-Agent header against banned patterns.
    user_agent = request.headers.get("user-agent", "")
    if any(pattern.search(user_agent) for pattern in BANNED_USER_AGENTS):
        logger.warning(f"Blocked request from banned user agent: {user_agent}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden user agent"
        ) from None

    # Validate User-Agent header for sufficiency.
    # Removed `len(user_agent) < 20` check to allow shorter user agents for testing.
    # 'Mozilla/5.0' ko ab bhi block kiya hai, agar tum ise allow karna chahte ho to hata sakte ho.
    if not user_agent or user_agent == "Mozilla/5.0":
        logger.warning(f"Blocked request due to insufficient User-Agent: '{user_agent}'")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient User-Agent"
        ) from None

    # Validate proxy-related headers.
    # TEMPORARILY COMMENTED OUT. Render jaise services proxy headers use karte hain.
    # Ise uncomment karne se pehle, Render ke proxy setup ko samajhna hoga.
    # for header in PROXY_HEADERS:
    #     if request.headers.get(header):
    #         logger.warning(f"Blocked request due to proxy header '{header}': {request.headers.get(header)}")
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="Access via proxy is not allowed"
    #         ) from None

    # Validate additional required headers.
    # TEMPORARILY COMMENTED OUT. Testing ke dauran in headers ka na hona common hai.
    # for header in REQUIRED_HEADERS:
    #     value = request.headers.get(header)
    #     if not value:
    #         logger.warning(f"Missing required header: {header}")
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=f"Missing required header: {header}"
    #         ) from None

    # Proceed with the next middleware or route handler.
    response = await call_next(request)
    return response