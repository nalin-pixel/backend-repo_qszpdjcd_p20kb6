import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document, get_documents, db
from schemas import Message

app = FastAPI(title="Live Chat Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Live Chat API ready"}

# Simple health + DB check
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Pydantic models for requests
class SendMessageRequest(BaseModel):
    room: str
    sender: str
    content: str

class MessagesResponse(BaseModel):
    messages: List[dict]

# Create a message
@app.post("/api/messages", response_model=dict)
async def send_message(payload: SendMessageRequest):
    data = payload.model_dump()
    data["timestamp"] = datetime.now(timezone.utc)
    # Validate against schema
    _ = Message(**data)
    inserted_id = create_document("message", data)
    return {"id": inserted_id}

# Get latest messages for a room, with optional since timestamp for polling
@app.get("/api/messages", response_model=MessagesResponse)
async def get_messages(
    room: str = Query("general"),
    since: Optional[str] = Query(None, description="ISO timestamp to fetch messages after")
):
    filter_query = {"room": room}
    if since:
        try:
            dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            filter_query["timestamp"] = {"$gt": dt}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'since' timestamp")

    docs = get_documents("message", filter_query, limit=None)
    # Sort by timestamp ascending
    docs.sort(key=lambda d: d.get("timestamp", datetime.min.replace(tzinfo=timezone.utc)))

    # Convert ObjectId and datetime to serializable
    def serialize(doc):
        d = dict(doc)
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
        ts = d.get("timestamp")
        if isinstance(ts, datetime):
            d["timestamp"] = ts.isoformat()
        return d

    return {"messages": [serialize(d) for d in docs]}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
