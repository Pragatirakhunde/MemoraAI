from app.database.postgres import SessionLocal

from app.services.hybrid_retrieval_service import (
    HybridRetrievalService,
)


db = SessionLocal()

try:

    query = (
        "Which database and technologies "
        "are used by the Inventory Management project?"
    )

    service = HybridRetrievalService()

    retrieval = service.retrieve(
        db=db,
        query=query,
        organization_id=1,
        limit=5,
    )

    fused = service.retrieve_fused_context(
        db=db,
        query=query,
        organization_id=1,
        limit=5,
        max_context_items=10,
    )

    print("\nQUERY")
    print(query)

    print(
        "\nVector results:",
        len(retrieval.vector_results),
    )

    print(
        "Graph results:",
        len(retrieval.graph_results),
    )

    print(
        "Fused evidence:",
        len(fused),
    )

    print("\nSources:")

    for item in fused:
        print(
            f"- {item.source_type} "
            f"(score={item.score})"
        )

finally:
    db.close()