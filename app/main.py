from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1 import ingestion, chat
from app.db.session import init_db
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (Create tables)
    await init_db()
    # Ensure static directory exists
    os.makedirs("app/static", exist_ok=True)
    yield

app = FastAPI(
    title="AI RAG Backend",
    description="A FastAPI backend for local RAG and interview booking",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(ingestion.router, prefix="/api/v1/ingestion", tags=["ingestion"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

# Serve Static Files
# We check if the directory exists first to avoid startup errors
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    index_path = "app/static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI RAG Backend API is running. Visit /docs for API documentation."}
