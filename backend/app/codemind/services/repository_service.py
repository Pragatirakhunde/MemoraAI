from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.connectors.git.repository import GitRepositoryConnector
from app.models.code_repository import CodeRepository
from app.codemind.repositories import CodeMindRepositoryRepository
from app.repositories.project_repository import ProjectRepository


class CodeRepositoryService:
    @staticmethod
    def create(db: Session, organization_id: int, data) -> CodeRepository:
        project = ProjectRepository.get_by_id_and_org(db, data.project_id, organization_id)
        if project is None:
            raise ValueError("Project not found in your organization.")
        if project.status != "active":
            raise ValueError("Archived projects cannot receive code repositories.")
        existing = db.scalar(
            select(CodeRepository).where(
                CodeRepository.organization_id == organization_id,
                CodeRepository.project_id == data.project_id,
                CodeRepository.name == data.name.strip(),
                CodeRepository.status == "active",
            )
        )
        if existing is not None:
            raise ValueError("An active repository with this name already exists for the project.")

        if data.provider == "local":
            if not data.local_path:
                raise ValueError("local_path is required for local repositories.")
            local_path = str(Path(data.local_path).expanduser().resolve())
        else:
            if not data.remote_url:
                raise ValueError("remote_url is required for GitHub repositories.")
            local_path = None
        return CodeMindRepositoryRepository.create(
            db,
            organization_id=organization_id,
            project_id=data.project_id,
            name=data.name.strip(),
            provider=data.provider,
            remote_url=data.remote_url,
            local_path=local_path,
            default_branch=data.default_branch,
            description=data.description,
            status="active",
            index_status="never",
        )

    @staticmethod
    def sync_provider(repository: CodeRepository) -> None:
        if repository.provider != "github":
            return
        connector = GitRepositoryConnector(
            url=repository.remote_url,
            branch=repository.default_branch,
            local_path=str(Path("datasets/raw_datasets/codemind") / str(repository.id)),
        )
        connector.sync_repository()
        repository.local_path = str(Path(connector.local_path).resolve())

    @staticmethod
    def validate_repository(repository: CodeRepository) -> bool:
        if repository.provider == "local":
            return bool(repository.local_path and Path(repository.local_path).expanduser().is_dir())
        connector = GitRepositoryConnector(
            url=repository.remote_url,
            branch=repository.default_branch,
            local_path=str(Path("datasets/raw_datasets/codemind") / str(repository.id)),
        )
        return connector.validate()
