import api from "../axios";

export interface SyncJob {
    id: number;
    data_source_id: number;
    status: "pending" | "running" | "completed" | "failed";
    started_at: string | null;
    completed_at: string | null;
    files_found: number;
    files_processed: number;
    error_message: string | null;
    created_at: string;
}

export async function queueBackgroundSync(
    dataSourceId: number
): Promise<SyncJob> {
    const response = await api.post(
        `/sync/data-sources/${dataSourceId}/background`
    );

    return response.data;
}

export async function getSyncJobs(): Promise<SyncJob[]> {
    const response = await api.get("/sync/jobs");

    return response.data;
}

export async function getSyncJob(
    jobId: number
): Promise<SyncJob> {
    const response = await api.get(
        `/sync/jobs/${jobId}`
    );

    return response.data;
}

export interface QueueAllSyncResponse {
    status: string;
    message: string;
    task_id: string;
}

export async function queueAllBackgroundSyncs(): Promise<QueueAllSyncResponse> {
    const response = await api.post("/sync/background");

    return response.data;
}