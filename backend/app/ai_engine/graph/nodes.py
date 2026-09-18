from sqlalchemy.orm import Session

from app.ai_engine.prompt_builder import PromptBuilder
from app.ai_engine.response_formatter import ResponseFormatter
from app.services.hybrid_retrieval_service import HybridRetrievalService
from app.services.llm_service import LLMService


def retrieve_knowledge(state: dict, db: Session) -> dict:
    """
    Retrieve organizational knowledge using hybrid vector + graph retrieval
    and construct a grounded prompt for the LLM.
    """

    query = state["query"]
    organization_id = state["organization_id"]

    service = HybridRetrievalService()

    # -------------------------------------------------
    # Hybrid retrieval
    # -------------------------------------------------

    retrieval = service.retrieve(
        db=db,
        query=query,
        organization_id=organization_id,
        limit=5,
    )

    # -------------------------------------------------
    # Context fusion
    # -------------------------------------------------

    fused = service.retrieve_fused_context(
        db=db,
        query=query,
        organization_id=organization_id,
        limit=5,
        max_context_items=10,
    )

    # -------------------------------------------------
    # Build grounded prompt
    # -------------------------------------------------

    fused_context = [
        {
            "source_type": item.source_type,
            "score": item.score,
            "content": item.content,
            "reference": item.reference,
        }
        for item in fused
    ]

    prompt = PromptBuilder.build_grounded_prompt(
        query=query,
        fused_context=fused_context,
        entities=retrieval.entities,
        conversation_history=state.get(
            "conversation_history",
            [],
        ),
    )

    # -------------------------------------------------
    # Return retrieval state
    # -------------------------------------------------

    return {
        "entities": retrieval.entities,

        "vector_results": [
            {
                "document_id": item.document_id,
                "chunk_id": item.chunk_id,
                "title": item.title,
                "content": item.content,
                "score": item.score,
                "reference": item.reference,
            }
            for item in retrieval.vector_results
        ],

        "graph_results": [
            {
                "entity_name": item.entity_name,
                "entity_type": item.entity_type,
                "relationship": item.relationship,
                "related_name": item.related_name,
                "related_type": item.related_type,
                "hops": item.hops,
                "confidence": item.confidence,
            }
            for item in retrieval.graph_results
        ],

        "fused_context": fused_context,

        "prompt": prompt,
    }


def generate_answer(state: dict) -> dict:
    """
    Generate a grounded answer using the LLM and format
    references from the retrieved context.
    """

    prompt = state.get("prompt")

    # -------------------------------------------------
    # Validate prompt
    # -------------------------------------------------

    if not prompt:
        return {
            "answer": "No grounded prompt was generated.",
            "references": [],
            "error": "Missing prompt",
        }

    try:
        # -------------------------------------------------
        # LLM generation
        # -------------------------------------------------

        llm_service = LLMService()

        answer = llm_service.generate(prompt)

        # -------------------------------------------------
        # Reference formatting
        # -------------------------------------------------

        references = ResponseFormatter.format_references(
            state.get("fused_context", [])
        )

        return {
            "answer": answer,
            "references": references,
            "error": None,
        }

    except Exception as exc:
        return {
            "answer": "",
            "references": [],
            "error": str(exc),
        }