from app.database.postgres import SessionLocal

from app.repositories.document_repository import (
    DocumentRepository,
)

from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)

from app.services.vector_service import VectorService

from app.database.qdrant import (
    COLLECTION_NAME,
    qdrant_client,
)


db = SessionLocal()

try:

    documents = DocumentRepository.get_all(
        db,
        organization_id=1,
    )

    if not documents:
        print("No documents found.")
        print("Run a sync first.")
    else:

        document = documents[0]

        chunks = (
            DocumentChunkRepository.get_by_document(
                db,
                document.id,
            )
        )

        if not chunks:
            print("No chunks found.")
            print("Process the document first.")

        else:

            print(
                f"Document: {document.title}"
            )

            print(
                f"Chunks: {len(chunks)}"
            )

            vector_service = VectorService()

            vector_service.upsert_chunks(
                document=document,
                chunks=chunks,
            )

            print(
                "\nVectors stored successfully."
            )

            info = qdrant_client.get_collection(
                collection_name=COLLECTION_NAME
            )

            print(
                "Qdrant points:",
                info.points_count,
            )

finally:
    db.close()