# frontend/controllers/news_controller.py
import os
from typing import List, Dict, Any, Tuple, Optional
from ..services.api_client import MockNewsClient, HttpNewsClient
# למעלה בקובץ
import html
from ..services.kafka_service import publish_batch  # או publish_article אם תרצי 
from pathlib import Path
from dotenv import load_dotenv

# טוען את frontend/.env במפורש (גם כשמריצים מהשורש)
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"   # .../frontend/.env
print("🔎 ENV_PATH =", ENV_PATH, "exists:", ENV_PATH.exists())
load_dotenv(ENV_PATH)

ENABLE_KAFKA = os.getenv("ENABLE_KAFKA", "1") not in ("0", "false", "False")

# --- בחירת מקור הנתונים + Fallback אוטומטי למוק ---
API_BASE_URL = os.getenv("API_BASE_URL")
print("🛰️  Using backend:", API_BASE_URL)

http_client: Optional[HttpNewsClient] = HttpNewsClient(API_BASE_URL) if API_BASE_URL else None
mock_client = MockNewsClient()
client = http_client or mock_client  # if there is no http_client, use the mock_client

CATEGORIES = ["all", "tech", "politics", "sport", "business", "world", "health"]


# ---------- עזר: מיון ועימוד ----------
def _apply_sort(items: List[Dict[str, Any]], sort_by: str, order: str) -> None:
    reverse = (order == "desc")

    def key_pub(a):
        # ברירת מחדל – מחרוזת/תאריך ISO, None -> ""
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

        # ... אחרי שמיינו/סיננו ויש לנו data:
    # אם תרצי לשלוח *לפני* המיון/סינון, הזיזי את הקריאה למעלה.
    if ENABLE_KAFKA:
        try:
            # שולחים את מה שחזר (עד LIMIT) כדי שלא להציף
            publish_batch(data)
        except Exception:
            # לא להפיל את ה-UI
            pass
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


def get_news_cards_html(category: str = "all", limit: int = 50, q: str = "",
                        sort_by: str = "publishedAt", order: str = "desc") -> str:
    """גרסה שמביאה נתונים בעצמה (לשימושים ישנים/מהירים)."""
    data = _fetch(category, limit, q, sort_by, order)
    return get_news_cards_html_from_items(data)


# ---------- פונקציות שה-View קורא ----------
def get_news_table(category: str = "all", limit: int = 50, q: str = "",
                   sort_by: str = "publishedAt", order: str = "desc") -> List[List[Any]]:
    data = _fetch(category, limit, q, sort_by, order)
    return _articles_to_table(data)


def update_all(category: str, limit: int, q: str):
    """גרסה ישנה (שמורה תאימות): כרטיסיות + טבלה, ללא עימוד."""
    return get_news_cards_html(category, limit, q), get_news_table(category, limit, q)


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
                          page: int = 1, page_size: int = 9):
    """
    מחזיר:
    - HTML כרטיסיות (רק פריטי העמוד)
    - שורות טבלה     (רק פריטי העמוד)
    - data_state      (פריטי העמוד, לשימוש בלשונית 'פרטים')
    - titles          (כותרות פריטי העמוד, ל-Dropdown)
    - total           (סך כל הפריטים לפני עימוד)
    """
    full_data = _fetch(category, limit, q, sort_by, order)
    page_items, total = _paginate(full_data, page, page_size)

    cards_html = get_news_cards_html_from_items(page_items)   # ⬅️ מסונכרן עם העימוד
    table_rows = _articles_to_table(page_items)               # ⬅️ גם הטבלה מסונכרנת
    titles = [a.get("title", "") for a in page_items]

    return cards_html, table_rows, page_items, titles, total


def detail_by_index(data: List[Dict[str, Any]], index: int) -> str:
    if not data or index is None or index < 0 or index >= len(data):
        return "לא נבחרה כתבה."
    return get_article_detail_md(data[index])




def get_news_cards_html_from_items(items: List[Dict[str, Any]]) -> str:
    if not items:
        return '<div class="cards-grid"><div class="card">🔍 לא נמצאו תוצאות</div></div>'

    parts: List[str] = []
    for a in items:
        title = html.escape(a.get("title", "") or "")
        summary = html.escape(a.get("summary", "") or "")
        cat = html.escape(a.get("category", "") or "")
        url = a.get("url") or ""
        published = html.escape(a.get("publishedAt", "") or "")
        image = a.get("imageUrl") or ""
        print(f"🖼️ Image URL: {image}")  
        if not image:
            image = "https://res.cloudinary.com/drelmxm3a/image/upload/v1763063593/ChatGPT_Image_Nov_13_2025_09_52_48_PM_fw5jyy.png"

        try:
            score = float(a.get("score", 0.0))
        except Exception:
            score = 0.0

        if summary and len(summary) > 300:
            summary = summary[:300].rstrip() + "…"

        parts.append(f"""
          <div class="card">
            {f'<img src="{image}" alt="{title}">' if image else ''}
            <h3>{title}</h3>
            <div class="meta">קטגוריה: {cat} · ציון: {score:.2f} · תאריך: {published}</div>
            <p>{summary}</p>
            {f'<a class="btn" href="{url}" target="_blank" rel="noopener">קראי עוד →</a>' if url else ''}
          </div>
        """)

    # 🧠 הוספת CSS שמתקן את התמונות
    styles = """
    <style>
    .card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 12px;
        display: block;
    }
    </style>
    """

    return styles + '<div class="cards-grid">' + "".join(parts) + '</div>'

def _articles_to_cards_md(items):
    # תאימות לשם הישן – מחזיר את ה-HTML החדש
    return get_news_cards_html_from_items(items)
