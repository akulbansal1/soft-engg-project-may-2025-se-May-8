from google import genai
from google.genai import types
import json
from datetime import date
from src.core.config import settings
from src.schemas.medicine import MedicineTranscriptionResponse, FrequencyPatternResponse
from src.models.medicine import Medicine

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

    @staticmethod
    def parse_medicine_frequency(medicine: Medicine) -> dict:
        """Parse medicine frequency text and return structured schedule pattern."""
        medicine_str = str(medicine)

        prompt = f"""
            Parse the following medicine information and create a structured reminder schedule:
            
            Medicine Details:
            {medicine_str}
            
            Focus on the "frequency" field, but also consider "notes" and other context for better scheduling.
            
            Return a structured schedule following the given schema with:
            1. interval: How often the medicine should be taken (unit and value)
            2. times_per_interval: Specific times during each interval when medicine should be taken
            
            Guidelines:
            - Use common medical timing (9 AM for morning, 9 PM for evening)
            - Consider notes for special timing (e.g., "with food", "before sleep")
            - Convert relative times to specific hours:
              * Morning: 9 AM, Afternoon: 2 PM, Evening: 7 PM
              * Before meals: 30min before (8 AM, 1 PM, 6:30 PM)
              * After meals: 30min after (9:30 AM, 2:30 PM, 8:30 PM)
              * With food/meals: same as after meals
              * Before sleep: 10 PM
              * Other cases should be handled based on common medical practices.
        """
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FrequencyPatternResponse,
                temperature=0.0,
            )
        )
        
        if not response.text:
            return {}
        return json.loads(response.text)
