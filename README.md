# Agentic AI PDF Analyzer
### Multi-Agent Document Intelligence System

A state-of-the-art document analysis system powered by **LangGraph** agents, **FastAPI**, and **React**.

## 🏗 System Architecture

```
Frontend (React + Vite)
  │
  └── [Upload PDF] 
        │
  (HTTP /analyze-pdf)
        ↓
Backend (FastAPI)
  │
  ├── PDF Processing (PyPDF + Tesseract Fallback)
  │
  └── LangGraph Orchestrator
        ├── 1. Classifier Agent (Identifies doc type)
        ├── 2. Extraction Agent (Pulls key sections)
        ├── 3. Summarization Agent (Generates summary)
        └── 4. Insight Agent (Risks & Questions)
  │
  └── SQLite (Persist results)
```

## 🚀 Features

- **Multi-Agent Orchestration**: Deterministic flow using LangGraph.
- **Rich Aesthetics**: Glassmorphism UI with smooth animations.
- **Deep Analysis**: Extracts structure, summarizes, and generates strategic insights.
- **Responsive**: Works on desktop and mobile.

## 🛠 Prerequisites

1. **Python 3.10+**
2. **Node.js 18+**
3. **OpenRouter API Key** (for LLM access)

## 📦 Installation & Setup

### 1. Backend Setup

```bash
cd backend
# Create virtual environment (optional but recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment
# Rename .env if needed and add your key:
# OPENROUTER_API_KEY=sk-or-v1-...
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

## ▶ Running the Application

### Start Backend
In the `backend` directory:
```bash
python main.py
# Server starts at http://localhost:8000
```

### Start Frontend
In the `frontend` directory:
```bash
npm run dev
# App starts at http://localhost:5173
```

## 📝 Notes
- **OCR Support**: Tesseract is integrated but requires the Tesseract binary installed on your system and added to PATH. 
- **LLM**: Defaults to `google/gemini-2.0-flash-001` via OpenRouter. You can change this in `backend/.env`.
