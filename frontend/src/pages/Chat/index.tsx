import {
    useEffect,
    useRef,
    useState,
} from "react";

import type { FormEvent } from "react";

import {
    Bot,
    Send,
    User,
    Loader2,
    Plus,
    MessageSquare,
} from "lucide-react";

import {
    sendAIMessage,
} from "../../services/aiService";

import type {
    AIReference,
} from "../../services/aiService";

import {
    getConversations,
    getConversationMessages,
} from "../../services/api/conversation";

import type {
    Conversation,
} from "../../services/api/conversation";


interface ChatMessage {
    role: "user" | "assistant";
    content: string;
    references?: AIReference[];
}


export default function Chat() {

    // -------------------------------------------------
    // Conversations
    // -------------------------------------------------

    const [conversations, setConversations] =
        useState<Conversation[]>([]);

    const [conversationId, setConversationId] =
        useState<number | null>(() => {

            const stored =
                localStorage.getItem(
                    "conversation_id"
                );

            return stored
                ? Number(stored)
                : null;
        });


    // -------------------------------------------------
    // Messages
    // -------------------------------------------------

    const [messages, setMessages] =
        useState<ChatMessage[]>([]);

    const [input, setInput] =
        useState("");


    // -------------------------------------------------
    // Loading states
    // -------------------------------------------------

    const [loading, setLoading] =
        useState(false);

    const [loadingHistory, setLoadingHistory] =
        useState(false);

    const [loadingConversations, setLoadingConversations] =
        useState(false);


    // -------------------------------------------------
    // Error
    // -------------------------------------------------

    const [error, setError] =
        useState("");

    const messagesEndRef = useRef<HTMLDivElement | null>(null);
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
        });
    }, [messages, loading]);


    // -------------------------------------------------
    // Load conversation list
    // -------------------------------------------------

    const loadConversations = async () => {

        setLoadingConversations(true);

        try {

            const data =
                await getConversations();

            setConversations(data);

            // Check whether the stored conversation
            // still exists.
            if (conversationId) {

                const exists = data.some(
                    (conversation) =>
                        conversation.id === conversationId
                );

                if (!exists) {

                    localStorage.removeItem(
                        "conversation_id"
                    );

                    setConversationId(null);
                    setMessages([]);
                }
            }

        } catch (err) {

            console.error(
                "Failed to load conversations:",
                err
            );

        } finally {

            setLoadingConversations(false);
        }
    };


    useEffect(() => {
        loadConversations();
    }, []);


    // -------------------------------------------------
    // Load selected conversation
    // -------------------------------------------------

    const loadConversation = async (
        id: number
    ) => {

        setLoadingHistory(true);
        setError("");

        try {

            const history =
                await getConversationMessages(id);

            setMessages(
                history.map((message) => ({
                    role: message.role,
                    content: message.content,
                }))
            );

            setConversationId(id);

            localStorage.setItem(
                "conversation_id",
                String(id)
            );

        } catch (err: any) {

            console.error(
                "Failed to load conversation:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to load conversation."
            );

        } finally {

            setLoadingHistory(false);
        }
    };


    // -------------------------------------------------
    // New conversation
    // -------------------------------------------------

    const handleNewConversation = () => {

        localStorage.removeItem(
            "conversation_id"
        );

        setConversationId(null);
        setMessages([]);
        setInput("");
        setError("");
    };


    // -------------------------------------------------
    // Send message
    // -------------------------------------------------

    const handleSubmit = async (
        event: FormEvent
    ) => {

        event.preventDefault();

        const message =
            input.trim();

        if (!message || loading) {
            return;
        }

        setError("");

        // Show user message immediately
        setMessages(
            (current) => [
                ...current,
                {
                    role: "user",
                    content: message,
                },
            ]
        );

        setInput("");
        setLoading(true);

        try {

            const response =
                await sendAIMessage({
                    message,
                    conversation_id:
                        conversationId,
                });

            // Save conversation ID
            setConversationId(
                response.conversation_id
            );

            localStorage.setItem(
                "conversation_id",
                String(
                    response.conversation_id
                )
            );

            // Add AI response
            setMessages(
                (current) => [
                    ...current,
                    {
                        role: "assistant",
                        content:
                            response.answer,
                        references:
                            response.references,
                    },
                ]
            );

            // Refresh conversation list
            await loadConversations();

        } catch (err: any) {

            console.error(
                "AI request failed:",
                err
            );

            const status =
                err?.response?.status;

            let errorMessage =
                "Something went wrong while contacting the AI assistant.";

            if (status === 401) {

                errorMessage =
                    "Your session has expired. Please log in again.";

            } else if (status === 403) {

                errorMessage =
                    "You do not have permission to access this conversation.";

            } else if (status === 429) {

                errorMessage =
                    "AI request limit reached. Please wait and try again later.";

            } else if (status === 503) {

                errorMessage =
                    "The AI service is temporarily busy. Please try again.";

            } else if (!err?.response) {

                errorMessage =
                    "Unable to reach the backend server.";

            } else if (
                err?.response?.data?.detail
            ) {

                errorMessage =
                    err.response.data.detail;
            }

            setError(errorMessage);

        }
        finally {

            setLoading(false);
        }
    };


    // -------------------------------------------------
    // Render
    // -------------------------------------------------

    return (
        <div className="flex h-full min-h-[calc(100vh-80px)] bg-slate-50">

            {/* =================================================
                Conversation Sidebar
            ================================================== */}

            <aside className="hidden w-72 shrink-0 border-r bg-white lg:flex lg:flex-col">

                <div className="flex items-center justify-between border-b p-4">

                    <h2 className="text-sm font-semibold text-slate-800">
                        Conversations
                    </h2>

                    <button
                        onClick={
                            handleNewConversation
                        }
                        className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800"
                        title="New conversation"
                    >
                        <Plus size={18} />
                    </button>

                </div>


                <div className="flex-1 overflow-y-auto p-2">

                    {loadingConversations ? (

                        <div className="flex items-center justify-center py-6">

                            <Loader2
                                size={18}
                                className="animate-spin text-slate-400"
                            />

                        </div>

                    ) : conversations.length === 0 ? (

                        <div className="px-3 py-6 text-center text-sm text-slate-400">
                            No conversations yet.
                        </div>

                    ) : (

                        <div className="space-y-1">

                            {conversations.map(
                                (conversation) => (

                                    <button
                                        key={
                                            conversation.id
                                        }
                                        onClick={() =>
                                            loadConversation(
                                                conversation.id
                                            )
                                        }
                                        className={`flex w-full items-start gap-3 rounded-lg px-3 py-3 text-left transition ${
                                            conversation.id ===
                                            conversationId
                                                ? "bg-slate-100 text-slate-900"
                                                : "text-slate-600 hover:bg-slate-50"
                                        }`}
                                    >

                                        <MessageSquare
                                            size={17}
                                            className="mt-0.5 shrink-0"
                                        />

                                        <div className="min-w-0">

                                            <p className="truncate text-sm font-medium">
                                                {conversation.title ||
                                                    "New conversation"}
                                            </p>

                                            <p className="mt-1 text-xs text-slate-400">
                                                {new Date(
                                                    conversation.created_at
                                                ).toLocaleDateString()}
                                            </p>

                                        </div>

                                    </button>

                                )
                            )}

                        </div>

                    )}

                </div>

            </aside>


            {/* =================================================
                Main Chat
            ================================================== */}

            <div className="flex min-w-0 flex-1 flex-col">

                {/* -------------------------------------------------
                    Header
                -------------------------------------------------- */}

                <div className="border-b bg-white px-6 py-4">

                    <div className="flex items-center gap-3">

                        <div className="rounded-lg bg-slate-900 p-2">

                            <Bot
                                size={20}
                                className="text-white"
                            />

                        </div>

                        <div>

                            <h1 className="text-xl font-semibold text-slate-900">
                                AI Assistant
                            </h1>

                            <p className="text-sm text-slate-500">
                                Ask questions about TechNova organizational knowledge
                            </p>

                        </div>

                    </div>

                </div>


                {/* -------------------------------------------------
                    Chat Area
                -------------------------------------------------- */}

                <div className="flex-1 overflow-y-auto px-6 py-6">

                    <div className="mx-auto max-w-4xl space-y-5">

                        {/* Loading history */}

                        {loadingHistory && (

                            <div className="flex items-center justify-center py-10">

                                <div className="flex items-center gap-2 text-sm text-slate-500">

                                    <Loader2
                                        size={18}
                                        className="animate-spin"
                                    />

                                    Loading conversation...

                                </div>

                            </div>

                        )}


                        {/* Empty state */}

                        {!loadingHistory &&
                            messages.length === 0 && (

                                <div className="flex min-h-[400px] items-center justify-center">

                                    <div className="max-w-lg text-center">

                                        <div className="mx-auto mb-4 w-fit rounded-full bg-slate-200 p-4">

                                            <Bot
                                                size={30}
                                                className="text-slate-700"
                                            />

                                        </div>

                                        <h2 className="text-2xl font-semibold text-slate-900">
                                            Ask your organization anything
                                        </h2>

                                        <p className="mt-2 text-sm leading-6 text-slate-500">
                                            Search across organizational
                                            documents, technologies,
                                            projects, databases and
                                            knowledge graph relationships.
                                        </p>

                                    </div>

                                </div>

                            )}


                        {/* =================================================
                            Messages
                        ================================================== */}

                        {messages.map(
                            (message, index) => (

                                <div
                                    key={index}
                                    className={`flex gap-3 ${
                                        message.role === "user"
                                            ? "justify-end"
                                            : "justify-start"
                                    }`}
                                >

                                    {/* Assistant Icon */}

                                    {message.role ===
                                        "assistant" && (

                                        <div className="mt-1 h-8 w-8 shrink-0 rounded-full bg-slate-900 p-1.5">

                                            <Bot
                                                size={20}
                                                className="text-white"
                                            />

                                        </div>

                                    )}


                                    {/* Message Bubble */}

                                    <div
                                        className={`max-w-3xl rounded-2xl px-4 py-3 ${
                                            message.role === "user"
                                                ? "bg-slate-900 text-white"
                                                : "border bg-white text-slate-800 shadow-sm"
                                        }`}
                                    >

                                        <div className="whitespace-pre-wrap text-sm leading-6">
                                            {message.content}
                                        </div>


                                        {/* =================================================
                                            Sources & Evidence
                                        ================================================== */}

                                        {message.references &&
                                            message.references.length >
                                                0 && (

                                                <div className="mt-5 border-t border-slate-200 pt-4">

                                                    <div className="mb-3 flex items-center justify-between">

                                                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                                                            Sources & Evidence
                                                        </p>

                                                        <span className="text-xs text-slate-400">
                                                            {
                                                                message.references.length
                                                            }{" "}
                                                            source
                                                            {message.references.length !==
                                                            1
                                                                ? "s"
                                                                : ""}
                                                        </span>

                                                    </div>


                                                    <div className="space-y-3">

                                                        {message.references.map(
                                                            (
                                                                reference,
                                                                referenceIndex
                                                            ) => {

                                                                const score =
                                                                    Math.round(
                                                                        reference.score *
                                                                            100
                                                                    );


                                                                {/* =========================
                                                                    Vector Source
                                                                ========================== */}

                                                                if (
                                                                    reference.source_type ===
                                                                    "vector"
                                                                ) {

                                                                    return (

                                                                        <div
                                                                            key={
                                                                                referenceIndex
                                                                            }
                                                                            className="rounded-xl border border-slate-200 bg-slate-50 p-3"
                                                                        >

                                                                            <div className="flex items-start justify-between gap-3">

                                                                                <div className="flex min-w-0 gap-2">

                                                                                    <div className="mt-0.5 rounded-md bg-white p-1.5 shadow-sm">

                                                                                        <span className="text-sm">
                                                                                            📄
                                                                                        </span>

                                                                                    </div>


                                                                                    <div className="min-w-0">

                                                                                        <p className="truncate text-sm font-medium text-slate-800">
                                                                                            {reference.title ||
                                                                                                "Document source"}
                                                                                        </p>

                                                                                        <p className="mt-1 break-all text-xs text-slate-500">
                                                                                            {reference.file_path ||
                                                                                                "Unknown file"}
                                                                                        </p>

                                                                                    </div>

                                                                                </div>


                                                                                <span className="shrink-0 rounded-full bg-white px-2 py-1 text-xs text-slate-500">

                                                                                    {score}%

                                                                                </span>

                                                                            </div>


                                                                            <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-400">

                                                                                {reference.chunk_index !==
                                                                                    undefined && (

                                                                                    <span>
                                                                                        Chunk{" "}
                                                                                        {
                                                                                            reference.chunk_index
                                                                                        }
                                                                                    </span>

                                                                                )}


                                                                                {reference.extension && (

                                                                                    <span>
                                                                                        {
                                                                                            reference.extension
                                                                                        }
                                                                                    </span>

                                                                                )}

                                                                            </div>

                                                                        </div>

                                                                    );
                                                                }


                                                                {/* =========================
                                                                    Graph Source
                                                                ========================== */}

                                                                return (

                                                                    <div
                                                                        key={
                                                                            referenceIndex
                                                                        }
                                                                        className="rounded-xl border border-slate-200 bg-slate-50 p-3"
                                                                    >

                                                                        <div className="flex items-start justify-between gap-3">

                                                                            <div className="flex gap-2">

                                                                                <div className="mt-0.5 rounded-md bg-white p-1.5 shadow-sm">

                                                                                    <span className="text-sm">
                                                                                        🔷
                                                                                    </span>

                                                                                </div>


                                                                                <div>

                                                                                    <p className="text-sm font-medium text-slate-800">
                                                                                        Knowledge Graph
                                                                                    </p>

                                                                                    <p className="mt-1 text-xs text-slate-500">
                                                                                        Entity relationship evidence
                                                                                    </p>

                                                                                </div>

                                                                            </div>


                                                                            <span className="shrink-0 rounded-full bg-white px-2 py-1 text-xs text-slate-500">

                                                                                {score}%

                                                                            </span>

                                                                        </div>


                                                                        <p className="mt-3 rounded-lg bg-white p-2 text-xs leading-5 text-slate-600">
                                                                            {reference.content ||
                                                                                "Graph evidence unavailable."}
                                                                        </p>

                                                                    </div>

                                                                );
                                                            }
                                                        )}

                                                    </div>

                                                </div>

                                            )}

                                    </div>


                                    {/* User Icon */}

                                    {message.role ===
                                        "user" && (

                                        <div className="mt-1 h-8 w-8 shrink-0 rounded-full bg-slate-200 p-1.5">

                                            <User
                                                size={20}
                                                className="text-slate-700"
                                            />

                                        </div>

                                    )}

                                </div>

                            )
                        )}


                        {/* =================================================
                            AI Loading
                        ================================================== */}

                        {loading && (

                            <div className="flex items-center gap-3">

                                <div className="h-8 w-8 rounded-full bg-slate-900 p-1.5">

                                    <Bot
                                        size={20}
                                        className="text-white"
                                    />

                                </div>


                                <div className="rounded-2xl border bg-white px-4 py-3 shadow-sm">

                                    <div className="flex items-center gap-2 text-sm text-slate-500">

                                        <Loader2
                                            size={16}
                                            className="animate-spin"
                                        />

                                        Searching organizational knowledge...

                                    </div>

                                </div>

                            </div>

                        )}


                        {/* =================================================
                            Error
                        ================================================== */}

                        {error && (

                            <div className="flex items-center justify-between gap-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">

                                <span>
                                    {error}
                                </span>

                                <button
                                    type="button"
                                    onClick={() => setError("")}
                                    className="shrink-0 font-medium text-red-700 hover:text-red-900"
                                >
                                    Dismiss
                                </button>

                            </div>

                        )}
                        <div ref={messagesEndRef} />

                    </div>

                </div>


                {/* =================================================
                    Input
                ================================================== */}

                <div className="border-t bg-white px-6 py-4">

                    <form
                        onSubmit={handleSubmit}
                        className="mx-auto flex max-w-4xl items-center gap-3"
                    >

                        <input
                            type="text"
                            value={input}
                            onChange={(event) =>
                                setInput(
                                    event.target.value
                                )
                            }
                            placeholder="Ask about projects, technologies, documents..."
                            disabled={loading}
                            className="flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200 disabled:bg-slate-100"
                        />


                        <button
                            type="submit"
                            disabled={
                                !input.trim() ||
                                loading
                            }
                            className="flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                        >

                            {loading ? (
                                <Loader2
                                    size={18}
                                    className="animate-spin"
                                />
                            ) : (
                                <Send
                                    size={18}
                                />
                            )}

                            Send

                        </button>

                    </form>

                </div>

            </div>

        </div>
    );
}