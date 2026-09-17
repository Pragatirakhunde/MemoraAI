from app.database.postgres import SessionLocal
from app.services.search_service import SearchService


db = SessionLocal()

try:

    service = SearchService()

    query = (
        "Which database is used "
        "by the Inventory Management project?"
    )

    results = service.search(
        db=db,
        query=query,
        organization_id=1,
        limit=5,
    )

    print("\nQuery:")
    print(query)

    print("\nResults:")

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"\n--- Result {index} ---"
        )

        print(
            "Score:",
            result["score"],
        )

        print(
            "Document:",
            result["title"],
        )

        print(
            "Document ID:",
            result["document_id"],
        )

        print(
            "Chunk ID:",
            result["chunk_id"],
        )

        print(
            "Reference:",
            result["reference"],
        )

        print(
            "Content:"
        )

        print(
            result["content"]
        )

finally:
    db.close()