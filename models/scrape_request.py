from pydantic import BaseModel
from typing import Optional, Dict, Any

class ScrapeRequest(BaseModel):
    category: str
    location: str
    params: Optional[Dict[str, Any]] = None