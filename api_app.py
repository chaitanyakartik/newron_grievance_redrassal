from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from utils.chat_utils import (query_classifier,
                            add_to_chat_history,
                            get_history_from_sesh_id, 
                            check_if_final_department,
                            check_if_final_department_id)
import uvicorn

app = FastAPI()

import os
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    if await check_if_final_department_id(request.session_id)== True:
        import uuid
        return{"result": request.query, 
               "path": "nothing here",
               "sesh_id": str(uuid.uuid4())}
    
    try:
        await add_to_chat_history(request.session_id, "user", request.query)

        # Call the query_classifier function
        result, path = await query_classifier(
            query=request.query,
            chat_session_id=request.session_id
        )

        await add_to_chat_history(request.session_id, "assistant", result)

        print(path)

        dept_res=result

        if await check_if_final_department(path)== True:
            response = await get_chat_history(session_id=request.session_id)
            dept_res = response.get("dept_res", "")

        return {"result": dept_res,
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

@app.get("/chat_history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        # Initialize dept_res at the very beginning to avoid "referenced before assignment"
        dept_res = ""
        
        # Get history and path
        history, path = await get_history_from_sesh_id(session_id)
        
        if history is None:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Check if path is valid and iterable
        if path and isinstance(path, list):
            c = 1
            for dept in path:
                dept_res += f"Department Level: {c} Department Name: {dept}\n\n"
                c += 1
        else:
            dept_res = "No department path available"

        return {
            "session_id": session_id,
            "history": history,
            "path": path if path else [],
            "dept_res": dept_res
        }
    except Exception as e:
        logger.error(f"Error in get_chat_history: {str(e)}")
        return {"error": str(e), "dept_res": "Error retrieving department resolution", "path": []}
    
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("api_app:app", host="127.0.0.1", port=8000, reload=True)
