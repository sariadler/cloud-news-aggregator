from typing import List, Dict
from backend.models.schemas import News

# backend/views/news_view.py
def render_news(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "title": item.get("title", ""),
        "summary": item.get("summary", ""),
        "url": item.get("url", ""),
        # התאמה לשמות שהפרונט מחפש
        "publishedAt": item.get("published_at") or "",
        "category": item.get("topic") or "",
        "entities": item.get("entities", []),
        "score": item.get("score", 0.0)
    }

def render_list(items: list[dict]) -> list[dict]:
    return [render_news(i) for i in items]


