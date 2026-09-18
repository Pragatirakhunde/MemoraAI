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

    context = service.retrieve_fused_context(
        db=db,
        query=query,
        organization_id=1,
        limit=5,
        max_context_items=10,
    )

    print("\n" + "=" * 60)
    print("FUSED CONTEXT")
    print("=" * 60)

    for index, item in enumerate(
        context,
        start=1,
    ):

        print(
            f"\n--- Context {index} ---"
        )

        print(
            "Source:",
            item.source_type,
        )

        print(
            "Score:",
            item.score,
        )

        print(
            "Content:",
            item.content,
        )

        print(
            "Reference:",
            item.reference,
        )

finally:
    db.close()