import api from "../axios";

export interface DocumentItem {
    id: number;
    data_source_id: number;
    source_file_id: number;
    title: string;
    file_path: string;
    extension: string;
    checksum: string;
    status: string;
    processing_status: string;
    processed_at: string | null;
    processing_error: string | null;
    created_at: string;
    updated_at: string;
}

export interface DocumentDetails extends DocumentItem {
    content: string;
    metadata_json: Record<string, unknown>;
}

export interface DocumentChunk {
    id: number;
    document_id: number;
    chunk_index: number;
    content: string;
    character_count: number;
    checksum: string;
    created_at: string;
}

export const getDocuments = async () => (await api.get<DocumentItem[]>("/documents")).data;
export const getDocument = async (id: number) => (await api.get<DocumentDetails>(`/documents/${id}`)).data;
export const getDocumentChunks = async (id: number) => (await api.get<DocumentChunk[]>(`/documents/${id}/chunks`)).data;
export const processDocument = async (id: number) => (await api.post<DocumentDetails>(`/documents/${id}/process`)).data;
