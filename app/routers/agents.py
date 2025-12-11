from fastapi import APIRouter, HTTPException
from typing import List
import json
from pathlib import Path
from app.db import get_supabase
from app.models import AgentBase, Agent

router = APIRouter(
    prefix="/agents",
    tags=["agents"]
)

@router.post("/seed", response_model=List[Agent])
def seed_agents():
    """
    Reads agents from app/data/agents.json and inserts/updates them in Supabase.
    """
    try:
        data_path = Path("app/data/agents.json")
        if not data_path.exists():
            raise HTTPException(status_code=404, detail="agents.json not found")

        with open(data_path, "r") as f:
            agents_data = json.load(f)

        supabase = get_supabase()
        response = supabase.table("agents").upsert(agents_data, on_conflict="name").execute()

        # In a real scenario, we might want to handle errors from Supabase
        # response.data contains the inserted rows
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Agent])
def get_agents():
    supabase = get_supabase()
    response = supabase.table("agents").select("*").execute()
    return response.data
