from fastapi import FastAPI
from backend import config_cloudinary
from backend.controllers.news_controller import router as news_router

app = FastAPI(title="Cloud News Aggregator - MVC Gateway")
app.include_router(news_router)

from backend.controllers import media_controller
app.include_router(media_controller.router)

import threading, time, requests, schedule


@app.on_event("startup")
def startup_event():
    """
    מפעיל אוטומטית את /admin/fetch כששרת ה־backend עולה.
    זה גורם למערכת להביא חדשות לבד ברגע שהכול עלה (כמו gateway קטן).
    בנוסף, מפעיל לולאת schedule שמביאה חדשות כל 30 דקות.
    """

    def trigger_fetch():
        """שאיבה ראשונית כששרת ה־backend עולה"""
        time.sleep(5)  # מוודא שקפקה ו־DB כבר פעילים
        try:
            print("🚀 Triggering automatic news fetch from /admin/fetch ...")
            res = requests.post("http://localhost:8000/admin/fetch", params={"limit": 50})
            print("✅ Auto-fetch response:", res.json())
        except Exception as e:
            print("❌ Failed to trigger automatic fetch:", e)

    def auto_fetch_job():
        """שאיבה חוזרת אוטומטית כל 30 דקות"""
        try:
            print("🕒 Scheduled fetch running ...")
            res = requests.post("http://localhost:8000/admin/fetch", params={"limit": 50})
            print("✅ Scheduled auto-fetch result:", res.json())
        except Exception as e:
            print("❌ Error in scheduled fetch:", e)

    def schedule_loop():
        """לולאה שרצה ברקע ומפעילה את המשימות המתוזמנות"""
        schedule.every(30).minutes.do(auto_fetch_job)
        print("🕒 Scheduler started (fetch every 30 minutes)")
        while True:
            schedule.run_pending()
            time.sleep(1)

    # מריצים את שתי הפונקציות ברקע בלי לחסום את השרת
    threading.Thread(target=trigger_fetch).start()
    threading.Thread(target=schedule_loop, daemon=True).start()
