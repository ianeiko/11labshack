from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from db import get_supabase
from services.llm_service import llm_service
from models import ConsensusReport

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

class ReportRequest(BaseModel):
    topic_id: UUID

@router.post("/generate")
async def generate_report(request: ReportRequest):
    """
    Generates a consensus report for a topic.
    1. Fetch all interviews (or turns) for the topic.
    2. Synthesize a script using a 'Reporter' persona.
    3. Store in consensus_reports.
    """
    supabase = get_supabase()

    # 1. Fetch Topic
    topic_res = supabase.table("topics").select("*").eq("id", str(request.topic_id)).execute()
    if not topic_res.data:
        raise HTTPException(status_code=404, detail="Topic not found")
    topic_title = topic_res.data[0]['title']

    # 2. Fetch Interviews (Assuming 'interviews' table or similar)
    # Since we implemented 'interviews' table logic in previous step (conceptually), we access it here.
    # Note: If we used 'turns' or 'conversations', adjust query accordingly.
    # For now, fetching from 'interviews' table.
    interviews_res = supabase.table("interviews").select("*, agents(name)").eq("topic_id", str(request.topic_id)).execute()
    interviews = interviews_res.data

    if not interviews:
        # Fallback: Check conversations/turns if interviews table empty
        # This is just safety logic
        pass

    # 3. Construct Context
    context = f"Topic: {topic_title}\n\nInterviews:\n"
    for iv in interviews:
        agent_name = iv.get('agents', {}).get('name', 'Unknown Agent')
        context += f"- {agent_name}: {iv.get('text')}\n"

    # 4. Synthesize Report
    system_prompt = (
        "You are a Radio Reporter synthesizing a consensus report. "
        "Create a script that alternates between your narration and direct quotes from the interviewed personas. "
        "The script should be formatted as a list of segments, e.g., [{'speaker': 'Reporter', 'text': '...'}, {'speaker': 'The Concerned Mother', 'text': '...'}]. "
        "Return ONLY the raw JSON list."
    )

    script_json_str = await llm_service.generate_response(
        provider="openai", # Making Reporter use OpenAI for quality/consistency
        model="gpt-4-turbo-preview",
        system_prompt=system_prompt,
        user_prompt=context
    )

    # Clean up JSON if needed
    script_json_str = script_json_str.replace("```json", "").replace("```", "").strip()

    # 5. Store Report
    # We store the raw script in 'narrative_text' for now.
    report_data = {
        "topic_id": str(request.topic_id),
        "narrative_text": script_json_str
    }

    res = supabase.table("consensus_reports").insert(report_data).execute()

    return res.data
