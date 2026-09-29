from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.code_repository import CodeRepository


class CodeMindRepositoryRepository:
    @staticmethod
    def create(db: Session, **kwargs):
        row = CodeRepository(**kwargs)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def by_id_org(db: Session, repository_id: int, organization_id: int):
        return db.scalar(select(CodeRepository).where(
            CodeRepository.id == repository_id,
            CodeRepository.organization_id == organization_id,
        ))

    @staticmethod
    def by_project(db: Session, project_id: int, organization_id: int):
        return list(db.scalars(select(CodeRepository).where(
            CodeRepository.project_id == project_id,
            CodeRepository.organization_id == organization_id,
            CodeRepository.status == "active",
        ).order_by(CodeRepository.name)).all())

    @staticmethod
    def authorized(db: Session, organization_id: int, project_ids: list[int]):
        if not project_ids:
            return []
        return list(db.scalars(select(CodeRepository).where(
            CodeRepository.organization_id == organization_id,
            CodeRepository.project_id.in_(project_ids),
            CodeRepository.status == "active",
        ).order_by(CodeRepository.name)).all())
