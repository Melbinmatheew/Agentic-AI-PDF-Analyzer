from sqlalchemy import create_engine, Column, Integer, String, JSON, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = "sqlite:///./agentic_pdf.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    document_type = Column(String)
    summary = Column(Text)
    key_sections = Column(JSON)
    insights = Column(JSON)
    agent_trace = Column(JSON)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_analysis(filename: str, result_data: dict):
    db = SessionLocal()
    try:
        db_record = AnalysisResult(
            filename=filename,
            document_type=result_data.get("document_type"),
            summary=result_data.get("summary"),
            key_sections=result_data.get("key_sections"),
            insights=result_data.get("insights"),
            agent_trace=result_data.get("agent_trace")
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record.id
    except Exception as e:
        print(f"Error saving to DB: {e}")
    finally:
        db.close()
