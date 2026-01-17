from langgraph.graph import StateGraph, END
from core.state import DocumentState
from core.agents import (
    document_classifier_agent,
    content_extraction_agent,
    summarization_agent,
    insight_generator_agent
)

def create_graph():
    workflow = StateGraph(DocumentState)
    
    # Add Nodes
    workflow.add_node("classifier", document_classifier_agent)
    workflow.add_node("extractor", content_extraction_agent)
    workflow.add_node("summarizer", summarization_agent)
    workflow.add_node("insight_generator", insight_generator_agent)
    
    # Define Edges (Linear Flow)
    workflow.set_entry_point("classifier")
    workflow.add_edge("classifier", "extractor")
    workflow.add_edge("extractor", "summarizer")
    workflow.add_edge("summarizer", "insight_generator")
    workflow.add_edge("insight_generator", END)
    
    return workflow.compile()

app_graph = create_graph()
