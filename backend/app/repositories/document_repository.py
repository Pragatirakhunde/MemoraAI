from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from datetime import datetime


class DocumentRepository:

    @staticmethod
    def get_by_source_file(
        db: Session,
        source_file_id: int,
    ) -> Document | None:

        statement = select(Document).where(
            Document.source_file_id == source_file_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_id(
        db: Session,
        document_id: int,
        organization_id: int,
    ) -> Document | None:

        statement = select(Document).where(
            Document.id == document_id,
            Document.organization_id == organization_id,
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        organization_id: int,
    ) -> list[Document]:

        statement = (
            select(Document)
            .where(
                Document.organization_id == organization_id
            )
            .order_by(Document.id)
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def create(
        db: Session,
        organization_id: int,
        data_source_id: int,
        source_file_id: int,
        title: str,
        file_path: str,
        extension: str,
        content: str,
        checksum: str,
    ) -> Document:

        document = Document(
            organization_id=organization_id,
            data_source_id=data_source_id,
            source_file_id=source_file_id,
            title=title,
            file_path=file_path,
            extension=extension,
            content=content,
            checksum=checksum,
            metadata_json={},
            status="active",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def update(
        db: Session,
        document: Document,
        content: str,
        checksum: str,
        title: str,
    ) -> Document:

        document.content = content
        document.checksum = checksum
        document.title = title
        document.status = "active"

        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def mark_deleted(
        db: Session,
        document: Document,
    ) -> None:

        document.status = "deleted"

        db.commit()
        db.refresh(document)

    @staticmethod
    def update_processing_status(
        db: Session,
        document: Document,
        status: str,
        error: str | None = None,
    ) -> Document:

        document.processing_status = status
        document.processing_error = error

        if status == "completed":
            document.processed_at = datetime.utcnow()

        db.commit()
        db.refresh(document)

        return document