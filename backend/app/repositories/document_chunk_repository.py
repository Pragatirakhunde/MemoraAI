from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository:

    @staticmethod
    def get_by_document(
        db: Session,
        document_id: int,
    ) -> list[DocumentChunk]:

        statement = (
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id
            )
            .order_by(DocumentChunk.chunk_index)
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def delete_by_document(
        db: Session,
        document_id: int,
    ) -> None:

        db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document_id
            )
        )

        db.commit()

    @staticmethod
    def create(
        db: Session,
        document_id: int,
        chunk_index: int,
        content: str,
        checksum: str,
    ) -> DocumentChunk:

        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            character_count=len(content),
            checksum=checksum,
        )

        db.add(chunk)
        db.commit()
        db.refresh(chunk)

        return chunk