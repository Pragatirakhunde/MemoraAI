from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.data_source import DataSource


class DataSourceRepository:

    @staticmethod
    def create(
        db: Session,
        organization_id: int,
        name: str,
        source_type: str,
        config: dict,
    ) -> DataSource:

        data_source = DataSource(
            organization_id=organization_id,
            name=name,
            source_type=source_type,
            config=config,
            status="inactive",
        )

        db.add(data_source)
        db.commit()
        db.refresh(data_source)

        return data_source

    @staticmethod
    def get_by_id(
        db: Session,
        data_source_id: int,
        organization_id: int,
    ) -> DataSource | None:

        statement = select(DataSource).where(
            DataSource.id == data_source_id,
            DataSource.organization_id == organization_id,
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
        organization_id: int,
    ) -> list[DataSource]:

        statement = (
            select(DataSource)
            .where(
                DataSource.organization_id == organization_id
            )
            .order_by(DataSource.id)
        )

        return list(db.scalars(statement).all())