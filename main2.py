from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from utils.chat_utils import query_classifier
import uvicorn

app = FastAPI()

# Define the HistoryItem model
class HistoryItem(BaseModel):
    role: str
    content: str

# Define the ChatRequest model
class ChatRequest(BaseModel):
    query: str
    history: Optional[List[HistoryItem]] = None
    dept_path: Optional[List[str]] = None  # Optional department path

@app.post("/classify")
async def classify_grievance(request: ChatRequest):
    """
    Endpoint to classify a grievance query.
    """
    try:
        # Convert history to the required format
        history=[]
        for item in request.history:
            history.append(HistoryItem(role=item.role, content=item.content))

        # Call the query_classifier function
        result = await query_classifier(
            query=request.query,
            history=history,
            dept_path=request.dept_path or []
        )

        return {"result": result}

    except Exception as e:
        # Handle exceptions and return a 500 error
        raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)