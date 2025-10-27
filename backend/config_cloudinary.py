# backend/config_cloudinary.py
import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

# טוען את .env מתוך תיקיית backend (אותו-folder של הקובץ הזה)
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

# אם יש CLOUDINARY_URL – מספיק; אחרת נטען שלושת המשתנים
if os.getenv("CLOUDINARY_URL"):
    cloudinary.config(secure=True)  # יקרא מה-URL
else:
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

print(
    "CLOUDINARY DEBUG →",
    {"has_url": bool(os.getenv("CLOUDINARY_URL")),
     "cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME") or "(from URL)"}
)
