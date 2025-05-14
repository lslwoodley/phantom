# handlers/feedback_handler.py

from fastapi import APIRouter, Request
from telemetry_logger import log_feedback
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/feedback", tags=["Feedback"])

class FeedbackRequest(BaseModel):
    oid: str
    query: str
    doc_id: str
    relevant: bool
    comments: Optional[str] = None

@router.post("/search-result")
async def record_feedback(feedback: FeedbackRequest):
    log_feedback(feedback.dict())
    return {"status": "success", "message": "Feedback recorded."}
