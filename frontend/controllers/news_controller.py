# frontend/controllers/news_controller.py
import os
from typing import List, Dict, Any, Tuple, Optional
from ..services.api_client import MockNewsClient, HttpNewsClient

# --- בחירת מקור הנתונים + Fallback אוטומטי למוק ---
API_BASE_URL = os.getenv("API_BASE_URL")
http_client: Optional[HttpNewsClient] = HttpNewsClient(API_BASE_URL) if API_BASE_URL else None
mock_client = MockNewsClient()
client = http_client or mock_client  # ברירת מחדל

CATEGORIES = ["all", "tech", "politics", "sport", "business", "world", "health"]


# ---------- עזר: מיון ועימוד ----------
def _apply_sort(items: List[Dict[str, Any]], sort_by: str, order: str) -> None:
    reverse = (order == "desc")

    def key_pub(a):
        # מפתח מיון לברירת מחדל (מחרוזת/תאריך ISO), None -> ""
        return a.get("publishedAt") or ""

    def key_score(a):
        try:
            return float(a.get("score", 0))
        except Exception:
            return 0.0

    def key_title(a):
        return (a.get("title") or "").lower()

    key_fn = key_pub
    if sort_by == "score":
        key_fn = key_score
    elif sort_by == "title":
        key_fn = key_title

    try:
        items.sort(key=key_fn, reverse=reverse)
    except Exception:
        # אם משהו לא תקין, לא מפילים את האפליקציה – פשוט לא נמיין
        pass


def _paginate(items: List[Dict[str, Any]], page: int, page_size: int) -> Tuple[List[Dict[str, Any]], int]:
    total = len(items)
    page = max(1, int(page or 1))
    page_size = max(1, int(page_size or 10))
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total


# ---------- שליפה + סינון + מיון ----------
def _fetch(category: str = "all", limit: int = 50, q: str = "",
           sort_by: str = "publishedAt", order: str = "desc") -> List[Dict[str, Any]]:
    """
    מחזיר רשימת כתבות (dict) אחרי סינון בסיסי,
    מיון לפי השדות המבוקשים, ועד LIMIT (לפני עימוד ב-UI).
    כולל Fallback למוק אם ה-HTTP נכשל.
    """
    # שליפה
    try:
        data = (client or mock_client).list_news(
            category=None if category == "all" else category,
            limit=limit
        )
    except Exception:
        # Fallback בטוח
        data = mock_client.list_news(
            category=None if category == "all" else category,
            limit=limit
        )

    # חיפוש טקסטואלי
    if q:
        ql = q.lower()
        data = [a for a in data
                if ql in (a.get("title", "")).lower()
                or ql in (a.get("summary", "")).lower()]

    # מיון במקום
    _apply_sort(data, sort_by=sort_by, order=order)
    return data


# ---------- בניית יציאות ל-View ----------
def _article_to_table_row(a: Dict[str, Any]) -> List[Any]:
    title = a.get("title", "")
    cat = a.get("category", "")
    score = a.get("score", 0.0)
    try:
        score = round(float(score), 2)
    except Exception:
        pass
    published = a.get("publishedAt", "")
    url = a.get("url", "")
    return [title, cat, score, published, url]


def _articles_to_table(items: List[Dict[str, Any]]) -> List[List[Any]]:
    return [_article_to_table_row(a) for a in items]


def _articles_to_cards_md(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "🔍 לא נמצאו תוצאות עבור הקריטריונים שנבחרו."
    parts: List[str] = []
    for a in items:
        title = a.get("title", "")
        summary = a.get("summary", "")
        cat = a.get("category", "")
        score = a.get("score", 0.0)
        url = a.get("url", "")
        published = a.get("publishedAt", "")
        image = a.get("imageUrl", "")

        try:
            score = float(score)
        except Exception:
            score = 0.0

        # קיצור תקציר ארוך כדי לא "לשבור" את ה-UI
        if summary and len(summary) > 300:
            summary = summary[:300].rstrip() + "…"

        img_md = f"![]({image})\n\n" if image else ""
        parts.append(
f"""### {title}

{img_md}**קטגוריה:** {cat} · **ציון:** {score:.2f} · **תאריך:** {published}

{summary}

{f"[קראי עוד →]({url})" if url else ""}

---
""")
    return "\n".join(parts)


# ---------- פונקציות שה-View קורא ----------
def get_news_table(category: str = "all", limit: int = 50, q: str = "",
                   sort_by: str = "publishedAt", order: str = "desc") -> List[List[Any]]:
    data = _fetch(category, limit, q, sort_by, order)
    return _articles_to_table(data)


def get_news_cards_md(category: str = "all", limit: int = 50, q: str = "",
                      sort_by: str = "publishedAt", order: str = "desc") -> str:
    data = _fetch(category, limit, q, sort_by, order)
    return _articles_to_cards_md(data)


def update_all(category: str, limit: int, q: str):
    """גרסה ישנה (שמורה תאימות): כרטיסיות + טבלה, ללא מיון/עימוד."""
    return get_news_cards_md(category, limit, q), get_news_table(category, limit, q)


def list_titles(category: str = "all", limit: int = 50, q: str = "",
                sort_by: str = "publishedAt", order: str = "desc") -> List[str]:
    return [a.get("title", "") for a in _fetch(category, limit, q, sort_by, order)]


def get_article_detail_md(article: Dict[str, Any]) -> str:
    title = article.get("title", "")
    summary = article.get("summary", "")
    url = article.get("url", "")
    image = article.get("imageUrl", "")
    published = article.get("publishedAt", "")
    cat = article.get("category", "")
    score = article.get("score", 0.0)
    try:
        score = float(score)
    except Exception:
        score = 0.0

    if summary and len(summary) > 1200:
        summary = summary[:1200].rstrip() + "…"

    img_md = f"![]({image})\n\n" if image else ""
    link = f"[פתחי מקור →]({url})" if url else ""
    return f"""## {title}

{img_md}**קטגוריה:** {cat} · **ציון:** {score:.2f} · **תאריך:** {published}

{summary}

{link}
"""


def update_all_with_state(category: str, limit: int, q: str,
                          sort_by: str = "publishedAt", order: str = "desc",
                          page: int = 1, page_size: int = 10):
    """
    מחזיר:
    - Markdown של כרטיסיות (רק פריטי העמוד)
    - שורות טבלה     (רק פריטי העמוד)
    - data_state      (פריטי העמוד, לשימוש בלשונית 'פרטים')
    - titles          (כותרות פריטי העמוד, ל-Dropdown)
    - total           (סך כל הפריטים לפני עימוד)
    """
    full_data = _fetch(category, limit, q, sort_by, order)
    page_items, total = _paginate(full_data, page, page_size)

    cards_md = _articles_to_cards_md(page_items)
    table_rows = _articles_to_table(page_items)
    titles = [a.get("title", "") for a in page_items]

    return cards_md, table_rows, page_items, titles, total


def detail_by_index(data: List[Dict[str, Any]], index: int) -> str:
    if not data or index is None or index < 0 or index >= len(data):
        return "לא נבחרה כתבה."
    return get_article_detail_md(data[index])
