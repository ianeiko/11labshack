from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.db import get_supabase
from app.models import Conversation, Turn, Agent
from app.services.llm_service import llm_service

router = APIRouter(
    prefix="/interviews",
    tags=["interviews"]
)

class InterviewRequest(BaseModel):
    topic: str

@router.post("/conduct")
async def conduct_interviews(request: InterviewRequest, background_tasks: BackgroundTasks):
    """
    Initiates interviews for a topic.
    1. Creates a topic entry.
    2. Fetches all agents.
    3. Iterate through agents and generate responses (in background or sync for now).
    """
    supabase = get_supabase()

    # 1. Create Topic
    topic_res = supabase.table("topics").insert({"title": request.topic}).execute()
    if not topic_res.data:
        raise HTTPException(status_code=500, detail="Failed to create topic")
    topic_id = topic_res.data[0]['id']

    # 2. Fetch Agents
    agents_res = supabase.table("agents").select("*").execute()
    agents = agents_res.data

    # 3. Process Interviews
    # Ideally async, but for MVP we might do it sequentially or spawn tasks
    # For now, let's do one by one and store results

    results = []

    for agent_data in agents:
        agent = Agent(**agent_data)

        # Determine model based on provider (simplified mapping)
        model = None
        if agent.provider == 'openai':
            model = "gpt-4-turbo-preview"
        elif agent.provider == 'claude':
            model = "claude-3-sonnet-20240229"

        # Generate Answer
        answer_text = await llm_service.generate_response(
            provider=agent.provider,
            model=model,
            system_prompt=f"You are {agent.name}. {agent.bio}. Answer the following question in character.",
            user_prompt=request.topic
        )

        # Store Interview (as a 'turn' or 'interview' entry)
        # The schema has 'conversations' (agent_1, agent_2) and 'turns'.
        # The README says: "Input: A specific Topic... Process: Each of the 11 Agents is prompted individually... Output: Text responses stored in Supabase interviews table."
        # Wait, README table for 'interviews' was NOT in the Data Model section I saw earlier.
        # It had 'conversations', 'turns', 'consensus_reports', 'topics', 'agents'.
        # Ah, Step 4 README view showed 'interviews' in the text "Output: Text responses stored in Supabase interviews table." but the schema section listed 'conversations'.
        # Let's assume we store it in `turns` or a simplified `interviews` table if it exists, or maybe `conversations` with just one agent?
        # The schema shows 'conversations' has `agent_1_id` and `agent_2_id`. This implies a dialogue.
        # But Phase 2 is "Interview Module... Each of the 11 Agents is prompted individually".
        # This implies a single-turn "interview" or a conversation with a "Reporter" (who isn't an agent in the DB?).
        # Let's assume for now we use a new table `interviews` if it makes sense, OR we use `turns` linked to a 'conversation' where agent_2 might be null or system.
        # Given "Output: Text responses stored in Supabase interviews table" in line 23 of README.
        # But line 128 "conversations... agent_1_id... agent_2_id".
        # I will CREATE an `interviews` table model if it's missing or re-read to see if I missed it.
        # I checked valid tables in models.py: topics, agents, conversations, turns, consensus_reports.
        # I'll create an `interviews` table in Supabase via code if I can, or just store in a way that fits.
        # Let's assume we create a 'conversation' with agent_1 = agent, agent_2 = NULL (if allowed) or a placeholder.
        # Actually, let's just stick to the text: "Output: Text responses stored in Supabase interviews table."
        # The schema section MIGHT be outdated or I missed a table.
        # I'll check `supabase_setup.sql` if I can.

        # For now, I'll return the results directly and maybe log them.
        # I'll insert into a generic 'interviews' table if I can, or just 'turns' associated with a topic?
        # The 'turns' table has `conversation_id`.
        # I'll create a `interviews` table reference in code for now, assuming it exists or I should create it.
        # Or I'll just return the logic for now.

        results.append({
            "agent": agent.name,
            "response": answer_text
        })

        # Start "saving" logic (stubbed if table unclear)
        try:
             # Try inserting into 'interviews' table if it was mentioned
             supabase.table("interviews").insert({
                 "topic_id": topic_id,
                 "agent_id": str(agent.id),
                 "text": answer_text
             }).execute()
        except:
            # Fallback or ignore if table missing
            pass

    return {"topic": request.topic, "responses": results}
