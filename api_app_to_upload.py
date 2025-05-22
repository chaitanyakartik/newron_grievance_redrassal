from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from utils.chat_utils import query_classifier,add_to_chat_history
import uvicorn

app = FastAPI()

# Define the HistoryItem model
class HistoryItem(BaseModel):
    role: str
    content: str

# Define the ChatRequest model
class ChatRequest(BaseModel):
    query: str
    session_id: str  # Optional session ID

@app.post("/continue_chat_classify")
async def classify_grievance(request: ChatRequest):
    """
    Endpoint to classify a grievance query.
    """
    try:

        await add_to_chat_history(request.session_id, "user", request.query)

        # Call the query_classifier function
        result, path = await query_classifier(
            query=request.query,
            chat_session_id=request.session_id
        )

        await add_to_chat_history(request.session_id, "assistant", result)

        return {"result": result,
                "path": path}

    except Exception as e:
        # Handle exceptions and return a 500 error
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/initiate_chat")
async def initiate_chat():
    """
    Endpoint to initiate a chat session.
    """
    # This could be used to initialize any resources or state for the chat session
    import uuid

    random_id = str(uuid.uuid4())

    return {
            "message": "Chat session initiated.",
            "session_id": random_id
            }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)