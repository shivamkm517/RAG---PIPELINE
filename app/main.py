import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.memory.database import Base, engine, SessionLocal
from app.memory.repository import (
    create_thread,
    get_all_threads,
    get_thread_by_id,
    get_thread_messages,
    delete_thread,
)
from app.chains.query_chain import answer_query

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PaperPilot RAG Chat API", version="1.0.0")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic Schemas
class CreateThreadRequest(BaseModel):
    title: str | None = None


class ChatRequest(BaseModel):
    thread_id: int | None = None
    message: str


# API Endpoints
@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "PaperPilot RAG Chat"}


@app.get("/api/threads")
def list_threads(db: Session = Depends(get_db)):
    threads = get_all_threads(db)
    return [
        {
            "id": t.id,
            "title": t.title or f"Chat #{t.id}",
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        }
        for t in threads
    ]


@app.post("/api/threads")
def new_thread(req: CreateThreadRequest = CreateThreadRequest(), db: Session = Depends(get_db)):
    thread = create_thread(db, title=req.title or "New Chat")
    return {
        "id": thread.id,
        "title": thread.title,
        "created_at": thread.created_at.isoformat() if thread.created_at else None,
    }


@app.get("/api/threads/{thread_id}")
def get_thread(thread_id: int, db: Session = Depends(get_db)):
    thread = get_thread_by_id(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    messages = get_thread_messages(db, thread_id)
    return {
        "id": thread.id,
        "title": thread.title or f"Chat #{thread.id}",
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }


@app.delete("/api/threads/{thread_id}")
def remove_thread(thread_id: int, db: Session = Depends(get_db)):
    success = delete_thread(db, thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"success": True, "message": "Thread deleted"}


@app.post("/api/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    
    thread_id = req.thread_id
    if not thread_id:
        thread = create_thread(db, title="New Chat")
        thread_id = thread.id
    else:
        thread = get_thread_by_id(db, thread_id)
        if not thread:
            thread = create_thread(db, title="New Chat")
            thread_id = thread.id
    
    result = answer_query(req.message.strip(), thread_id)
    
    # Refresh thread title info
    updated_thread = get_thread_by_id(db, thread_id)
    title = updated_thread.title if updated_thread else "Chat"

    return {
        "thread_id": thread_id,
        "title": title,
        "answer": result["answer"],
        "route": result["route"],
    }


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    upload_dir = Path("data/raw")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
        
    return {
        "filename": file.filename,
        "status": "uploaded",
        "message": f"Successfully uploaded {file.filename} to data/raw/",
    }


# Serve static web interface
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    def read_root():
        return FileResponse(static_dir / "index.html")
