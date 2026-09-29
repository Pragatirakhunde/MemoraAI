from __future__ import annotations

import argparse

from app.codemind.schemas.models import CodeRepositoryCreate
from app.codemind.repositories import CodeMindRepositoryRepository
from app.codemind.services.indexing_service import CodeMindIndexingService
from app.codemind.services.repository_service import CodeRepositoryService
from app.database.postgres import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/reuse and index a local CodeMind repository.")
    parser.add_argument("--project-id", type=int, required=True)
    parser.add_argument("--organization-id", type=int, default=1)
    parser.add_argument("--name", required=True)
    parser.add_argument("--path", required=True)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        existing = [
            repo for repo in CodeMindRepositoryRepository.by_project(
                db, args.project_id, args.organization_id
            )
            if repo.name == args.name and repo.provider == "local"
        ]
        repository = existing[0] if existing else CodeRepositoryService.create(
            db,
            args.organization_id,
            CodeRepositoryCreate(
                project_id=args.project_id,
                name=args.name,
                provider="local",
                local_path=args.path,
            ),
        )

        if not CodeRepositoryService.validate_repository(repository):
            raise SystemExit(f"Repository path is invalid: {repository.local_path}")

        result = CodeMindIndexingService(db).index_repository(repository)
        print("CodeMind indexing completed")
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
