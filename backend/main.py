from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import shutil
import os
import uuid
from dotenv import load_dotenv

from core.graph import app_graph
from core.pdf import extract_text_from_pdf, chunk_text
from core.state import DocumentState

from core.db import init_db, save_analysis, save_analytics_session, get_analytics_sessions, get_analytics_summary
from core.analytics import AnalyticsSession

load_dotenv()

# Initialize DB (will create tables if missing)
init_db()

app = FastAPI(title="Agentic AI PDF Analyzer", version="1.0")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeResponse(BaseModel):
    document_type: str
    summary: str
    key_sections: Dict[str, Any]
    insights: List[str]
    agent_trace: List[str]
    session_id: str
    analytics: Optional[Dict[str, Any]] = None

@app.post("/analyze-pdf", response_model=AnalyzeResponse)
async def analyze_pdf(
    file: UploadFile = File(...),
    user_question: Optional[str] = Form(None)
):
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Initialize analytics session
    analytics_session = AnalyticsSession(session_id)
    analytics_session.set_metadata(filename=file.filename)
    
    try:
        content = await file.read()
        raw_text = extract_text_from_pdf(content)
        
        if not raw_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. It might be empty or scanned images without OCR enabled.")
            
        chunks = chunk_text(raw_text)
        
        # Initialize State with analytics trackers
        initial_state: DocumentState = {
            "raw_text": raw_text,
            "chunks": chunks,
            "document_type": None,
            "extracted_sections": {},
            "summary": None,
            "insights": [],
            "agent_logs": [f"System: Received file {file.filename}. Text length: {len(raw_text)} chars."],
            "_token_tracker": analytics_session.token_tracker,
            "_agent_tracker": analytics_session.agent_tracker
        }
        
        # Run Graph
        result_state = app_graph.invoke(initial_state)
        
        # Generate analytics report
        analytics_report = analytics_session.get_full_report()
        
        response_data = {
            "document_type": result_state.get("document_type", "Unknown"),
            "summary": result_state.get("summary", "No summary available"),
            "key_sections": result_state.get("extracted_sections", {}),
            "insights": result_state.get("insights", []),
            "agent_trace": result_state.get("agent_logs", []),
            "session_id": session_id,
            "analytics": analytics_report
        }

        # Save to SQLite
        save_analysis(file.filename, response_data, session_id)
        save_analytics_session(analytics_report)
        
        return AnalyzeResponse(**response_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/sessions")
async def get_sessions(limit: int = 10):
    """Get recent analytics sessions"""
    sessions = get_analytics_sessions(limit)
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "filename": s.filename,
                "start_timestamp": s.start_timestamp.isoformat() if s.start_timestamp else None,
                "total_tokens": s.total_tokens,
                "estimated_cost_usd": s.estimated_cost_usd,
                "total_duration_seconds": s.total_duration_seconds,
                "successful_agents": s.successful_agents,
                "failed_agents": s.failed_agents
            }
            for s in sessions
        ]
    }

@app.get("/analytics/summary")
async def get_summary():
    """Get overall analytics summary"""
    return get_analytics_summary()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
