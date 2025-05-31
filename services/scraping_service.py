import datetime
import threading
import json
from typing import List
from scrapers import SCRAPERS
from cache.redis_cache import get_cache, set_cache
from database.mongo import db
from core.exceptions import ScraperException
from core.logging import logger
from tasks.tasks import insert_data_to_db_task

def get_scraped_data(category: str, location: str, **kwargs) -> List[dict]:
    """
    Fetch scraped data from cache, database, or scraper if necessary.
    1. Check Redis cache.
    2. Check MongoDB for data (valid if < 7 days old).
    3. If outdated or absent, scrape fresh data.
    4. Update MongoDB and Redis in the background.
    """
    try:
        category = category.lower()
        location = location.lower()
        today = datetime.datetime.utcnow()
        seven_days_ago = today - datetime.timedelta(days=7)
        
        # Create cache key
        cache_key = f"{category}_{location}"
        if kwargs:
            extra_key = json.dumps(kwargs, sort_keys=True)
            cache_key = f"{cache_key}_{extra_key}"

    except Exception as e:
        logger.error("Error processing input parameters", exc_info=True)
        raise ScraperException(detail="Input processing error") from None

    # Step 1: Check Redis cache
    try:
        cached_data = get_cache(cache_key)
        if cached_data:
            logger.info(f"Returning cached data from Redis for {category} in {location}.")
            return cached_data
    except Exception as e:
        logger.warning("Redis cache retrieval failed", exc_info=True)

    # Step 2: Check MongoDB for existing recent data
    try:
        existing_data = db.find_documents(location, category)
        if existing_data:
            # Convert `last_updated` to datetime if it's a string
            for doc in existing_data:
                if isinstance(doc.get("last_updated"), str):
                    doc["last_updated"] = datetime.datetime.fromisoformat(doc["last_updated"])

            # Filter based on `last_updated` (7-day freshness check)
            valid_data = [doc for doc in existing_data if doc["last_updated"] >= seven_days_ago]

            if valid_data:
                logger.info(f"Returning fresh data from MongoDB for {category} in {location}.")
                try:
                    set_cache(cache_key, valid_data)  # Update Redis cache
                except Exception as e:
                    logger.warning("Failed to update Redis cache", exc_info=True)
                return valid_data
    except Exception as e:
        logger.warning("MongoDB lookup failed", exc_info=True)

    # Step 3: Scrape fresh data (if no valid cached data found)
    logger.info(f"🛠 Scraping fresh data for {category} in {location}.")
    if category not in SCRAPERS:
        raise ScraperException(detail=f"No scraper available for category {category}")

    try:
        data: List[dict] = SCRAPERS[category].main(location, **kwargs)
        if not data:
            raise ScraperException(detail="Scraping function returned no data")

    except Exception as e:
        logger.error("Error during scraping", exc_info=True)
        raise ScraperException(detail="Scraping failed") from None

    # Process scraped data
    for doc in data:
        doc.pop("_id", None)
        doc["last_updated"] = today.isoformat()  # Store as ISO format string
        for k, v in kwargs.items():
            doc[k] = v

    # Background task to update MongoDB & Redis
    def background_store():
        try:
            db.insert_data(location, category, data)
        except Exception as e:
            logger.error(f"Error inserting data into MongoDB: {e}", exc_info=True)

        try:
            set_cache(cache_key, data)  # Cache new data
        except Exception as e:
            logger.warning("Failed to update Redis cache", exc_info=True)

        try:
            insert_data_to_db_task.apply_async((location, category, data))
        except Exception as e:
            logger.warning("Failed to trigger background DB update task", exc_info=True)

    threading.Thread(target=background_store, daemon=True).start()
    
    return data