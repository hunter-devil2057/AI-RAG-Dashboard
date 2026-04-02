from openai import OpenAI
from app.core.config import settings
from pydantic import BaseModel, Field
from typing import Optional
import json

class BookingDetails(BaseModel):
    is_booking_intent: bool = Field(description="True if the user wants to book or schedule an interview/meeting")
    name: Optional[str] = Field(None, description="Full name of the user")
    email: Optional[str] = Field(None, description="Email address of the user")
    date: Optional[str] = Field(None, description="Date of the interview (YYYY-MM-DD format)")
    time: Optional[str] = Field(None, description="Time of the interview (HH:MM format)")

class IntentExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract(self, query: str, history: list = []) -> BookingDetails:
        """Extracts booking intent and details from the query and history."""
        
        system_prompt = """
        You are an assistant that identifies 'interview booking' intent and extracts details.
        Details needed: name, email, date (YYYY-MM-DD), time (HH:MM).
        Current date is 2026-04-02.
        If any detail is missing, leave it as null.
        Only set is_booking_intent to True if the text explicitly requests a booking or schedule.
        """
        
        # Format history for extraction context
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        user_input = f"History:\n{history_str}\n\nQuery: {query}"
        
        try:
            # We use tool/function calling for structured extraction
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "extract_booking",
                        "description": "Extract interview booking details",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "is_booking_intent": {"type": "boolean"},
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                                "date": {"type": "string"},
                                "time": {"type": "string"}
                            },
                            "required": ["is_booking_intent"]
                        }
                    }
                }],
                tool_choice={"type": "function", "function": {"name": "extract_booking"}}
            )
            
            tool_call = response.choices[0].message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            return BookingDetails(**args)
            
        except Exception as e:
            # Fallback or log
            print(f"Extraction error: {e}")
            return BookingDetails(is_booking_intent=False)

intent_extractor = IntentExtractor()
