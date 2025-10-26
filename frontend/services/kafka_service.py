# frontend/services/kafka_service.py
import os, json
from kafka import KafkaProducer

_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS_DOCKER",
             os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
_TOPIC = os.getenv("TOPIC_NEWS_CLASSIFIED", "news.classified")

_producer = None

def _get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
            linger_ms=10
        )
    return _producer

def publish_article(article: dict) -> None:
    """שולח כתבה בודדת לטופיק; שקט אם יש כשל."""
    try:
        p = _get_producer()
        p.send(_TOPIC, article)
    except Exception:
        pass

def publish_batch(articles: list) -> None:
    """שולח באצ' של כתבות; עושה flush פעם אחת בסוף."""
    if not articles:
        return
    try:
        p = _get_producer()
        for a in articles:
            p.send(_TOPIC, {
                "title": a.get("title"),
                "summary": a.get("summary"),
                "category": a.get("category"),
                "publishedAt": a.get("publishedAt"),
                "url": a.get("url"),
                "imageUrl": a.get("imageUrl"),
                "score": a.get("score", 0),
                "_source": "frontend-ui"
            })
        p.flush(timeout=2)
    except Exception:
        pass
