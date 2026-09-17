from app.database.postgres import SessionLocal
from app.database.qdrant import (
    COLLECTION_NAME,
)
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.vector_service import VectorService


db = SessionLocal()

try:
    vector_service = VectorService()

    documents = DocumentRepository.get_all(
        db,
        organization_id=1,
    )

    total = 0

    for document in documents:

        if document.status != "active":
            continue

        chunks = (
            DocumentChunkRepository.get_by_document(
                db,
                document.id,
            )
        )

        if not chunks:
            continue

        vector_service.upsert_chunks(
            document=document,
            chunks=chunks,
        )

        total += len(chunks)

        print(
            f"Indexed {len(chunks)} chunks "
            f"for document: {document.title}"
        )

    print(
        f"\nReindex complete. "
        f"Total chunks: {total}"
    )

finally:
    db.close()