from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import shutil
import os
from dotenv import load_dotenv

from core.graph import app_graph
from core.pdf import extract_text_from_pdf, chunk_text
from core.state import DocumentState

from core.db import init_db, save_analysis

load_dotenv()

# Initialize DB
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

@app.post("/analyze-pdf", response_model=AnalyzeResponse)
async def analyze_pdf(
    file: UploadFile = File(...),
    user_question: Optional[str] = Form(None)
):
    try:
        content = await file.read()
        raw_text = extract_text_from_pdf(content)
        
        if not raw_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. It might be empty or scanned images without OCR enabled.")
            
        chunks = chunk_text(raw_text)
        
        # Initialize State
        initial_state: DocumentState = {
            "raw_text": raw_text,
            "chunks": chunks,
            "document_type": None,
            "extracted_sections": {},
            "summary": None,
            "insights": [],
            "agent_logs": [f"System: Received file {file.filename}. Text length: {len(raw_text)} chars."]
        }
        
        # Run Graph
        result_state = app_graph.invoke(initial_state)
        
        response_data = {
            "document_type": result_state.get("document_type", "Unknown"),
            "summary": result_state.get("summary", "No summary available"),
            "key_sections": result_state.get("extracted_sections", {}),
            "insights": result_state.get("insights", []),
            "agent_trace": result_state.get("agent_logs", [])
        }

        # Save to SQLite
        save_analysis(file.filename, response_data)
        
        return AnalyzeResponse(**response_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
