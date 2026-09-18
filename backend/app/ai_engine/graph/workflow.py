from langgraph.graph import END, START, StateGraph

from app.ai_engine.graph.state import AgentState


def build_agent_graph(retrieval_node, generation_node):
    workflow = StateGraph(AgentState)

    workflow.add_node("retrieve", retrieval_node)
    workflow.add_node("generate", generation_node)

    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()