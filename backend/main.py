from fastapi import FastAPI
from api.routes import router
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine
from database.models import Base
from api.auth_routes import router as auth_router

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="GenAI Banking Chatbot",
    description="AI-powered banking support chatbot using RAG",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)