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


from pymongo import MongoClient
import os


class MongoNewsRepository(NewsRepository):
    def __init__(self):
        mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017")
        client = MongoClient(mongo_url)

        db_name = os.getenv("MONGO_DB", "newsdb")
        self.db = client[db_name]

        # שם הקולקציה
        self.collection = self.db["news"]

    def save(self, item: News) -> None:
        data = item.dict()
        # כדי למנוע כפילויות  
        data["_id"] = data["id"]
        self.collection.replace_one({"_id": data["_id"]}, data, upsert=True)

    def get(self, news_id: str) -> Optional[News]:
        doc = self.collection.find_one({"_id": news_id})
        return News(**doc) if doc else None

    def list(self, topic: str | None = None, limit: int = 10) -> List[News]:
        query = {}
        if topic and topic != "all":
            query["topic"] = topic

        docs = self.collection.find(query).sort("published_at", -1).limit(limit)
        return [News(**d) for d in docs]
