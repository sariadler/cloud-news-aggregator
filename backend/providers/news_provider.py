# backend/providers/news_provider.py
import logging
from typing import List, Dict, Optional
import requests
from backend.config import NEWSAPI_KEY

log = logging.getLogger("news_provider")

# דמה לפיתוח תמידי (fallback)
_DUMMY = [
    {"title":"Sample headline about AI in politics","url":"https://example.com/ai-politics",
     "summary":"Short summary for local testing.","published_at":"2025-09-21T10:00:00Z"},
    {"title":"Finance: Markets rise amid tech rally","url":"https://example.com/finance",
     "summary":"Stocks climb as investors digest earnings.","published_at":"2025-09-21T11:00:00Z"},
    {"title":"Science: New telescope discovery","url":"https://example.com/science",
     "summary":"Interesting finding in space.","published_at":"2025-09-21T12:00:00Z"},
    {"title":"Culture: Festival opens downtown","url":"https://example.com/culture",
     "summary":"City hosts annual event.","published_at":"2025-09-21T13:00:00Z"},
    {"title":"Sport: Local team wins","url":"https://example.com/sport",
     "summary":"Big victory last night.","published_at":"2025-09-21T14:00:00Z"},
]

def _repeat_to_limit(base: List[Dict], limit: int) -> List[Dict]:
    return (base * ((limit + len(base) - 1) // len(base)))[:limit]

def _safe_call(url: str, params: dict) -> Optional[dict]:
    """קריאה בטוחה ל-NewsAPI עם לוג שגיאה כשנכשל."""
    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code != 200:
            log.error("NewsAPI %s returned %s: %s", url, r.status_code, r.text[:300])
            return None
        data = r.json()
        # גם אם 200, לפעמים אין מאמרים
        if not data or not data.get("articles"):
            log.warning("NewsAPI returned no articles for %s params=%s", url, params)
        return data
    except Exception as e:
        log.exception("NewsAPI request failed: %s", e)
        return None

def fetch_latest(limit: int = 10) -> List[Dict]:
    """
    מחזיר ידיעות גולמיות:
    {title,url,summary,published_at}
    זורם כך:
    1) top-headlines לפי מדינה (מהיר)
    2) אם נכשל/ריק -> everything לפי שאילתה כללית
    3) אם עדיין אין -> דמה (כדי שתמיד יעבוד)
    """
    # 0) אם אין KEY – דמה
    if not NEWSAPI_KEY:
        return _repeat_to_limit(_DUMMY, limit)

    # 1) ניסיון ראשון: top-headlines (בחרי 'us' או 'il')
    url1 = "https://newsapi.org/v2/top-headlines"
    p1 = {
        "country": "us",         # אפשר לשנות ל-"il" אם את רוצה ישראלי
        "pageSize": limit,
        "apiKey": NEWSAPI_KEY,
    }
    data = _safe_call(url1, p1)

    # 2) אם נכשל או אין תוצאות – ננסה everything (לפי נושאים כלליים)
    if not data or not data.get("articles"):
        url2 = "https://newsapi.org/v2/everything"
        p2 = {
            "q": "technology OR science OR politics OR sports OR culture",
            "language": "en",     # אפשר "he" לעברית, אך ה-NLP אצלך באנגלית – ממליץ EN
            "pageSize": limit,
            "sortBy": "publishedAt",
            "apiKey": NEWSAPI_KEY,
        }
        data = _safe_call(url2, p2)

    # 3) אם עדיין אין – חוזרים לדמה
    if not data or not data.get("articles"):
        return _repeat_to_limit(_DUMMY, limit)

    # מיפוי לפורמט אחיד
    out: List[Dict] = []
    for a in data.get("articles", [])[:limit]:
        out.append({
            "title": a.get("title") or "",
            "url": a.get("url"),
            "summary": a.get("description"),
            "published_at": a.get("publishedAt"),
        })
    # אם משום מה לא גזרנו כלום – דמה
    return out if out else _repeat_to_limit(_DUMMY, limit)
