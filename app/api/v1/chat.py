from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import InterviewBooking
from app.core.memory import chat_memory
from app.services.booking_logic import intent_extractor
from app.services.rag_logic import rag_service
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    is_booking: bool = False

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch History from Redis
    history = chat_memory.get_history(request.session_id)
    
    # 2. Check for Booking Intent & Extraction
    booking_details = intent_extractor.extract(request.query, history)
    
    if booking_details.is_booking_intent:
        # Check if we have all details
        missing = []
        if not booking_details.name: missing.append("name")
        if not booking_details.email: missing.append("email")
        if not booking_details.date: missing.append("date")
        if not booking_details.time: missing.append("time")
        
        if missing:
            res_text = f"I'd love to help you book that! I just need a few more details: {', '.join(missing)}."
            chat_memory.add_message(request.session_id, "user", request.query)
            chat_memory.add_message(request.session_id, "assistant", res_text)
            return ChatResponse(response=res_text, session_id=request.session_id, is_booking=True)
        else:
            # All details present, save to DB
            try:
                scheduled_time = datetime.strptime(f"{booking_details.date} {booking_details.time}", "%Y-%m-%d %H:%M")
                
                new_booking = InterviewBooking(
                    name=booking_details.name,
                    email=booking_details.email,
                    scheduled_at=scheduled_time,
                    session_id=request.session_id
                )
                db.add(new_booking)
                await db.commit()
                
                res_text = f"Perfect! Your interview is booked for {booking_details.date} at {booking_details.time}. I've saved your details for {booking_details.name} ({booking_details.email})."
                chat_memory.add_message(request.session_id, "user", request.query)
                chat_memory.add_message(request.session_id, "assistant", res_text)
                return ChatResponse(response=res_text, session_id=request.session_id, is_booking=True)
            except Exception as e:
                await db.rollback()
                raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")

    # 3. Standard RAG Response if no booking intent
    try:
        response_text = rag_service.generate_response(request.query, history)
        
        # Save messages to Memory
        chat_memory.add_message(request.session_id, "user", request.query)
        chat_memory.add_message(request.session_id, "assistant", response_text)
        
        return ChatResponse(response=response_text, session_id=request.session_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Error: {str(e)}")
