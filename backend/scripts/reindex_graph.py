from app.database.postgres import SessionLocal

from app.repositories.document_repository import (
    DocumentRepository,
)

from app.services.graph_indexing_service import (
    GraphIndexingService,
)


db = SessionLocal()

try:

    documents = DocumentRepository.get_all(
        db,
        organization_id=1,
    )

    if not documents:
        print("No documents found.")
    else:

        print(
            f"Found {len(documents)} documents."
        )

        for document in documents:

            print(
                f"\nIndexing: "
                f"{document.id} - "
                f"{document.title}"
            )

            GraphIndexingService.index_document(
                db,
                document,
            )

        print(
            "\nGraph reindex completed."
        )

finally:
    db.close()