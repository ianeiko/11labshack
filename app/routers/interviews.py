from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from db import get_supabase
from models import Conversation, Turn, Agent
from services.llm_service import llm_service

router = APIRouter(
    prefix="/interviews",
    tags=["interviews"]
)

class InterviewRequest(BaseModel):
    topic_id: UUID

@router.post("/conduct")
async def conduct_interviews(request: InterviewRequest, background_tasks: BackgroundTasks):
    """
    Initiates interviews for a topic.
    1. Fetches the topic entry.
    2. Fetches all agents.
    3. Iterate through agents and generate responses.
    """
    supabase = get_supabase()

    # 1. Fetch Topic
    topic_res = supabase.table("topics").select("*").eq("id", str(request.topic_id)).execute()
    if not topic_res.data:
        raise HTTPException(status_code=404, detail="Topic not found")
    topic = topic_res.data[0]
    topic_title = topic['title']
    topic_id = topic['id']

    # 2. Fetch Agents
    agents_res = supabase.table("agents").select("*").execute()
    agents = agents_res.data

    # 3. Process Interviews
    # Ideally async, but for MVP we might do it sequentially or spawn tasks
    # For now, let's do one by one and store results

    results = []

    for agent_data in agents:
        agent = Agent(**agent_data)

        # Determine model based on provider
        model = None
        if agent.provider == 'openai':
            model = "gpt-4-turbo-preview"
        elif agent.provider == 'claude':
            model = "claude-3-opus-20240229"
        elif agent.provider == 'gemini':
            model = "gemini-1.5-flash"
        elif agent.provider == 'grok':
            model = "grok-beta"

        # Construct System Prompt
        INSTRUCTIONAL_PROMPT = (
            "You are a specific AI persona participating in a round-table interview. "
            "You will be given a topic and must answer based on your specific backstory, "
            "personality, and opinions. Keep your answer concise (under 3-4 sentences) "
            "but full of character."
        )
        system_prompt = f"{INSTRUCTIONAL_PROMPT}\n\nName: {agent.name}\nBio: {agent.bio}"

        # Generate Answer
        answer_text = await llm_service.generate_response(
            provider=agent.provider,
            model=model,
            system_prompt=system_prompt,
            user_prompt=topic_title
        )

        results.append({
            "agent": agent.name,
            "response": answer_text
        })

        # Save to database (placeholder for `interviews` or `turns` table logic)
        # Assuming we just log/return for now as per previous exploration
        # checks showed ambiguity in 'reviews' table existence.
        print(f"Agent {agent.name} says: {answer_text}")

    return {"topic_id": topic_id, "topic": topic_title, "responses": results}
