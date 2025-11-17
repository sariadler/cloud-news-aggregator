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
    native = (
        item.get("imageUrl") or 
        item.get("urlToImage") or 
        item.get("image") or
        item.get("thumbnail") or
        item.get("media")
    )

    if native:
        # עוטפים ב־Cloudinary אם מופעל
        return (
            f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/fetch/f_auto,q_auto,w_800/{quote(native, safe='')}"
            if CLOUDINARY_CLOUD_NAME else native
        )

#     # 2) אין urlToImage → אין תמונה אמיתית → מחזירים None
#     return None



def pull_and_process(limit: int = 10) -> List[str]:
    
    raw = fetch_latest(limit)
    publish_batch(raw)
    ids: List[str] = []
    for it in raw:
        print("DEBUG RAW ITEM:", it)
        text = f"{it.get('title','')} {it.get('summary','')}"
        topic = classify_topic(text)
        ents  = extract_entities(text)
        
        image_url = it.get("imageUrl") or _pick_image_url(it)

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



# import os
# import uuid
# from typing import List, Optional
# from urllib.parse import quote

# from backend.models.schemas import News
# from backend.repositories.news_repo import MongoNewsRepository
# from backend.providers.news_provider import fetch_latest
# from backend.ai.nlp import classify_topic, extract_entities
# from backend.services.kafka_producer import publish_batch

# _repo = MongoNewsRepository()

# CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
# print(f"🌥️ CLOUDINARY_CLOUD_NAME = {CLOUDINARY_CLOUD_NAME}")


# # ---------------------------
# # תמונת fallback לפי topic
# # ---------------------------
# def _fallback_image(topic: str) -> str:
#     mapping = {
#         "Politics": "https://res.cloudinary.com/drelmxm3a/image/upload/politics.jpg",
#         "Finance":  "https://res.cloudinary.com/drelmxm3a/image/upload/finance.jpg",
#         "Science":  "https://res.cloudinary.com/drelmxm3a/image/upload/science.jpg",
#         "Culture":  "https://res.cloudinary.com/drelmxm3a/image/upload/culture.jpg",
#         "Sport":    "https://res.cloudinary.com/drelmxm3a/image/upload/sport.jpg",
#     }
#     return mapping.get(topic, "https://res.cloudinary.com/drelmxm3a/image/upload/default.jpg")


# # ---------------------------
# # בחירת תמונה
# # ---------------------------
# def _pick_image_url(item: dict, topic: str) -> str:
#     native = item.get("urlToImage") or item.get("image")

#     # יש תמונה מקורית
#     if native:
#         return (
#             f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/fetch/f_auto,q_auto,w_800/{quote(native, safe='')}"
#         )

#     # אין תמונה → תמונת fallback לפי topic
#     return _fallback_image(topic)


# # ---------------------------
# # שמירת חדשות
# # ---------------------------
# def pull_and_process(limit: int = 10) -> List[str]:
#     raw = fetch_latest(limit)
#     publish_batch(raw)

#     ids = []

#     for it in raw:
#         print("DEBUG RAW ITEM:", it)

#         text = f"{it.get('title','')} {it.get('summary','')}"
#         topic = classify_topic(text)
#         ents = extract_entities(text)

#         image_url = _pick_image_url(it, topic)

#         news = News(
#             id=str(uuid.uuid4()),
#             title=it.get("title", ""),
#             summary=it.get("summary"),
#             url=it.get("url"),
#             published_at=it.get("published_at"),
#             topic=topic,
#             entities=ents,
#             imageUrl=image_url
#         )

#         _repo.save(news)
#         ids.append(news.id)

#     return ids


# def get_news(news_id: str) -> Optional[News]:
#     return _repo.get(news_id)


# def list_news(topic: str | None = None, limit: int = 10) -> List[News]:
#     return _repo.list(topic=topic, limit=limit)

