from datetime import datetime

from pydantic import BaseModel


class OrganizationDashboard(BaseModel):
    id: int
    name: str | None
    slug: str | None


class UsersDashboard(BaseModel):
    total: int
    active: int
    admins: int
    employees: int


class SourcesDashboard(BaseModel):
    total: int
    active: int
    inactive: int
    error: int
    last_synced_at: datetime | None


class SourceFilesDashboard(BaseModel):
    total: int
    active: int
    deleted: int


class DocumentsDashboard(BaseModel):
    total: int
    active: int
    deleted: int
    pending: int
    processing: int
    completed: int
    failed: int


class ChunksDashboard(BaseModel):
    total: int


class SyncJobsDashboard(BaseModel):
    total: int
    pending: int
    running: int
    completed: int
    failed: int
    files_found: int
    files_processed: int


class ConversationsDashboard(BaseModel):
    total: int
    messages: int


class KnowledgeGraphDashboard(BaseModel):
    total_nodes: int
    projects: int
    technologies: int
    databases: int
    documents: int
    total_relationships: int

class AIUsageDashboard(BaseModel):
    queries: int
    responses: int

class RecentSyncActivity(BaseModel):
    id: int
    source_name: str
    status: str
    files_found: int
    files_processed: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class SystemHealthDashboard(BaseModel):
    database: str
    ingestion: str

class AdminDashboardResponse(BaseModel):

    organization: OrganizationDashboard

    users: UsersDashboard

    sources: SourcesDashboard

    source_files: SourceFilesDashboard

    documents: DocumentsDashboard

    chunks: ChunksDashboard

    sync_jobs: SyncJobsDashboard

    conversations: ConversationsDashboard
    knowledge_graph: KnowledgeGraphDashboard
    ai_usage: AIUsageDashboard
    recent_activity: list[RecentSyncActivity]
    system_health: SystemHealthDashboard


