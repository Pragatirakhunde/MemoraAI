import {
    useEffect,
    useState,
} from "react";

import type {
    ReactNode,
} from "react";

import {
    Bot,
    Search,
    Network,
    FileText,
    MessageSquare,
    ArrowRight,
    Loader2,
} from "lucide-react";

import {
    useAuth,
} from "../../context/AuthContext";

import {
    getConversations,
} from "../../services/api/conversation";

import type {
    Conversation,
} from "../../services/api/conversation";


function EmployeeDashboard() {

    const { user } = useAuth();

    const [conversations, setConversations] =
        useState<Conversation[]>([]);

    const [loading, setLoading] =
        useState(true);


    useEffect(() => {

        const loadConversations = async () => {

            try {

                const data =
                    await getConversations();

                setConversations(
                    data.slice(0, 5)
                );

            } catch (error) {

                console.error(
                    "Failed to load conversations:",
                    error
                );

            } finally {

                setLoading(false);

            }
        };

        loadConversations();

    }, []);


    const openPage = (
        path: string
    ) => {
        window.location.href = path;
    };


    return (

        <div className="space-y-6">

            {/* =========================================
                Welcome
            ========================================== */}

            <div className="rounded-2xl bg-white p-6 shadow-sm">

                <p className="text-sm font-medium text-slate-500">
                    Employee Workspace
                </p>

                <h1 className="mt-2 text-3xl font-bold text-slate-900">

                    Welcome,{" "}
                    {user?.name || "Employee"}

                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">

                    Explore organizational knowledge,
                    search documents, ask the AI assistant,
                    and explore relationships in the
                    Knowledge Graph.

                </p>

            </div>


            {/* =========================================
                Quick Actions
            ========================================== */}

            <div>

                <h2 className="mb-4 text-lg font-semibold text-slate-900">
                    Quick Actions
                </h2>


                <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-4">


                    <ActionCard
                        title="Ask AI"
                        description="Ask questions about organizational knowledge."
                        icon={<Bot size={22} />}
                        onClick={() =>
                            openPage("/chat")
                        }
                    />


                    <ActionCard
                        title="Search Knowledge"
                        description="Search documents and organizational information."
                        icon={<Search size={22} />}
                        onClick={() =>
                            openPage("/search")
                        }
                    />


                    <ActionCard
                        title="Knowledge Graph"
                        description="Explore projects, technologies and relationships."
                        icon={<Network size={22} />}
                        onClick={() =>
                            openPage("/graph")
                        }
                    />


                    <ActionCard
                        title="Documents"
                        description="Browse available organizational documents."
                        icon={<FileText size={22} />}
                        onClick={() =>
                            openPage("/documents")
                        }
                    />

                </div>

            </div>


            {/* =========================================
                Employee Overview
            ========================================== */}

            <div className="grid grid-cols-1 gap-5 md:grid-cols-3">


                <InfoCard
                    title="Conversations"
                    value={conversations.length}
                    icon={<MessageSquare size={21} />}
                />


                <InfoCard
                    title="Role"
                    value={
                        user?.role === "employee"
                            ? "Employee"
                            : user?.role || "-"
                    }
                    icon={<Bot size={21} />}
                />


                <InfoCard
                    title="Organization"
                    value={String(
                        user?.organization_id || "-"
                    )}
                    icon={<Network size={21} />}
                />

            </div>


            {/* =========================================
                Recent Conversations
            ========================================== */}

            <div className="rounded-xl border bg-white p-5 shadow-sm">

                <div className="flex items-center justify-between">

                    <div>

                        <h2 className="text-lg font-semibold text-slate-900">
                            Recent Conversations
                        </h2>

                        <p className="mt-1 text-sm text-slate-500">
                            Your recent AI assistant conversations
                        </p>

                    </div>


                    <button
                        onClick={() =>
                            openPage("/chat")
                        }
                        className="inline-flex items-center gap-2 text-sm font-medium text-slate-700 hover:text-slate-900"
                    >

                        View all

                        <ArrowRight size={16} />

                    </button>

                </div>


                <div className="mt-5">

                    {loading ? (

                        <div className="flex items-center justify-center py-8">

                            <Loader2
                                size={20}
                                className="animate-spin text-slate-400"
                            />

                        </div>

                    ) : conversations.length === 0 ? (

                        <div className="py-8 text-center">

                            <MessageSquare
                                size={28}
                                className="mx-auto text-slate-300"
                            />

                            <p className="mt-3 text-sm text-slate-400">
                                No conversations yet.
                            </p>

                            <button
                                onClick={() =>
                                    openPage("/chat")
                                }
                                className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
                            >
                                Start a conversation
                            </button>

                        </div>

                    ) : (

                        <div className="space-y-2">

                            {conversations.map(
                                (conversation) => (

                                    <button
                                        key={
                                            conversation.id
                                        }
                                        onClick={() =>
                                            openPage(
                                                `/chat?conversation=${conversation.id}`
                                            )
                                        }
                                        className="flex w-full items-center justify-between rounded-lg border p-4 text-left transition hover:bg-slate-50"
                                    >

                                        <div className="min-w-0">

                                            <p className="truncate text-sm font-medium text-slate-800">

                                                {conversation.title ||
                                                    "New conversation"}

                                            </p>

                                            <p className="mt-1 text-xs text-slate-400">

                                                {new Date(
                                                    conversation.created_at
                                                ).toLocaleDateString()}

                                            </p>

                                        </div>


                                        <ArrowRight
                                            size={17}
                                            className="shrink-0 text-slate-400"
                                        />

                                    </button>

                                )
                            )}

                        </div>

                    )}

                </div>

            </div>


            {/* =========================================
                How To Use
            ========================================== */}

            <div className="rounded-xl border bg-white p-5 shadow-sm">

                <h2 className="text-lg font-semibold text-slate-900">
                    Employee Knowledge Workflow
                </h2>

                <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-4">

                    <WorkflowStep
                        number="1"
                        title="Search"
                        text="Find relevant organizational knowledge."
                    />

                    <WorkflowStep
                        number="2"
                        title="Ask AI"
                        text="Ask questions in natural language."
                    />

                    <WorkflowStep
                        number="3"
                        title="Explore"
                        text="Inspect graph relationships and references."
                    />

                    <WorkflowStep
                        number="4"
                        title="Learn"
                        text="Use grounded organizational information."
                    />

                </div>

            </div>

        </div>
    );
}


/* ================================================
   Action Card
================================================ */

function ActionCard(
    {
        title,
        description,
        icon,
        onClick,
    }: {
        title: string;
        description: string;
        icon: ReactNode;
        onClick: () => void;
    }
) {

    return (

        <button
            onClick={onClick}
            className="group rounded-xl border bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
        >

            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
                {icon}
            </div>


            <h3 className="font-semibold text-slate-900">
                {title}
            </h3>


            <p className="mt-2 text-sm leading-5 text-slate-500">
                {description}
            </p>


            <div className="mt-4 flex items-center gap-1 text-sm font-medium text-slate-700">

                Open

                <ArrowRight
                    size={15}
                    className="transition group-hover:translate-x-1"
                />

            </div>

        </button>
    );
}


/* ================================================
   Info Card
================================================ */

function InfoCard(
    {
        title,
        value,
        icon,
    }: {
        title: string;
        value: string | number;
        icon: ReactNode;
    }
) {

    return (

        <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

                <p className="text-sm text-slate-500">
                    {title}
                </p>

                <div className="rounded-lg bg-slate-100 p-2 text-slate-700">
                    {icon}
                </div>

            </div>


            <p className="mt-3 text-2xl font-bold text-slate-900">
                {value}
            </p>

        </div>
    );
}


/* ================================================
   Workflow Step
================================================ */

function WorkflowStep(
    {
        number,
        title,
        text,
    }: {
        number: string;
        title: string;
        text: string;
    }
) {

    return (

        <div className="rounded-lg bg-slate-50 p-4">

            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-900 text-sm font-semibold text-white">
                {number}
            </div>

            <h3 className="mt-3 font-medium text-slate-900">
                {title}
            </h3>

            <p className="mt-1 text-sm leading-5 text-slate-500">
                {text}
            </p>

        </div>
    );
}


export default EmployeeDashboard;