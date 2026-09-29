import api from "../axios";

export interface CodeRepository {
    id: number;
    organization_id: number;
    project_id: number;
    name: string;
    provider: "local" | "github";
    remote_url: string | null;
    local_path: string | null;
    default_branch: string;
    status: string;
    index_status: string;
    last_indexed_at: string | null;
    last_index_error: string | null;
}

export interface CodeReference {
    file_path: string;
    symbol_name: string;
    start_line: number;
    end_line: number;
    score?: number;
}

export const listCodeRepositories = async () =>
    (await api.get<CodeRepository[]>("/codemind/repositories")).data;

export const createCodeRepository = async (payload: Partial<CodeRepository> & { project_id: number; name: string; provider: "local" | "github" }) =>
    (await api.post<CodeRepository>("/codemind/repositories", payload)).data;

export const validateCodeRepository = async (id: number) =>
    (await api.post(`/codemind/repositories/${id}/validate`)).data;

export const indexCodeRepository = async (id: number) =>
    (await api.post(`/codemind/repositories/${id}/index`)).data;

export const getProjectCodeRepositories = async (projectId: number) =>
    (await api.get<CodeRepository[]>(`/codemind/projects/${projectId}/repositories`)).data;

export const getCodeFiles = async (projectId: number) =>
    (await api.get(`/codemind/projects/${projectId}/files`)).data;

export const getCodeSymbols = async (projectId: number) =>
    (await api.get(`/codemind/projects/${projectId}/symbols`)).data;

export const codeSearch = async (projectId: number, query: string, limit = 10) =>
    (await api.post(`/codemind/projects/${projectId}/search`, { query, limit })).data;

export const askCodeMind = async (projectId: number, query: string, limit = 8) =>
    (await api.post(`/codemind/projects/${projectId}/ask`, { query, limit })).data;

export const getArchitecture = async (projectId: number) =>
    (await api.get(`/codemind/projects/${projectId}/architecture`)).data;

export const getHistory = async (projectId: number) =>
    (await api.get(`/codemind/projects/${projectId}/history`)).data;

export const getDependencies = async (projectId: number, symbolId: number) =>
    (await api.get(`/codemind/projects/${projectId}/dependencies/${symbolId}`)).data;

export const getImpact = async (projectId: number, symbolId: number) =>
    (await api.get(`/codemind/projects/${projectId}/impact/${symbolId}`)).data;

export const businessRule = async (projectId: number, rule: string, limit = 8) =>
    (await api.post(`/codemind/projects/${projectId}/business-rule`, { rule, limit })).data;
