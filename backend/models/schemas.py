from pydantic import BaseModel, HttpUrl
from typing import List, Optional

# הקטגוריות הקבועות בפרויקט
CATEGORIES = ["Politics", "Finance", "Science", "Culture", "Sport"]

class PreferencesIn(BaseModel):
    topics: List[str]

class News(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    url: Optional[HttpUrl] = None
    published_at: Optional[str] = None
    topic: Optional[str] = None
    entities: List[str] = []
    imageUrl: Optional[str] = None