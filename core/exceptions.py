from fastapi import HTTPException

class ScraperException(HTTPException):
    """
    Exception raised for errors occurring during scraping operations.
    Args:
        detail (str): Detailed error message.
    """
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Scraper error: {detail}")

class DatabaseException(HTTPException):
    """
    Exception raised for database-related errors.
    Args:
        detail (str): Detailed error message.
    """
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Database error: {detail}")

class RateLimitException(HTTPException):
    """
    Exception raised when the rate limit is exceeded.
    Args:
        detail (str): Detailed error message, defaults to a standard rate-limit exceeded message.
    """
    def __init__(self, detail: str = "You have sent too many requests. Please try again later."):
        super().__init__(status_code=429, detail=detail)