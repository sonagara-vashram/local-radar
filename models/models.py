from pydantic import BaseModel, Field
from typing import List, Dict

class ScrapeResponse(BaseModel):
    """
    Model representing a successful scraping response.
    Attributes:
        data (List[Dict]): A list of dictionaries containing scraped data.
    """
    data: List[Dict] = Field(..., description="List of scraped data items")

class ErrorResponse(BaseModel):
    """
    Model representing an error response.
    Attributes:
        detail (str): A message detailing the error encountered.
    """
    detail: str = Field(..., description="Error detail message")