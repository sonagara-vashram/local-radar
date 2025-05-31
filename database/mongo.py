import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from config.config import settings
from core.exceptions import DatabaseException
from core.logging import logger
from typing import Any, List, Optional

class MongoDB:
    def __init__(self, uri: str = settings.MONGO_URI, db_name: str = settings.DATABASE_NAME) -> None:
        """
        Initialize the MongoDB connection.
        Args:
            uri (str): MongoDB URI.
            db_name (str): Name of the database.
        """
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            logger.info(f"Connected to MongoDB: {db_name}")
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
            raise DatabaseException(str(e)) from None

    def get_collection(self, collection_name: str):
        """
        Retrieve a collection from the database.
        Args:
            collection_name (str): The name of the collection.
        Returns:
            Collection: The MongoDB collection object.
        """
        return self.db[collection_name]

    def insert_data(self, location: str, category: str, data: List[dict]) -> bool:
        """
        Insert or update data in MongoDB while avoiding duplicates.
        
        This function normalizes the 'location' and 'category' strings, adds a 'last_updated'
        timestamp to each data item, and then either updates an existing document or inserts a new one.
        Args:
            location (str): The location identifier.
            category (str): The category under which data is stored.
            data (List[dict]): The data to be inserted.
        Returns:
            bool: True if data was inserted/updated, False if data was already up-to-date.
        Raises:
            DatabaseException: If an error occurs during the insert/update operation.
        """
        try:
            collection = self.get_collection(category)
            timestamp = datetime.datetime.utcnow()

            # Normalize inputs by converting to lowercase.
            location = location.lower()
            category = category.lower()

            # Add the current timestamp to each data item.
            for item in data:
                item["last_updated"] = timestamp

            # Check for an existing document for the given location.
            existing_doc = collection.find_one({"location": location})

            if existing_doc:
                existing_data = existing_doc.get("categories", {}).get(category, [])
                # If all existing documents are up-to-date, skip insertion.
                if all(
                    doc["last_updated"] >= timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                    for doc in existing_data
                ):
                    logger.info(f"Data for {category} in {location} is already up to date")
                    return False

            # Update or insert data for the given location and category.
            collection.update_one(
                {"location": location},
                {"$set": {f"categories.{category}": data}},
                upsert=True
            )
            logger.info(f"Inserted/updated data for {category} in {location}")
            return True

        except PyMongoError as e:
            logger.error(f"MongoDB Insert Error: {e}", exc_info=True)
            raise DatabaseException(str(e)) from None

    def find_documents(self, location: str, category: str) -> Optional[List[dict]]:
        """
        Retrieve documents for a given location and category using a case-insensitive search.
        Args:
            location (str): The location to search for.
            category (str): The category to retrieve data from.
        Returns:
            Optional[List[dict]]: A list of documents if found; otherwise, None.
        Raises:
            DatabaseException: If an error occurs during the retrieval process.
        """
        try:
            collection = self.get_collection(category)
            logger.debug(f"Searching MongoDB for: location={location}, category={category}")
            result = collection.find_one(
                {"location": {"$regex": f"^{location}$", "$options": "i"}},  # Case-insensitive search
                {"categories": 1, "_id": 0}
            )
            if result:
                return result["categories"].get(category, [])
            return None
        except PyMongoError as e:
            logger.error(f"MongoDB Find Error: {e}", exc_info=True)
            raise DatabaseException(str(e)) from None

    def __del__(self) -> None:
        """
        Close the MongoDB connection when the instance is destroyed.
        Note: __del__ may not always be reliably called in production; consider implementing an explicit close() method.
        """
        try:
            self.client.close()
            logger.info("Closed MongoDB connection")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}", exc_info=True)

    def get_request_logs(self, start_date: Any = None, end_date: Any = None, limit: int = 100) -> List[dict]:
        """
        Retrieve request logs from the 'request_logs' collection within a specified date range.
        Args:
            start_date (Any, optional): The start date for filtering logs.
            end_date (Any, optional): The end date for filtering logs.
            limit (int, optional): Maximum number of log entries to retrieve (default is 100).
        Returns:
            List[dict]: A list of log documents.
        Raises:
            DatabaseException: If an error occurs during log retrieval.
        """
        try:
            collection = self.get_collection("request_logs")
            query = {}
            if start_date:
                query["timestamp"] = {"$gte": start_date}
            if end_date:
                query["timestamp"] = query.get("timestamp", {})
                query["timestamp"]["$lte"] = end_date
            
            cursor = collection.find(query).sort("timestamp", -1).limit(limit)
            return list(cursor)
        except PyMongoError as e:
            logger.error(f"MongoDB Get Logs Error: {e}", exc_info=True)
            raise DatabaseException(str(e)) from None

db = MongoDB()