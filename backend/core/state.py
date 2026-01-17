from typing import TypedDict, List, Dict, Any, Optional

class DocumentState(TypedDict):
    """
    Global state shared between agents in the LangGraph workflow.
    """
    raw_text: str
    chunks: List[str]
    document_type: Optional[str]
    extracted_sections: Dict[str, Any]
    summary: Optional[str]
    insights: List[str]
    agent_logs: List[str]
