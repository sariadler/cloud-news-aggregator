# frontend/models/schema.py
from pydantic import BaseModel, HttpUrl
from typing import Optional

class Article(BaseModel):
    title: str
    summary: str = ""
    category: str = "general"
    url: Optional[str] = None
    publishedAt: Optional[str] = None
    imageUrl: Optional[str] = None
    score: float = 0.0

def normalize_article(d: dict) -> Article:
    """מקבל dict מה-API/Mock ומחזיר Article עם ערכי ברירת מחדל בטוחים."""
    # המרת טיפוסים ועדינות לשדות חסרים
    score = d.get("score", 0.0)
    try:
        score = float(score)
    except Exception:
        score = 0.0

    return Article(
        title=d.get("title", "").strip(),
        summary=d.get("summary", "").strip(),
        category=d.get("category", "general"),
        url=d.get("url"),
        publishedAt=d.get("publishedAt"),
        imageUrl=d.get("imageUrl"),
        score=score,
    )
