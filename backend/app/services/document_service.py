from pathlib import Path

from sqlalchemy.orm import Session

from app.models.data_source_file import DataSourceFile
from app.models.document import Document
from app.repositories.document_repository import (
    DocumentRepository,
)


class DocumentService:

    @staticmethod
    def ingest_file(
        db: Session,
        organization_id: int,
        project_id: int | None,
        data_source_id: int,
        source_file: DataSourceFile,
        content: str,
    ) -> Document:

        document = DocumentRepository.get_by_source_file(
            db,
            source_file.id,
        )

        title = Path(
            source_file.file_name
        ).stem

        if document is None:

            document = DocumentRepository.create(
                db=db,
                organization_id=organization_id,
                project_id=project_id,
                data_source_id=data_source_id,
                source_file_id=source_file.id,
                title=title,
                file_path=source_file.file_path,
                extension=source_file.extension,
                content=content,
                checksum=source_file.checksum,
            )

        else:

            document = DocumentRepository.update(
                db=db,
                document=document,
                project_id=project_id,
                content=content,
                checksum=source_file.checksum,
                title=title,
            )

        return document

    @staticmethod
    def get_documents(
        db: Session,
        organization_id: int,
    ):
        return DocumentRepository.get_all(
            db,
            organization_id,
        )

    @staticmethod
    def get_document(
        db: Session,
        document_id: int,
        organization_id: int,
    ):
        return DocumentRepository.get_by_id(
            db,
            document_id,
            organization_id,
        )

    @staticmethod
    def get_accessible_documents(
        db: Session,
        organization_id: int,
        project_ids: list[int],
    ):
        return DocumentRepository.get_accessible(
            db=db,
            organization_id=organization_id,
            project_ids=project_ids,
        )

    @staticmethod
    def get_accessible_document(
        db: Session,
        document_id: int,
        organization_id: int,
        project_ids: list[int],
    ):
        return DocumentRepository.get_accessible_by_id(
            db=db,
            document_id=document_id,
            organization_id=organization_id,
            project_ids=project_ids,
        )