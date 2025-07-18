from google import genai
from google.genai import types
import json
from datetime import date
from src.core.config import settings
from src.schemas.medicine import MedicineTranscriptionResponse

class AIService:
    """Service class for AI operations using Gemini API."""

    @staticmethod
    def transcribe_prescription(audio_bytes: bytes, mime_type: str) -> dict:
        """Transcribes prescription from audio bytes and returns a JSON object."""
        today_str = date.today().isoformat()
        prompt = f"""
            Analyze this audio recording of a doctor's prescription dictation and extract the prescription information.
            The doctor is speaking about medication details including:
            - Medicine name
            - Strength/dosage
            - Frequency (how often to take)
            - Timing (when to take - morning/evening/after food etc.)
            - Start date of the medicine course (if mentioned, if not, assume today ({today_str}) as the start date)
            - End date of the medicine course (if mentioned or can be inferred based on duration or number of days)
            - Any additional notes or instructions about the prescription.

            Extract this information accurately with your best effort from the audio and return it in the requested structured format.
        """
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=mime_type,
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MedicineTranscriptionResponse,
                thinking_config=types.ThinkingConfig(thinking_budget=1024),
                temperature=0.0,
            )
        )
        if not response.text:
            return {}
        return json.loads(response.text)
