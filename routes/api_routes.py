from fastapi import APIRouter, HTTPException, Depends, Request
from enum import Enum
from typing import List
from models.models import ScrapeResponse, ErrorResponse
from services.scraping_service import get_scraped_data
from security.rate_limiter import rate_limit
from core.logging import logger
from models.scrape_request import ScrapeRequest
from security.api_key_validator import validate_api_key
from scrapers.scraper_config import SCRAPER_REQUIRED_PARAMS
import asyncio  # For running blocking calls in a separate thread

router = APIRouter()

class ScraperCategory(str, Enum):
    """
    Enum representing the available scraper categories.
    """
    weather = "weather"
    restaurants = "restaurants"
    hotels = "hotels"
    night_clubs = "night_clubs"
    schools = "schools"
    supermarkets = "supermarkets"
    police_stations = "police_stations"
    fire_stations = "fire_stations"
    gyms = "gyms"
    libraries = "libraries"
    colleges = "colleges"
    naukri = "naukri"
    shine = "shine"
    apna = "apna"
    indiatoday = "indiatoday"

@router.get("/scrapers", response_model=List[str])
def get_scrapers() -> List[str]:
    """
    Retrieve the list of available scrapers.
    This endpoint returns a list of keys corresponding to available scraper modules.
    Args:
        current_user (Dict): The currently authenticated user's payload.
    Returns:
        List[str]: A list of scraper names.
    """
    from scrapers import SCRAPERS
    return list(SCRAPERS.keys())

@router.post("/scrape", response_model=ScrapeResponse, responses={404: {"model": ErrorResponse}})
async def scrape_data(
    request: Request,
    scrape_request: ScrapeRequest,
    # rate_limit_key: str = Depends(rate_limit),
    api_key_valid: bool = Depends(validate_api_key),
) -> ScrapeResponse:
    """
    Endpoint to trigger scraping for a given category and location.
    
    This endpoint validates the request with rate limiting, API key, and user authentication,
    then offloads the blocking scraping operation to a background thread.
    Args:
        request (Request): The incoming HTTP request.
        category (ScraperCategory): The category to scrape.
        location (str): The location for which data is to be scraped.
        rate_limit_key (str): A key to enforce rate limiting.
        api_key_valid (bool): Flag indicating if the API key is valid.
        current_user (Dict): The authenticated user payload.
    Returns:
        ScrapeResponse: A response model containing the scraped data.
    Raises:
        HTTPException: If an error occurs during scraping.
    """
    category = scrape_request.category.lower()
    location = scrape_request.location.lower()
    additional_params = scrape_request.params or {}
    
    # Check if extra parameters are required for this category.
    required = SCRAPER_REQUIRED_PARAMS.get(category, [])
    missing = [param for param in required if param not in additional_params]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required parameters for {category}: {missing}")

    try:
        # Offload the blocking get_scraped_data call to a separate thread
        data = await asyncio.to_thread(get_scraped_data, category, location, **additional_params)
        return {"data": data}
    except Exception as e:
        logger.error(f"Error during scraping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from None