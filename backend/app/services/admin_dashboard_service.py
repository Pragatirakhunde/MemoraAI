from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.data_source import DataSource
from app.models.data_source_file import DataSourceFile
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.organization import Organization
from app.models.sync_job import SyncJob
from app.models.user import User
from app.services.graph_query_service import GraphQueryService


class AdminDashboardService:

    @staticmethod
    def get_dashboard(
        db: Session,
        organization_id: int,
    ) -> dict:

        # =================================================
        # Organization
        # =================================================

        organization = db.execute(
            select(Organization).where(
                Organization.id == organization_id
            )
        ).scalar_one_or_none()


        # =================================================
        # Users
        # =================================================

        total_users = db.scalar(
            select(func.count(User.id)).where(
                User.organization_id == organization_id
            )
        ) or 0


        active_users = db.scalar(
            select(func.count(User.id)).where(
                User.organization_id == organization_id,
                User.is_active.is_(True),
            )
        ) or 0


        admin_users = db.scalar(
            select(func.count(User.id)).where(
                User.organization_id == organization_id,
                User.role == "admin",
            )
        ) or 0


        employee_users = db.scalar(
            select(func.count(User.id)).where(
                User.organization_id == organization_id,
                User.role == "employee",
            )
        ) or 0


        # =================================================
        # Data Sources
        # =================================================

        total_sources = db.scalar(
            select(func.count(DataSource.id)).where(
                DataSource.organization_id ==
                organization_id
            )
        ) or 0


        active_sources = db.scalar(
            select(func.count(DataSource.id)).where(
                DataSource.organization_id ==
                organization_id,
                DataSource.status == "active",
            )
        ) or 0


        inactive_sources = db.scalar(
            select(func.count(DataSource.id)).where(
                DataSource.organization_id ==
                organization_id,
                DataSource.status == "inactive",
            )
        ) or 0


        error_sources = db.scalar(
            select(func.count(DataSource.id)).where(
                DataSource.organization_id ==
                organization_id,
                DataSource.status == "error",
            )
        ) or 0


        # =================================================
        # Data Source Files
        # =================================================

        total_source_files = db.scalar(
            select(func.count(DataSourceFile.id))
            .select_from(DataSourceFile)
            .join(
                DataSource,
                DataSource.id ==
                DataSourceFile.data_source_id,
            )
            .where(
                DataSource.organization_id ==
                organization_id
            )
        ) or 0


        active_source_files = db.scalar(
            select(func.count(DataSourceFile.id))
            .select_from(DataSourceFile)
            .join(
                DataSource,
                DataSource.id ==
                DataSourceFile.data_source_id,
            )
            .where(
                DataSource.organization_id ==
                organization_id,
                DataSourceFile.status == "active",
            )
        ) or 0


        deleted_source_files = db.scalar(
            select(func.count(DataSourceFile.id))
            .select_from(DataSourceFile)
            .join(
                DataSource,
                DataSource.id ==
                DataSourceFile.data_source_id,
            )
            .where(
                DataSource.organization_id ==
                organization_id,
                DataSourceFile.status == "deleted",
            )
        ) or 0


        # =================================================
        # Documents
        # =================================================

        total_documents = db.scalar(
            select(func.count(Document.id)).where(
                Document.organization_id ==
                organization_id
            )
        ) or 0


        active_documents = db.scalar(
            select(func.count(Document.id)).where(
                Document.organization_id ==
                organization_id,
                Document.status == "active",
            )
        ) or 0


        deleted_documents = db.scalar(
            select(func.count(Document.id)).where(
                Document.organization_id ==
                organization_id,
                Document.status == "deleted",
            )
        ) or 0


        # -------------------------------------------------
        # Document processing status
        # -------------------------------------------------

        pending_documents = db.scalar(
            select(func.count(Document.id)).where(
                Document.organization_id ==
                organization_id,
                Document.processing_status ==
                "pending",
            )
        ) or 0


        processing_documents = db.scalar(
            select(func.count(Document.id)).where(
                Document.organization_id ==
                organization_id,
                Document.processing_status ==
                "processing",
            )
        ) or 0


        completed_documents = db.scalar(
            select(func.count(Document.id)).where(
                Document.organization_id ==
                organization_id,
                Document.processing_status ==
                "completed",
            )
        ) or 0


        failed_documents = db.scalar(
            select(func.count(Document.id)).where(
                Document.organization_id ==
                organization_id,
                Document.processing_status ==
                "failed",
            )
        ) or 0


        # =================================================
        # Document Chunks
        # =================================================

        total_chunks = db.scalar(
            select(func.count(DocumentChunk.id))
            .select_from(DocumentChunk)
            .join(
                Document,
                Document.id ==
                DocumentChunk.document_id,
            )
            .where(
                Document.organization_id ==
                organization_id
            )
        ) or 0


        # =================================================
        # Sync Jobs
        # =================================================

        total_sync_jobs = db.scalar(
            select(func.count(SyncJob.id))
            .select_from(SyncJob)
            .join(
                DataSource,
                DataSource.id ==
                SyncJob.data_source_id,
            )
            .where(
                DataSource.organization_id ==
                organization_id
            )
        ) or 0


        pending_sync_jobs = db.scalar(
            select(func.count(SyncJob.id))
            .select_from(SyncJob)
            .join(
                DataSource,
                DataSource.id ==
                SyncJob.data_source_id,
            )
            .where(
                DataSource.organization_id ==
                organization_id,
                SyncJob.status == "pending",
            )
        ) or 0


        running_sync_jobs = db.scalar(
            select(func.count(SyncJob.id))
            .select_from(SyncJob)
            .join(
                DataSource,
                DataSource.id ==
                SyncJob.data_source_id,
            )
            .where(
                DataSource.organization_id ==
                organization_id,
                SyncJob.status == "running",
            )
        ) or 0


        completed_sync_jobs = db.scalar(
            select(func.count(SyncJob.id))
            .select_from(SyncJob)
            .join(
                DataSource,
                DataSource.id ==
                SyncJob.data_source_id,
            )
            .where(
                DataSource.organization_id ==
                organization_id,
                SyncJob.status == "completed",
            )
        ) or 0


        failed_sync_jobs = db.scalar(
            select(func.count(SyncJob.id))
            .select_from(SyncJob)
            .join(
                DataSource,
                DataSource.id ==
                SyncJob.data_source_id,
            )
            .where(
                DataSource.organization_id ==
                organization_id,
                SyncJob.status == "failed",
            )
        ) or 0


        # =================================================
        # Sync File Totals
        # =================================================

        sync_file_totals = db.execute(
            select(
                func.coalesce(
                    func.sum(SyncJob.files_found),
                    0,
                ),
                func.coalesce(
                    func.sum(SyncJob.files_processed),
                    0,
                ),
            )
            .select_from(SyncJob)
            .join(
                DataSource,
                DataSource.id ==
                SyncJob.data_source_id,
            )
            .where(
                DataSource.organization_id ==
                organization_id
            )
        ).one()


        total_files_found = (
            sync_file_totals[0] or 0
        )

        total_files_processed = (
            sync_file_totals[1] or 0
        )


        # =================================================
        # Conversations
        # =================================================

        total_conversations = db.scalar(
            select(
                func.count(
                    Conversation.id
                )
            ).where(
                Conversation.organization_id ==
                organization_id
            )
        ) or 0


        # =================================================
        # Messages
        # =================================================

        total_messages = db.scalar(
            select(
                func.count(
                    Message.id
                )
            )
            .select_from(Message)
            .join(
                Conversation,
                Conversation.id ==
                Message.conversation_id,
            )
            .where(
                Conversation.organization_id ==
                organization_id
            )
        ) or 0


        # =================================================
        # AI Usage
        # =================================================

        total_user_queries = db.scalar(
            select(
                func.count(Message.id)
            )
            .select_from(Message)
            .join(
                Conversation,
                Conversation.id ==
                Message.conversation_id,
            )
            .where(
                Conversation.organization_id ==
                organization_id,
                Message.role == "user",
            )
        ) or 0


        total_ai_responses = db.scalar(
            select(
                func.count(Message.id)
            )
            .select_from(Message)
            .join(
                Conversation,
                Conversation.id ==
                Message.conversation_id,
            )
            .where(
                Conversation.organization_id ==
                organization_id,
                Message.role == "assistant",
            )
        ) or 0


        # =================================================
        # Latest Data Source Sync
        # =================================================

        latest_sync = db.scalar(
            select(
                func.max(
                    DataSource.last_synced_at
                )
            ).where(
                DataSource.organization_id ==
                organization_id
            )
        )

        # =================================================
        # Knowledge Graph
        # =================================================

        graph_stats = (
            GraphQueryService.get_graph_stats(
                organization_id
            )
        )

                # =================================================
        # Recent Sync Activity
        # =================================================

        recent_sync_jobs = db.execute(
            select(
                SyncJob.id,
                DataSource.name.label("source_name"),
                SyncJob.status,
                SyncJob.files_found,
                SyncJob.files_processed,
                SyncJob.created_at,
                SyncJob.started_at,
                SyncJob.completed_at,
            )
            .select_from(SyncJob)
            .join(
                DataSource,
                DataSource.id ==
                SyncJob.data_source_id,
            )
            .where(
                DataSource.organization_id ==
                organization_id
            )
            .order_by(
                SyncJob.created_at.desc()
            )
            .limit(5)
        ).all()


        recent_activity = []

        for job in recent_sync_jobs:

            recent_activity.append(
                {
                    "id": job.id,
                    "source_name": job.source_name,
                    "status": job.status,
                    "files_found":
                        job.files_found or 0,
                    "files_processed":
                        job.files_processed or 0,
                    "created_at":
                        job.created_at,
                    "started_at":
                        job.started_at,
                    "completed_at":
                        job.completed_at,
                }
            )


        # =================================================
        # System Health
        # =================================================

        try:

            db.execute(text("SELECT 1"))

            database_status = "healthy"

        except Exception:

            database_status = "error"


        if running_sync_jobs > 0:

            ingestion_status = "syncing"

        elif failed_sync_jobs > 0:

            ingestion_status = "attention"

        else:

            ingestion_status = "idle"


        # =================================================
        # Response
        # =================================================

        return {

            "organization": {

                "id": organization_id,

                "name":
                    organization.name
                    if organization
                    else None,

                "slug":
                    organization.slug
                    if organization
                    else None,
            },


            "users": {

                "total":
                    total_users,

                "active":
                    active_users,

                "admins":
                    admin_users,

                "employees":
                    employee_users,
            },


            "sources": {

                "total":
                    total_sources,

                "active":
                    active_sources,

                "inactive":
                    inactive_sources,

                "error":
                    error_sources,

                "last_synced_at":
                    latest_sync,
            },

            "knowledge_graph": graph_stats,


            "source_files": {

                "total":
                    total_source_files,

                "active":
                    active_source_files,

                "deleted":
                    deleted_source_files,
            },


            "documents": {

                "total":
                    total_documents,

                "active":
                    active_documents,

                "deleted":
                    deleted_documents,

                "pending":
                    pending_documents,

                "processing":
                    processing_documents,

                "completed":
                    completed_documents,

                "failed":
                    failed_documents,
            },


            "chunks": {

                "total":
                    total_chunks,
            },


            "sync_jobs": {

                "total":
                    total_sync_jobs,

                "pending":
                    pending_sync_jobs,

                "running":
                    running_sync_jobs,

                "completed":
                    completed_sync_jobs,

                "failed":
                    failed_sync_jobs,

                "files_found":
                    total_files_found,

                "files_processed":
                    total_files_processed,
            },


            "conversations": {

                "total":
                    total_conversations,

                "messages":
                    total_messages,
            },

            "ai_usage": {

                "queries":
                    total_user_queries,

                "responses":
                    total_ai_responses,
            },

            "recent_activity":
                recent_activity,

            "system_health": {

                "database":
                    database_status,

                "ingestion":
                    ingestion_status,
            },
        }