from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import asyncio

from utils.chat_utils import handle_chat

app = FastAPI()

class HistoryItem(BaseModel):
    # Define fields as per your History model in chat_utils.py
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[HistoryItem]] = None

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        result = await handle_chat(request.query, request.history)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))