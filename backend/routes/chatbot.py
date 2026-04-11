from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# This lets Python find the layers/ folder
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from layers.layer4_chatbot.chatbot import chat_with_data

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    table_name: str


class ChatResponse(BaseModel):
    success: bool
    question: str
    sql: str | None
    data: dict | None
    error: str | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Accepts a plain English question and a table name.
    Returns the generated SQL and query results.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    if not request.table_name.strip():
        raise HTTPException(status_code=400, detail="Table name cannot be empty.")

    result = chat_with_data(
        user_question=request.question,
        table_name=request.table_name
    )

    return ChatResponse(
        success=result["success"],
        question=result["question"],
        sql=result.get("sql"),
        data=result.get("data"),
        error=result.get("error")
    )


@router.get("/chat/health")
async def chat_health():
    """Simple check to confirm the chatbot route is working."""
    return {"status": "chatbot route is live"}