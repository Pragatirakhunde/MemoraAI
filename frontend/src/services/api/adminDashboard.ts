import api from "../axios";

export interface AdminDashboardData {
    organization: {
        id: number;
        name: string | null;
        slug: string | null;
    };

    users: {
        total: number;
        active: number;
        admins: number;
        employees: number;
    };

    sources: {
        total: number;
        active: number;
        inactive: number;
        error: number;
        last_synced_at: string | null;
    };

    source_files: {
        total: number;
        active: number;
        deleted: number;
    };

    documents: {
        total: number;
        active: number;
        deleted: number;
        pending: number;
        processing: number;
        completed: number;
        failed: number;
    };

    chunks: {
        total: number;
    };

    sync_jobs: {
        total: number;
        pending: number;
        running: number;
        completed: number;
        failed: number;
        files_found: number;
        files_processed: number;
    };

    conversations: {
        total: number;
        messages: number;
    };

    knowledge_graph: {
        total_nodes: number;
        projects: number;
        technologies: number;
        databases: number;
        documents: number;
        total_relationships: number;
    };
    ai_usage: {
        queries: number;
        responses: number;
    };

    recent_activity: {
        id: number;
        source_name: string;
        status: string;
        files_found: number;
        files_processed: number;
        created_at: string;
        started_at: string | null;
        completed_at: string | null;
    }[];

    system_health: {
        database: string;
        ingestion: string;
    };
}


export const getAdminDashboard =
    async (): Promise<AdminDashboardData> => {

        const response =
            await api.get<AdminDashboardData>(
                "/admin/dashboard"
            );

        return response.data;
    };