import os, json
from pathlib import Path
import requests
from typing import List, Optional, Dict, Any

# 👈 שימי לב: schema נמצא עכשיו מתחת models, ולכן שני נקודות
from ..models.schema import Article  # אם אין לך שימוש ב-Article פה, אפשר גם להסיר

# טיפוס נוח למערך כתבות כפי שהוא מגיע (dictים גולמיים)
Articles = List[Dict[str, Any]]

# --- ממשק גנרי ---
class NewsClient:
    def list_news(self, category: Optional[str]=None, limit: int=20) -> Articles:
        raise NotImplementedError

# --- מימוש Mock להתחלה ---
class MockNewsClient(NewsClient):
    def __init__(self):
        # הקובץ mock_data.json יושב בתיקיית frontend (אחות של services)
        mock_path = Path(__file__).parents[1] / "mock_data.json"
        self.data: Articles = json.loads(mock_path.read_text(encoding="utf-8"))

    def list_news(self, category: Optional[str]=None, limit: int=20) -> Articles:
        items = self.data
        if category and category != "all":
            items = [a for a in items if a.get("category","").lower() == category.lower()]
        return items[:limit]


class HttpNewsClient(NewsClient):
    def __init__(self, base_url: str):
        self.base_url = (base_url or "").rstrip("/")

    def list_news(self, category: Optional[str]=None, limit: int=20) -> Articles:
        params = {"limit": limit}
        if category and category != "all":
            params["category"] = category
        
        r = requests.get(f"{self.base_url}/news", params=params, timeout=10)
        r.raise_for_status()
        raw_list = r.json()

        normalized = []
        for a in raw_list:
            normalized.append({
                "title": a.get("title", ""),
                "summary": a.get("summary", ""),
                "url": a.get("url", ""),
                "publishedAt": a.get("publishedAt") or a.get("published_at") or "",
                "category": a.get("category", ""),
                "entities": a.get("entities", []),
                "score": a.get("score", 0),
                
                # 👇 זה הכי חשוב
                "imageUrl": a.get("imageUrl") or a.get("image") or a.get("urlToImage") or "",
            })

        return normalized

