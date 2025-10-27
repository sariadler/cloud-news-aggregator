import json
from kafka import KafkaConsumer
from pymongo import MongoClient
import os

# ---- הגדרות סביבה ----
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("TOPIC_NEWS_CLASSIFIED", "news.classified")
MONGO_URL = os.getenv("DB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "cloud_news")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "articles")

# ---- פונקציית עזר לפענוח JSON ----
def safe_json_load(msg):
    if not msg:
        return None
    try:
        return json.loads(msg.decode("utf-8"))
    except Exception:
        print(f"⚠️ הודעה לא תקינה: {msg}")
        return None

# ---- חיבור למונגו ----
try:
    mongo_client = MongoClient(MONGO_URL)
    db = mongo_client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f"✅ Connected to MongoDB at {MONGO_URL}, using DB '{DB_NAME}', collection '{COLLECTION_NAME}'")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    exit(1)

# ---- חיבור לקפקה ----
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="cloud-news-consumer",
    value_deserializer=safe_json_load,
)

print(f"📥 Listening to Kafka topic: {TOPIC}")

# ---- לולאת קריאה ----
for msg in consumer:
    data = msg.value
    if not data:
        continue

    title = data.get("title", "ללא כותרת")
    category = data.get("category", "?")
    print(f"✅ כתבה חדשה: {title} | קטגוריה: {category}")

    try:
        collection.insert_one(data)
        print("💾 Saved to MongoDB!\n")
    except Exception as e:
        print(f"❌ Error saving to MongoDB: {e}")
