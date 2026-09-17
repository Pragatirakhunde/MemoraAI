from sqlalchemy.orm import Session

from app.repositories.data_source_repository import (
    DataSourceRepository,
)
from app.schemas.data_source import DataSourceCreate


class DataSourceService:

    @staticmethod
    def create(
        db: Session,
        organization_id: int,
        data: DataSourceCreate,
    ):

        allowed_types = {
            "local_directory",
            "git",
        }

        if data.source_type not in allowed_types:
            raise ValueError(
                "Unsupported data source type"
            )

        return DataSourceRepository.create(
            db=db,
            organization_id=organization_id,
            name=data.name,
            source_type=data.source_type,
            config=data.config,
        )

    @staticmethod
    def get_all(
        db: Session,
        organization_id: int,
    ):
        return DataSourceRepository.get_all(
            db,
            organization_id,
        )

    @staticmethod
    def get_by_id(
        db: Session,
        data_source_id: int,
        organization_id: int,
    ):
        return DataSourceRepository.get_by_id(
            db,
            data_source_id,
            organization_id,
        )

    @staticmethod
    def deactivate(
        db: Session,
        data_source_id: int,
        organization_id: int,
    ):

        data_source = DataSourceRepository.get_by_id(
            db,
            data_source_id,
            organization_id,
        )

        if data_source is None:
            return None

        data_source.status = "inactive"

        db.commit()
        db.refresh(data_source)

        return data_source