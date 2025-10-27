from fastapi import FastAPI
from backend import config_cloudinary
from backend.controllers.news_controller import router as news_router


app = FastAPI(title="Cloud News Aggregator - MVC Gateway")
app.include_router(news_router)


from backend.controllers import media_controller
app.include_router(media_controller.router)
