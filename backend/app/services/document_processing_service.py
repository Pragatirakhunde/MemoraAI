import hashlib

from sqlalchemy.orm import Session

from app.models.document import Document

from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)

from app.repositories.document_repository import (
    DocumentRepository,
)

from app.processors.document_processor import (
    DocumentProcessor,
)

from app.services.vector_service import (
    VectorService,
)


class DocumentProcessingService:

    @staticmethod
    def process_document(
        db: Session,
        document: Document,
    ):

        DocumentRepository.update_processing_status(
            db,
            document,
            "processing",
        )

        try:
            processor = DocumentProcessor()

            result = processor.process(
                document
            )

            # Get old chunks before deleting them.
            old_chunks = (
                DocumentChunkRepository.get_by_document(
                    db,
                    document.id,
                )
            )

            old_chunk_ids = [
                chunk.id
                for chunk in old_chunks
            ]

            # Remove old vectors from Qdrant.
            vector_service = VectorService()

            vector_service.delete_document_chunks(
                old_chunk_ids
            )

            # Remove old chunks from PostgreSQL.
            DocumentChunkRepository.delete_by_document(
                db,
                document.id,
            )

            # Create new chunks.
            new_chunks = []

            for index, chunk_content in enumerate(
                result.chunks
            ):

                checksum = hashlib.sha256(
                    chunk_content.encode("utf-8")
                ).hexdigest()

                chunk = (
                    DocumentChunkRepository.create(
                        db=db,
                        document_id=document.id,
                        chunk_index=index,
                        content=chunk_content,
                        checksum=checksum,
                    )
                )

                new_chunks.append(chunk)

            # Save extracted metadata.
            document.metadata_json = result.metadata

            db.commit()
            db.refresh(document)

            # Generate embeddings and store in Qdrant.
            vector_service.upsert_chunks(
                document=document,
                chunks=new_chunks,
            )

            # Mark processing as completed.
            DocumentRepository.update_processing_status(
                db,
                document,
                "completed",
            )

            return result

        except Exception as exc:

            DocumentRepository.update_processing_status(
                db,
                document,
                "failed",
                str(exc),
            )

            raise

    @staticmethod
    def get_chunks(
        db: Session,
        document_id: int,
    ):

        return (
            DocumentChunkRepository.get_by_document(
                db,
                document_id,
            )
        )