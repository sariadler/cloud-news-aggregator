# backend/config_cloudinary.py
import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),      # לא חובה ל-fetch, כן חובה ל-upload
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),# לא חובה ל-fetch, כן חובה ל-upload
    secure=True,
)
CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
