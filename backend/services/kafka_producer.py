import os
import json
from kafka import KafkaProducer

# ---- הגדרות קפקה ----
_TOPIC = os.getenv("TOPIC_NEWS_RAW", "news.raw")
_BOOTSTRAP = os.getenv("KAFKA_BROKER", "kafka:29092")

# ---- יצירת producer אחד בלבד ----
_producer = KafkaProducer(
    bootstrap_servers=_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def _get_producer():
    """מחזיר את האובייקט היחיד של KafkaProducer"""
    return _producer


def publish_batch(articles: list) -> None:
    """שולח באצ' של כתבות גולמיות לטופיק בקפקה"""
    if not articles:
        print("⚠️ אין כתבות לשליחה ל־Kafka.")
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
        print(f"✅ נשלחו {len(articles)} כתבות ל־Kafka → {_TOPIC}")
    except Exception as e:
        print(f"❌ שגיאה בשליחה ל־Kafka: {e}")
