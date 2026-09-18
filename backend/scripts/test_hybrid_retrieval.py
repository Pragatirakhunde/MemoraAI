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

    result = service.retrieve(
        db=db,
        query=query,
        organization_id=1,
        limit=5,
    )

    print("\n" + "=" * 60)
    print("HYBRID RETRIEVAL")
    print("=" * 60)

    print("\nQuery:")
    print(result.query)

    print("\nDetected Entities:")

    for entity in result.entities:
        print(
            f"- {entity['type']}: "
            f"{entity['name']} "
            f"({entity['confidence']})"
        )

    print("\n--- Vector Results ---")

    for item in result.vector_results:

        print(
            f"\nDocument: {item.title}"
        )

        print(
            f"Score: {item.score}"
        )

        print(
            f"Chunk: {item.chunk_id}"
        )

        print(
            f"Content: {item.content[:300]}"
        )

    print("\n--- Graph Results ---")

    for item in result.graph_results:

        print(
            f"- {item.entity_name} "
            f"-[:{item.relationship}]-> "
            f"{item.related_name}"
        )

finally:
    db.close()