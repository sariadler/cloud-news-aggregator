# from typing import List, Dict
# from backend.models.schemas import News

# # backend/views/news_view.py
# def render_news(item: dict) -> dict:
#     return {
#         "id": item.get("id"),
#         "title": item.get("title", ""),
#         "summary": item.get("summary", ""),
#         "url": item.get("url", ""),
#         # התאמה לשמות שהפרונט מחפש
#         "publishedAt": item.get("published_at") or "",
#         "category": item.get("topic") or "",
#         "entities": item.get("entities", []),
#         "score": item.get("score", 0.0)
#     }

# def render_list(items: list[dict]) -> list[dict]:
#     return [render_news(i) for i in items]


from typing import Any, Mapping
from backend.models.schemas import News


def render_news(item: Any) -> dict:
    """
    ממיר אובייקט חדשות (מודל News או dict) למבנה dict פשוט ל-API.
    """

    # אם זה מודל Pydantic מסוג News
    if isinstance(item, News):
        # ב-Pydantic v2 יש model_dump, ב-v1 יש dict
        if hasattr(item, "model_dump"):
            data = item.model_dump()
        else:
            data = item.dict()
    # אם זה כבר dict או אובייקט דמוי-מילון
    elif isinstance(item, Mapping):
        data = dict(item)
    else:
        # fallback – ניסיון לקחת __dict__ מאובייקט רגיל
        data = getattr(item, "__dict__", {})

    return {
        "id": str(data.get("id") or data.get("_id") or ""),
        "title": data.get("title", ""),
        "summary": data.get("summary", ""),
        "url": data.get("url", ""),
        # התאמה לשמות שהפרונט מחפש
        "publishedAt": data.get("published_at") or data.get("publishedAt") or "",
        "category": data.get("topic") or data.get("category") or "",
        "entities": data.get("entities") or [],
        "score": data.get("score") or 0.0,
        # תמונה אם קיימת (לא חובה לפרונט, אבל נחמד)
        "imageUrl": data.get("imageUrl") or data.get("image_url"),
    }


def render_list(items: list[Any]) -> list[dict]:
    return [render_news(i) for i in items]
