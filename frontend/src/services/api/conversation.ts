import api from "../axios";


export interface Conversation {
    id: number;
    title?: string | null;
    created_at: string;
}


export interface ConversationMessage {
    id: number;
    conversation_id: number;
    role: "user" | "assistant";
    content: string;
    created_at: string;
}


export const getConversations = async (): Promise<Conversation[]> => {

    const response =
        await api.get<Conversation[]>(
            "/ai/conversations"
        );

    return response.data;
};


export const getConversationMessages = async (
    conversationId: number
): Promise<ConversationMessage[]> => {

    const response =
        await api.get<ConversationMessage[]>(
            `/ai/conversations/${conversationId}/messages`
        );

    return response.data;
};