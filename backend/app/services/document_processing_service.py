import hashlib

from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.processors.document_processor import DocumentProcessor


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

            result = processor.process(document)

            DocumentChunkRepository.delete_by_document(
                db,
                document.id,
            )

            for index, chunk in enumerate(
                result.chunks
            ):
                checksum = hashlib.sha256(
                    chunk.encode("utf-8")
                ).hexdigest()

                DocumentChunkRepository.create(
                    db=db,
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    checksum=checksum,
                )

            document.metadata_json = result.metadata

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
        return DocumentChunkRepository.get_by_document(
            db,
            document_id,
        )