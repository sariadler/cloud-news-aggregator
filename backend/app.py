from fastapi import FastAPI
from backend.controllers.news_controller import router as news_router

app = FastAPI(title="Cloud News Aggregator - MVC Gateway")
app.include_router(news_router)
