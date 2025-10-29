import uuid
from typing import List
from backend.models.schemas import News
from backend.repositories.news_repo import NewsRepository, InMemoryNewsRepository
from backend.providers.news_provider import fetch_latest
from backend.ai.nlp import classify_topic, extract_entities
from backend.services.kafka_producer import publish_batch


_repo: NewsRepository = InMemoryNewsRepository()

def set_repo(repo: NewsRepository):
    global _repo
    _repo = repo

def pull_and_process(limit: int = 10) -> List[str]:
    raw = fetch_latest(limit)
    publish_batch(raw)
    ids: List[str] = []
    for it in raw:
        text = f"{it.get('title','')} {it.get('summary','')}"
        topic = classify_topic(text)
        ents  = extract_entities(text)
        news = News(
            id=str(uuid.uuid4()),
            title=it.get("title",""),
            summary=it.get("summary"),
            url=it.get("url"),
            published_at=it.get("published_at"),
            topic=topic,
            entities=ents
        )
        _repo.save(news)
        ids.append(news.id)
    return ids

def get_news(news_id: str) -> News | None:
    return _repo.get(news_id)

def list_news(topic: str | None = None, limit: int = 10) -> List[News]:
    return _repo.list(topic=topic, limit=limit)
