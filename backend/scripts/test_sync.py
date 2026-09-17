from app.database.postgres import SessionLocal
from app.repositories.data_source_repository import (
    DataSourceRepository,
)
from app.services.sync_service import SyncService


db = SessionLocal()

try:
    source = DataSourceRepository.get_by_id(
        db,
        data_source_id=1,
        organization_id=1,
    )

    if source is None:
        print("Data source not found")
    else:
        job = SyncService.run_sync(
            db,
            source,
        )

        print("Sync Job ID:", job.id)
        print("Status:", job.status)
        print("Files Found:", job.files_found)
        print("Files Processed:", job.files_processed)

finally:
    db.close()