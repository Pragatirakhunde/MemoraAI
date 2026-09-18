import api from "./axios";

export interface AIReference {
    source_type: string;
    document_id?: number;
    chunk_id?: number;
    title?: string;
    file_path?: string;
    extension?: string;
    chunk_index?: number;
    score: number;
    content?: string;
}

export interface AIEntity {
  name: string;
  type: string;
  confidence?: number;
}

export interface AIChatRequest {
  message: string;
  conversation_id?: number | null;
}

export interface AIChatResponse {
  conversation_id: number;
  query: string;
  answer: string;
  references: AIReference[];
  entities: AIEntity[];
}

export const sendAIMessage = async (
  data: AIChatRequest
): Promise<AIChatResponse> => {
  const response = await api.post<AIChatResponse>(
    "/ai/chat",
    data
  );

  return response.data;
};