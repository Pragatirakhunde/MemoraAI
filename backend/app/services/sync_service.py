import hashlib
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.connectors.factory import get_connector
from app.models.data_source import DataSource

from app.repositories.data_source_file_repository import (
    DataSourceFileRepository,
)

from app.repositories.document_repository import (
    DocumentRepository,
)

from app.repositories.sync_job_repository import (
    SyncJobRepository,
)

from app.services.document_service import (
    DocumentService,
)

from app.services.document_processing_service import (
    DocumentProcessingService,
)


class SyncService:

    @staticmethod
    def calculate_checksum(
        content: str,
    ) -> str:

        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def run_sync(
        db: Session,
        data_source: DataSource,
    ):

        job = SyncJobRepository.create(
            db,
            data_source.id,
        )

        try:

            SyncJobRepository.update(
                db,
                job,
                status="running",
            )

            connector = get_connector(
                data_source.source_type,
                data_source.config,
            )

            # Update Git repository
            if data_source.source_type == "git":
                connector.sync_repository()

            files = connector.list_files()

            files_processed = 0
            seen_paths = set()

            for file in files:

                seen_paths.add(file.path)

                content = connector.read_file(
                    file.path
                )

                checksum = (
                    SyncService.calculate_checksum(
                        content
                    )
                )

                file_path = Path(file.path)

                last_modified_at = (
                    datetime.utcfromtimestamp(
                        file_path.stat().st_mtime
                    )
                )

                existing = (
                    DataSourceFileRepository.get_by_path(
                        db=db,
                        data_source_id=data_source.id,
                        file_path=file.path,
                    )
                )

                should_process = False

                # -----------------------------
                # NEW FILE
                # -----------------------------
                if existing is None:

                    existing = (
                        DataSourceFileRepository.create(
                            db=db,
                            data_source_id=data_source.id,
                            file_path=file.path,
                            file_name=file.name,
                            extension=file.extension,
                            size=file.size,
                            checksum=checksum,
                            last_modified_at=last_modified_at,
                        )
                    )

                    should_process = True

                # -----------------------------
                # MODIFIED FILE
                # -----------------------------
                elif (
                    existing.checksum != checksum
                    or existing.size != file.size
                ):

                    existing = (
                        DataSourceFileRepository.update(
                            db=db,
                            file_record=existing,
                            size=file.size,
                            checksum=checksum,
                            last_modified_at=last_modified_at,
                        )
                    )

                    should_process = True

                # -----------------------------
                # UNCHANGED FILE
                # -----------------------------
                else:

                    DataSourceFileRepository.mark_seen(
                        db,
                        existing,
                    )

                # -----------------------------
                # DOCUMENT PROCESSING
                # -----------------------------
                if should_process:

                    document = (
                        DocumentService.ingest_file(
                            db=db,
                            organization_id=(
                                data_source.organization_id
                            ),
                            data_source_id=data_source.id,
                            source_file=existing,
                            content=content,
                        )
                    )

                    # Automatically process
                    DocumentProcessingService.process_document(
                        db=db,
                        document=document,
                    )

                    files_processed += 1

            # -----------------------------
            # DELETED FILE DETECTION
            # -----------------------------

            existing_files = (
                DataSourceFileRepository.get_all_by_source(
                    db,
                    data_source.id,
                )
            )

            for existing in existing_files:

                if (
                    existing.file_path not in seen_paths
                    and existing.status != "deleted"
                ):

                    DataSourceFileRepository.mark_deleted(
                        db,
                        existing,
                    )

                    document = (
                        DocumentRepository.get_by_source_file(
                            db,
                            existing.id,
                        )
                    )

                    if document is not None:

                        DocumentRepository.mark_deleted(
                            db,
                            document,
                        )

            # -----------------------------
            # SYNC SUCCESS
            # -----------------------------

            job = SyncJobRepository.update(
                db,
                job,
                status="completed",
                files_found=len(files),
                files_processed=files_processed,
            )

            data_source.status = "active"
            data_source.last_synced_at = (
                datetime.utcnow()
            )

            db.commit()
            db.refresh(data_source)

            return job

        except Exception as exc:

            data_source.status = "error"

            db.commit()

            return SyncJobRepository.update(
                db,
                job,
                status="failed",
                error_message=str(exc),
            )