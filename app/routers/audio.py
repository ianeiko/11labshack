from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
import json
from app.db import get_supabase
from app.services.elevenlabs_service import elevenlabs_service
from app.models import ConsensusReport, Agent

router = APIRouter(
    prefix="/audio",
    tags=["audio"]
)

class AudioRequest(BaseModel):
    report_id: UUID

@router.post("/synthesize")
async def synthesize_audio(request: AudioRequest):
    """
    Synthesizes audio for a report.
    1. Fetch Report.
    2. Parse script.
    3. Generate audio for each segment.
    4. Stitch/Upload.
    """
    supabase = get_supabase()

    # 1. Fetch Report
    report_res = supabase.table("consensus_reports").select("*").eq("id", str(request.report_id)).execute()
    if not report_res.data:
        raise HTTPException(status_code=404, detail="Report not found")
    report = report_res.data[0]
    script_str = report['narrative_text']

    try:
        segments = json.loads(script_str)
    except:
        raise HTTPException(status_code=500, detail="Failed to parse report script JSON")

    full_audio = b""

    # Pre-fetch agents to get voice IDs
    agents_res = supabase.table("agents").select("name, voice_id").execute()
    agents_map = {a['name']: a['voice_id'] for a in agents_res.data}
    # Add Reporter voice ID (hardcoded or from config)
    agents_map['Reporter'] = "21m00Tcm4TlvDq8ikWAM" # Example 'Rachel' voice or similar

    for seg in segments:
        speaker = seg.get('speaker')
        text = seg.get('text')

        voice_id = agents_map.get(speaker)
        if not voice_id:
            # Fallback for unknown speakers
            voice_id = agents_map.get('Reporter')

        audio_chunk = elevenlabs_service.generate_audio(text, voice_id)
        if audio_chunk:
            full_audio += audio_chunk

    # Upload to Supabase Storage
    path = f"reports/{request.report_id}.mp3"
    try:
        # Check if bucket exists, assuming 'audio-reports' or similar from README/setup
        # Using 'public' bucket for simplicity if not specified
        bucket = "reports"

        # Supabase Python SDK storage upload
        # supabase.storage.from_(bucket).upload(path, full_audio, {"content-type": "audio/mpeg"})
        # We need to handle overwrite or existing

        res = supabase.storage.from_(bucket).upload(path, full_audio, {"content-type": "audio/mpeg", "upsert": "true"})

        # Get Public URL
        public_url = supabase.storage.from_(bucket).get_public_url(path)

        # Update Report
        supabase.table("consensus_reports").update({"audio_url": public_url}).eq("id", str(request.report_id)).execute()

        return {"audio_url": public_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {str(e)}")
