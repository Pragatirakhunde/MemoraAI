from app.ai_engine.graph.nodes import generate_answer, retrieve_knowledge
from app.ai_engine.graph.workflow import build_agent_graph


class AgentService:

    @staticmethod
    def run(
        db,
        query,
        organization_id,
        conversation_history=None,
    ):

        def retrieval_node(state):
            return retrieve_knowledge(state, db)

        def generation_node(state):
            return generate_answer(state)

        graph = build_agent_graph(
            retrieval_node=retrieval_node,
            generation_node=generation_node,
        )

        return graph.invoke(
            {
                "query": query,
                "organization_id": organization_id,
                "conversation_history": conversation_history or [],
            }
        )