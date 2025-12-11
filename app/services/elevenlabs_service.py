from elevenlabs import generate, set_api_key
from app.config import settings

class ElevenLabsService:
    def __init__(self):
        if settings.elevenlabs_api_key:
            set_api_key(settings.elevenlabs_api_key)

    def generate_audio(self, text: str, voice_id: str) -> bytes:
        try:
            audio = generate(
                text=text,
                voice=voice_id,
                model="eleven_monolingual_v1"
            )
            return audio
        except Exception as e:
            print(f"Error generating audio: {e}")
            return b""

elevenlabs_service = ElevenLabsService()
