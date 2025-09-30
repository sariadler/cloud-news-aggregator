from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from backend.models.schemas import News

class NewsRepository(ABC):
    @abstractmethod
    def save(self, item: News) -> None: ...
    @abstractmethod
    def get(self, news_id: str) -> Optional[News]: ...
    @abstractmethod
    def list(self, topic: str | None = None, limit: int = 10) -> List[News]: ...

class InMemoryNewsRepository(NewsRepository):
    def __init__(self):
        self._db: Dict[str, News] = {}
    def save(self, item: News) -> None:
        self._db[item.id] = item
    def get(self, news_id: str) -> Optional[News]:
        return self._db.get(news_id)
    def list(self, topic: str | None = None, limit: int = 10) -> List[News]:
        values = list(self._db.values())
        if topic:
            values = [n for n in values if n.topic == topic]
        return values[:limit]
