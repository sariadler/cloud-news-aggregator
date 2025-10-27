from dotenv import load_dotenv
from pathlib import Path
import os

ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
