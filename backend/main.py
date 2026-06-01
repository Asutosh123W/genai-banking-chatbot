from fastapi import FastAPI
from backend.api.routes import router
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import engine
from backend.database.models import Base
from backend.api.auth_routes import router as auth_router

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