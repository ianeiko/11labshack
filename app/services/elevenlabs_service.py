from elevenlabs.client import ElevenLabs
from config import settings

class ElevenLabsService:
    def __init__(self):
        self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)

    def generate_audio(self, text: str, voice_id: str) -> bytes:
        try:
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_monolingual_v1"
            )
            # Consume the generator to get full bytes
            return b"".join(audio_generator)
        except Exception as e:
            print(f"Error generating audio: {e}")
            return b""

elevenlabs_service = ElevenLabsService()
