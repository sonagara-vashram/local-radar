from typing import List
from config.celery_config import celery_app
from database.mongo import db
from core.logging import logger
from core.exceptions import DatabaseException

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def insert_data_to_db_task(self, location: str, category: str, data: List[dict]) -> None:
    """
    Celery task to insert scraped data into MongoDB.

    This task attempts to insert or update scraped data into the database.
    If the insertion fails due to a DatabaseException, the task will retry up to 3 times
    with a 60-second delay between retries.

    Args:
        location (str): The location for which data has been scraped.
        category (str): The category of the scraped data.
        data (List[dict]): A list of dictionaries representing the scraped data.
    Returns:
        None
    """
    try:
        if not data:
            logger.info(f"No data to insert for category '{category}' in location '{location}'.")
            return
        # Attempt to insert or update the scraped data in MongoDB.
        inserted = db.insert_data(location, category, data)
        logger.info(f"Data insertion successful for category '{category}' in location '{location}': {inserted}")
    except DatabaseException as e:
        logger.error(f"Failed to insert data for category '{category}' in location '{location}': {e}", exc_info=True)
        try:
            # Retry the task with the original exception.
            self.retry(exc=e, countdown=60)
        except Exception as retry_exc:
            logger.error(f"Retry failed for category '{category}' in location '{location}': {retry_exc}", exc_info=True)
            raise retry_exc from None