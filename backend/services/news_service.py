import os
import uuid
from typing import List, Optional
from urllib.parse import quote

from backend.models.schemas import News
from backend.repositories.news_repo import NewsRepository, InMemoryNewsRepository
from backend.providers.news_provider import fetch_latest
from backend.ai.nlp import classify_topic, extract_entities
from backend.services.kafka_producer import publish_batch

from backend.repositories.news_repo import MongoNewsRepository

_repo = MongoNewsRepository()


# ⚙️ אופציונלי: להשתמש ב-Cloudinary fetch אם יש cloud_name
CLOUDINARY_CLOUD_NAME: Optional[str] = os.getenv("CLOUDINARY_CLOUD_NAME")
print(f"🌥️ CLOUDINARY_CLOUD_NAME = {CLOUDINARY_CLOUD_NAME}")

def _as_cloudinary_fetch(raw_url: str) -> str:
    # f_auto,q_auto כדי לקבל דחיסה ותמיכה בפורמטים אוטומטית
    return f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/fetch/f_auto,q_auto,w_800/{quote(raw_url, safe='')}"

def _pick_image_url(item: dict) -> Optional[str]:
    # 1) יש תמונה מקורית אמיתית → משתמשים בה
    native = item.get("urlToImage") or item.get("image")
    if native:
        # עוטפים ב־Cloudinary אם מופעל
        return (
            f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/fetch/f_auto,q_auto,w_800/{quote(native, safe='')}"
            if CLOUDINARY_CLOUD_NAME else native
        )

    # 2) אין urlToImage → אין תמונה אמיתית → מחזירים None
    return None



# def _pick_image_url(item: dict) -> Optional[str]:
#     # 1) אם NewsAPI הביא urlToImage – נשתמש בו
#     native = item.get("urlToImage") or item.get("image")
#     page_url = item.get("url")
#     if native:
#         return _as_cloudinary_fetch(native) if CLOUDINARY_CLOUD_NAME else native
#     # 2) אין urlToImage? אם יש cloud_name ננסה fetch ישירות מכתבת המקור (לא תמיד עובד, אבל עדיף מכלום)
#     if CLOUDINARY_CLOUD_NAME and page_url:
#         return _as_cloudinary_fetch(page_url)
#     # 3) אין תמונה
#     return None

# def set_repo(repo: NewsRepository):
#     global _repo
#     _repo = repo

def pull_and_process(limit: int = 10) -> List[str]:
    raw = fetch_latest(limit)
    publish_batch(raw)
    ids: List[str] = []
    for it in raw:
        text = f"{it.get('title','')} {it.get('summary','')}"
        topic = classify_topic(text)
        ents  = extract_entities(text)

        image_url = _pick_image_url(it)   # 👈 חדש

        news = News(
            id=str(uuid.uuid4()),
            title=it.get("title",""),
            summary=it.get("summary"),
            url=it.get("url"),
            published_at=it.get("published_at"),
            topic=topic,
            entities=ents,
            imageUrl=image_url # 👈 חדש
        )
        _repo.save(news)
        ids.append(news.id)
    return ids

def get_news(news_id: str) -> News | None:
    return _repo.get(news_id)

def list_news(topic: str | None = None, limit: int = 10) -> List[News]:
    return _repo.list(topic=topic, limit=limit)
