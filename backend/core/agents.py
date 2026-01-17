import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.callbacks import BaseCallbackHandler
from core.state import DocumentState
import json

# Initialize OpenRouter LLM
# Note: User must provide OPENROUTER_API_KEY in .env
# We use a default lightweight model, but allow configuration.
MODEL_NAME = os.getenv("LLM_MODEL", "google/gemini-2.0-flash-001") # flexible default
BASE_URL = "https://openrouter.ai/api/v1"
API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_llm(callbacks=None):
    if not API_KEY:
        # Fallback only for demonstration or specific envs; ideally should raise error or handle gracefully
        print("Warning: OPENROUTER_API_KEY not found.")
        
    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=API_KEY,
        openai_api_base=BASE_URL,
        temperature=0.1,
        callbacks=callbacks or []
    )

# --- Agent 1: Document Classifier ---
def document_classifier_agent(state: DocumentState) -> DocumentState:
    import time
    start_time = time.time()
    
    # Get analytics trackers from state
    token_tracker = state.get('_token_tracker')
    agent_tracker = state.get('_agent_tracker')
    
    if agent_tracker:
        agent_tracker.start_agent("classifier", state)
    
    callbacks = [token_tracker] if token_tracker else []
    llm = get_llm(callbacks=callbacks)
    
    # We use a snippet of text to classify to save tokens, or full text if reasonable.
    # For classification, the first 2000 chars are usually enough + some middle/end?
    # Let's use the first chunk or first 3000 chars of raw text.
    text_sample = state["raw_text"][:3000]

    if agent_tracker:
        agent_tracker.start_agent(
            "classifier", 
            state, 
            additional_info={"sample_length": len(text_sample)}
        )
    
    callbacks = [token_tracker] if token_tracker else []
    llm = get_llm(callbacks=callbacks)

    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert Document Classifier Agent. 
        Analyze the following text sample from a document and classify its type.
        
        Possible types: Contract, Research Paper, Technical Report, Notes, Legal Document, Invoice, Resume, Other.
        
        Text Sample:
        {text}
        
        Return ONLY a JSON object with the key "document_type".
        Example: {{"document_type": "Contract"}}
        """
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({"text": text_sample})
        doc_type = result.get("document_type", "Unknown")
        log = f"Classifier Agent: Identified document as {doc_type}"
        success = True
    except Exception as e:
        doc_type = "Unknown"
        log = f"Classifier Agent: Failed to classify. Error: {str(e)}"
        success = False

    result_state = {
        "document_type": doc_type,
        "agent_logs": state.get("agent_logs", []) + [log]
    }
    
    if agent_tracker:
        agent_tracker.end_agent(
            result_state, 
            success=success,
            additional_info={"classified_type": doc_type}
        )
    
    return result_state

# --- Agent 2: Content Extraction Agent ---
def content_extraction_agent(state: DocumentState) -> DocumentState:
    import time
    start_time = time.time()
    
    # Get analytics trackers from state
    token_tracker = state.get('_token_tracker')
    agent_tracker = state.get('_agent_tracker')
    
    if agent_tracker:
        agent_tracker.start_agent("extractor", state)
    
    callbacks = [token_tracker] if token_tracker else []
    llm = get_llm(callbacks=callbacks)
    
    doc_type = state["document_type"]
    text_sample = state["raw_text"]  
    # For extraction, we might need more context. 
    # If text is huge, we might need a map-reduce strategy or just process the first N chunks.
    # For simplicity in this demo, we assume the text fits context or we truncate.
    # A robust production system would iterate over chunks.
    # Let's limit to 10k chars for this demo to ensure speed and low cost.
    processing_text = text_sample[:10000] 

    if agent_tracker:
        agent_tracker.start_agent(
            "extractor", 
            state,
            additional_info={
                "document_type": doc_type,
                "processing_length": len(processing_text)
            }
        )
    
    callbacks = [token_tracker] if token_tracker else []
    llm = get_llm(callbacks=callbacks)

    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert Content Extraction Agent.
        The document type is determined to be: {doc_type}.
        
        Extract key sections and structured content relevant to this document type.
        - If Contract: clauses, obligations, deadlines.
        - If Report: sections, key findings.
        - If Notes: bullet points, main topics.
        
        Text content:
        {text}
        
        Return a JSON object with a key "sections" mapping section names to content summaries or extracts.
        """
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({"doc_type": doc_type, "text": processing_text})
        sections = result.get("sections", {})
        log = f"Extraction Agent: Extracted {len(sections)} key sections."
        success = True
    except Exception as e:
        sections = {}
        log = f"Extraction Agent: Extraction failed. Error: {str(e)}"
        success = False
        
    result_state = {
        "extracted_sections": sections,
        "agent_logs": state["agent_logs"] + [log]
    }
    
    if agent_tracker:
        agent_tracker.end_agent(
            result_state, 
            success=success,
            additional_info={"sections_found": len(sections)}
        )
    
    return result_state

# --- Agent 3: Summarization Agent ---
def summarization_agent(state: DocumentState) -> DocumentState:
    import time
    start_time = time.time()
    
    # Get analytics trackers from state
    token_tracker = state.get('_token_tracker')
    agent_tracker = state.get('_agent_tracker')
    
    if agent_tracker:
        agent_tracker.start_agent("summarizer", state)
    
    callbacks = [token_tracker] if token_tracker else []
    llm = get_llm(callbacks=callbacks)
    
    # In a real chunk-based system, we would summarize chunks and then aggregate.
    # Here we perform a direct summarization on the potentially truncated text 
    # or the aggregated chunks if we implemented a map-reduce. 
    # We will use the raw text (truncated if massive).
    
    text_content = state["raw_text"][:15000] 

    if agent_tracker:
        agent_tracker.start_agent(
            "summarizer", 
            state,
            additional_info={"input_length": len(text_content)}
        )
    
    callbacks = [token_tracker] if token_tracker else []
    llm = get_llm(callbacks=callbacks)

    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert Summarization Agent.
        Provide a concise, comprehensive summary of the document.
        Focus on the main objectives, outcomes, and key entities involved.
        
        Document Text:
        {text}
        
        Return a JSON object with `summary` key.
        """
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({"text": text_content})
        summary = result.get("summary", "No summary generated.")
        log = "Summarization Agent: Generated summary."
        success = True
    except Exception as e:
        summary = "Error generating summary."
        log = f"Summarization Agent: Failed. Error: {str(e)}"
        success = False

    result_state = {
        "summary": summary,
        "agent_logs": state["agent_logs"] + [log]
    }
    
    if agent_tracker:
        agent_tracker.end_agent(
            result_state, 
            success=success,
            additional_info={"summary_length": len(summary) if summary else 0}
        )
    
    return result_state

# --- Agent 4: Insight Generator Agent ---
def insight_generator_agent(state: DocumentState) -> DocumentState:
    import time
    start_time = time.time()
    
    # Get analytics trackers from state
    token_tracker = state.get('_token_tracker')
    agent_tracker = state.get('_agent_tracker')
    
    if agent_tracker:
        agent_tracker.start_agent("insight_generator", state)
    
    callbacks = [token_tracker] if token_tracker else []
    llm = get_llm(callbacks=callbacks)
    
    summary = state.get("summary", "")
    sections = state.get("extracted_sections", {})
    doc_type = state.get("document_type", "Unknown") # Access from state directly

    if agent_tracker:
        agent_tracker.start_agent(
            "insight_generator", 
            state,
            additional_info={
                "has_summary": bool(summary),
                "num_sections": len(sections)
            }
        )
    
    callbacks = [token_tracker] if token_tracker else []
    llm = get_llm(callbacks=callbacks)

    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert Insight Generator Agent.
        Based on the document summary, type, and extracted sections, generate strategic insights.
        
        1. Generate 3 key questions a user might have.
        2. Identify potentially risky areas or missing information (if applicable).
        3. Suggest follow-up actions.
        
        Document Type: {doc_type}
        Summary: {summary}
        Sections: {sections}
        
        Return a JSON object with a key "insights" which is a LIST of strings.
        Example: ["Risk: Missing termination date", "Question: Who is the primary stakeholder?", "Action: Review clause 4.2"]
        """
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        # Pass doc_type to invoke
        result = chain.invoke({"summary": summary, "sections": json.dumps(sections), "doc_type": doc_type})
        insights = result.get("insights", [])
        log = f"Insight Agent: Generated {len(insights)} insights."
        success = True
    except Exception as e:
        insights = []
        log = f"Insight Agent: Failed. Error: {str(e)}"
        success = False

    result_state = {
        "insights": insights,
        "agent_logs": state["agent_logs"] + [log]
    }
    
    if agent_tracker:
        agent_tracker.end_agent(
            result_state, 
            success=success,
            additional_info={"num_insights": len(insights)}
        )
    
    return result_state
