from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="11LabsHack API",
    description="Backend for Radio Pacis Populi",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to 11LabsHack API", "docs_url": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "ok", "supabase_configured": bool(settings.supabase_url and settings.supabase_key)}

from app.routers import agents, interviews, reports, audio
app.include_router(agents.router)
app.include_router(interviews.router)
app.include_router(reports.router)
app.include_router(audio.router)
