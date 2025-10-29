from fastapi import APIRouter, HTTPException
from typing import List, Optional
from backend.services import news_service
from backend.models.schemas import PreferencesIn
from backend.providers import news_provider

from backend.views.news_view import render_news, render_list

router = APIRouter()
USER_PREFS: dict[str, List[str]] = {}

@router.get("/health")
def health():
    return {"ok": True}

@router.post("/users/{user_id}/preferences")
def save_prefs(user_id: str, prefs: PreferencesIn):
    USER_PREFS[user_id] = prefs.topics
    return {"saved": True, "topics": prefs.topics}

@router.post("/admin/fetch")
def admin_fetch(limit: int = 5):
    ids = news_service.pull_and_process(limit=limit)
    return {"inserted": len(ids), "ids": ids}

@router.get("/news/{news_id}")
def get_news(news_id: str):
    item = news_service.get_news(news_id)
    if not item:
        raise HTTPException(404, "news not found")
    return render_news(item)

@router.get("/news")
def list_news(topic: Optional[str] = None, limit: int = 10):
    items = news_service.list_news(topic=topic, limit=limit)
    return render_list(items)



