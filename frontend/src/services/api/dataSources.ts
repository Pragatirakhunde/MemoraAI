import api from "../axios";

export interface DataSource {
    id: number;
    organization_id: number;
    project_id: number | null;
    name: string;
    source_type: "local_directory" | "git";
    config: Record<string, unknown>;
    status: "active" | "inactive" | "error";
    last_synced_at: string | null;
    created_at: string;
    updated_at: string;
}

export interface CreateDataSourceRequest {
    name: string;
    source_type: "local_directory" | "git";
    config: Record<string, unknown>;
    project_id: number | null;
}

export interface ValidateDataSourceResponse {
    data_source_id: number;
    status: string;
    valid: boolean;
    message?: string;
    [key: string]: unknown;
}

export async function getDataSources(): Promise<DataSource[]> {
    const response = await api.get("/data-sources");

    return response.data;
}

export async function getDataSource(
    dataSourceId: number
): Promise<DataSource> {
    const response = await api.get(
        `/data-sources/${dataSourceId}`
    );

    return response.data;
}

export async function createDataSource(
    data: CreateDataSourceRequest
): Promise<DataSource> {
    const response = await api.post(
        "/data-sources",
        data
    );

    return response.data;
}

export async function deactivateDataSource(
    dataSourceId: number
): Promise<DataSource> {
    const response = await api.patch(
        `/data-sources/${dataSourceId}/deactivate`
    );

    return response.data;
}

export async function validateDataSource(
    dataSourceId: number
): Promise<ValidateDataSourceResponse> {
    const response = await api.post(
        `/data-sources/${dataSourceId}/validate`
    );

    return response.data;
}