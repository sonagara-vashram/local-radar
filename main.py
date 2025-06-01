from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.api_routes import router as api_router
from core.exceptions import ScraperException, DatabaseException, RateLimitException
from core.logging import logger
from middleware.request_logger import log_request
from middleware.header_validator import header_validator

# Initialize FastAPI application with metadata.
app = FastAPI(
    title="Scraper API",
    version="1.0",
    description="API for scraping and retrieving data from various sources."
)

# Register custom middleware.
# The order of middleware registration matters.
app.middleware("http")(header_validator)
app.middleware("http")(log_request)

# Include CORS middleware for handling cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://my-cool-scraper-api.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for various API endpoints
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event() -> None:
    """
    Startup event handler for application initialization.
    Additional startup routines (e.g., connecting to databases) can be added here.
    """
    logger.info("Application startup initiated.")

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Shutdown event handler for application cleanup.
    Resources (e.g., database connections) can be gracefully closed here.
    """
    logger.info("Application shutdown initiated.")

@app.get("/")
async def root() -> dict:
    """
    Root endpoint that returns a welcome message.
    Returns:
        dict: A dictionary with a welcome message.
    """
    return {"message": "Welcome to Scraper API"}

@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint to verify that the API is running.
    Returns:
        dict: A dictionary with the health status.
    """
    return {"status": "healthy"}

# Exception handlers for custom exceptions
@app.exception_handler(ScraperException)
async def scraper_exception_handler(request: Request, exc: ScraperException) -> JSONResponse:
    """
    Handle ScraperException errors.
    Args:
        request (Request): The incoming request.
        exc (ScraperException): The exception instance.
    Returns:
        JSONResponse: A JSON response with the error details.
    """
    logger.error(f"ScraperException: {exc.detail}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    """
    Handle DatabaseException errors.
    Args:
        request (Request): The incoming request.
        exc (DatabaseException): The exception instance.
    Returns:
        JSONResponse: A JSON response with the error details.
    """
    logger.error(f"DatabaseException: {exc.detail}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RateLimitException)
async def rate_limit_exception_handler(request: Request, exc: RateLimitException) -> JSONResponse:
    """
    Handle RateLimitException errors.
    Args:
        request (Request): The incoming request.
        exc (RateLimitException): The exception instance.
    Returns:
        JSONResponse: A JSON response with the error details.
    """
    logger.warning(f"RateLimitException from {request.client.host}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle any unhandled exceptions.
    Args:
        request (Request): The incoming request.
        exc (Exception): The exception instance.
    Returns:
        JSONResponse: A JSON response with a generic error message.
    """
    logger.exception("Unhandled exception occurred:", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please contact support."},
    )