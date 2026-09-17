from app.database.postgres import SessionLocal

from app.repositories.document_repository import (
    DocumentRepository,
)

from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)

from app.services.document_processing_service import (
    DocumentProcessingService,
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

        document = documents[0]

        print(
            f"Processing: "
            f"{document.id} - {document.title}"
        )

        DocumentProcessingService.process_document(
            db,
            document,
        )

        chunks = (
            DocumentChunkRepository.get_by_document(
                db,
                document.id,
            )
        )

        print(
            "\nProcessing Status:",
            document.processing_status,
        )

        print(
            "Chunks Created:",
            len(chunks),
        )

        for chunk in chunks:

            print(
                f"\nChunk {chunk.chunk_index}"
            )

            print(chunk.content[:300])

finally:
    db.close()