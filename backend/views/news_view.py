from typing import List, Dict
from backend.models.schemas import News

def render_news(item: News) -> Dict:
    return item.model_dump()

def render_list(items: List[News]) -> List[Dict]:
    return [render_news(n) for n in items]
