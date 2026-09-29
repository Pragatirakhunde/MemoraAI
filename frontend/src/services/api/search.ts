import api from "../axios";

export interface SearchResult {
    score: number;
    document_id: number;
    chunk_id: number;
    title: string;
    content: string;
    reference: {
        document_id: number;
        chunk_id: number;
        title: string;
        file_path: string;
        extension: string;
        document_type: string | null;
        language: string | null;
        chunk_index: number;
        score: number;
    };
}

export async function semanticSearch(query: string, limit = 10) {
    return (await api.post<SearchResult[]>("/search", { query, limit })).data;
}
