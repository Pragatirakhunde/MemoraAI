from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.data_source_file import DataSourceFile


class DataSourceFileRepository:

    @staticmethod
    def get_by_path(
        db: Session,
        data_source_id: int,
        file_path: str,
    ) -> DataSourceFile | None:

        statement = select(DataSourceFile).where(
            DataSourceFile.data_source_id == data_source_id,
            DataSourceFile.file_path == file_path,
        )

        return db.scalar(statement)

    @staticmethod
    def get_all_by_source(
        db: Session,
        data_source_id: int,
    ) -> list[DataSourceFile]:

        statement = select(DataSourceFile).where(
            DataSourceFile.data_source_id == data_source_id
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def create(
        db: Session,
        data_source_id: int,
        file_path: str,
        file_name: str,
        extension: str,
        size: int,
        checksum: str,
        last_modified_at: datetime,
    ) -> DataSourceFile:

        now = datetime.utcnow()

        file_record = DataSourceFile(
            data_source_id=data_source_id,
            file_path=file_path,
            file_name=file_name,
            extension=extension,
            size=size,
            checksum=checksum,
            last_modified_at=last_modified_at,
            last_seen_at=now,
            status="active",
        )

        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        return file_record

    @staticmethod
    def update(
        db: Session,
        file_record: DataSourceFile,
        size: int,
        checksum: str,
        last_modified_at: datetime,
    ):

        file_record.size = size
        file_record.checksum = checksum
        file_record.last_modified_at = last_modified_at
        file_record.last_seen_at = datetime.utcnow()
        file_record.status = "active"

        db.commit()
        db.refresh(file_record)

        return file_record

    @staticmethod
    def mark_seen(
        db: Session,
        file_record: DataSourceFile,
    ):

        file_record.last_seen_at = datetime.utcnow()
        file_record.status = "active"

        db.commit()

    @staticmethod
    def mark_deleted(
        db: Session,
        file_record: DataSourceFile,
    ):

        file_record.status = "deleted"

        db.commit()