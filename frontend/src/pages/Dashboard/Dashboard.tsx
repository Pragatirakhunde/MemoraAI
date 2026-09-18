import {
    useEffect,
    useState,
} from "react";

import type {
    ReactNode,
} from "react";


import {
    Building2,
    Database,
    FileText,
    Layers3,
    MessageSquare,
    RefreshCw,
    Loader2,
    AlertCircle,
} from "lucide-react";

import {
    getAdminDashboard,
} from "../../services/api/adminDashboard";

import type {
    AdminDashboardData,
} from "../../services/api/adminDashboard";

import {
    useAuth,
} from "../../context/AuthContext";

import EmployeeDashboard from "./EmployeeDashboard";

import {
    queueAllBackgroundSyncs,
} from "../../services/api/sync";

function AdminDashboard() {

    const [data, setData] =
        useState<AdminDashboardData | null>(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");

    const [syncing, setSyncing] =
        useState(false);

    const [syncMessage, setSyncMessage] =
        useState("");


    const loadDashboard = async () => {

        setLoading(true);
        setError("");

        try {

            const dashboard =
                await getAdminDashboard();

            setData(dashboard);

        } catch (err: any) {

            console.error(
                "Failed to load admin dashboard:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to load dashboard data."
            );

        } finally {

            setLoading(false);
        }
    };

    const handleSyncAll = async () => {
        setSyncing(true);
        setSyncMessage("");
        setError("");

        try {

            await queueAllBackgroundSyncs();

            setSyncMessage(
                "Synchronization queued. Processing in background..."
            );

            for (let attempt = 0; attempt < 15; attempt++) {

                await new Promise((resolve) =>
                    setTimeout(resolve, 2000)
                );

                const dashboard =
                    await getAdminDashboard();

                setData(dashboard);

                const hasActiveJobs =
                    dashboard.sync_jobs.pending > 0 ||
                    dashboard.sync_jobs.running > 0;

                if (!hasActiveJobs) {

                    setSyncMessage(
                        "Synchronization completed."
                    );

                    break;
                }

                setSyncMessage(
                    "Synchronization is still running..."
                );
            }

        } catch (err: any) {

            console.error(
                "Failed to synchronize:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to synchronize data sources."
            );

        } finally {

            setSyncing(false);
        }
    };


    useEffect(() => {
        loadDashboard();
    }, []);


    if (loading) {

        return (

            <div className="flex min-h-125 items-center justify-center">

                <div className="flex items-center gap-2 text-sm text-slate-500">

                    <Loader2
                        size={20}
                        className="animate-spin"
                    />

                    Loading dashboard...

                </div>

            </div>
        );
    }


    if (error) {

        return (

            <div className="rounded-xl border border-red-200 bg-red-50 p-6">

                <div className="flex items-start gap-3">

                    <AlertCircle
                        size={20}
                        className="mt-0.5 text-red-600"
                    />

                    <div>

                        <h2 className="font-semibold text-red-800">
                            Unable to load dashboard
                        </h2>

                        <p className="mt-1 text-sm text-red-700">
                            {error}
                        </p>

                        <button
                            onClick={loadDashboard}
                            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
                        >
                            <RefreshCw size={16} />
                            Retry
                        </button>

                    </div>

                </div>

            </div>
        );
    }


    if (!data) {
        return null;
    }


    return (

        <div className="space-y-6">

            {/* =========================================
                Header
            ========================================== */}

            <div className="flex items-center justify-between">

                <div>

                    <h2 className="text-3xl font-bold text-slate-900">
                        Admin Dashboard
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                        {data.organization.name ||
                            "Organization overview"}
                    </p>

                </div>


                <div className="flex items-center gap-3">

                    {/* =========================================
                        Sync All Sources
                    ========================================== */}

                    <button
                        onClick={handleSyncAll}
                        disabled={syncing}
                        className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                    >

                        {syncing ? (

                            <Loader2
                                size={16}
                                className="animate-spin"
                            />

                        ) : (

                            <RefreshCw size={16} />

                        )}

                        {syncing
                            ? "Queuing..."
                            : "Sync All Sources"}

                    </button>


                    {/* =========================================
                        Refresh Dashboard
                    ========================================== */}

                    <button
                        onClick={loadDashboard}
                        className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                    >

                        <RefreshCw size={16} />

                        Refresh

                    </button>

                </div>

            </div>

            {syncMessage && (
                <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                    {syncMessage}
                </div>
            )}


            {/* =========================================
                Main Statistics
            ========================================== */}

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">


                <Card
                    title="Organizations"
                    value="1"
                    icon={<Building2 size={22} />}
                />


                <Card
                    title="Data Sources"
                    value={String(
                        data.sources.total
                    )}
                    icon={<Database size={22} />}
                />


                <Card
                    title="Documents"
                    value={String(
                        data.documents.total
                    )}
                    icon={<FileText size={22} />}
                />


                <Card
                    title="Chunks"
                    value={String(
                        data.chunks.total
                    )}
                    icon={<Layers3 size={22} />}
                />


                <Card
                    title="Conversations"
                    value={String(
                        data.conversations.total
                    )}
                    icon={<MessageSquare size={22} />}
                />

            </div>


            {/* =========================================
                Users + Sources
            ========================================== */}

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">


                <SectionCard title="Users">

                    <StatRow
                        label="Total users"
                        value={data.users.total}
                    />

                    <StatRow
                        label="Active users"
                        value={data.users.active}
                    />

                    <StatRow
                        label="Admins"
                        value={data.users.admins}
                    />

                    <StatRow
                        label="Employees"
                        value={data.users.employees}
                    />

                </SectionCard>


                <SectionCard title="Data Sources">

                    <StatRow
                        label="Total sources"
                        value={data.sources.total}
                    />

                    <StatRow
                        label="Active"
                        value={data.sources.active}
                    />

                    <StatRow
                        label="Inactive"
                        value={data.sources.inactive}
                    />

                    <StatRow
                        label="Error"
                        value={data.sources.error}
                    />

                </SectionCard>

            </div>


            {/* =========================================
                Documents + Sync
            ========================================== */}

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">


                <SectionCard title="Document Processing">

                    <StatRow
                        label="Total documents"
                        value={data.documents.total}
                    />

                    <StatRow
                        label="Completed"
                        value={data.documents.completed}
                    />

                    <StatRow
                        label="Processing"
                        value={data.documents.processing}
                    />

                    <StatRow
                        label="Pending"
                        value={data.documents.pending}
                    />

                    <StatRow
                        label="Failed"
                        value={data.documents.failed}
                    />

                </SectionCard>


                <SectionCard title="Synchronization">

                    <StatRow
                        label="Total sync jobs"
                        value={data.sync_jobs.total}
                    />

                    <StatRow
                        label="Completed"
                        value={data.sync_jobs.completed}
                    />

                    <StatRow
                        label="Running"
                        value={data.sync_jobs.running}
                    />

                    <StatRow
                        label="Pending"
                        value={data.sync_jobs.pending}
                    />

                    <StatRow
                        label="Failed"
                        value={data.sync_jobs.failed}
                    />

                </SectionCard>

            </div>


            {/* =========================================
                Knowledge Graph
            ========================================== */}

            <SectionCard title="Knowledge Graph">

                <StatRow
                    label="Total nodes"
                    value={
                        data.knowledge_graph.total_nodes
                    }
                />

                <StatRow
                    label="Projects"
                    value={
                        data.knowledge_graph.projects
                    }
                />

                <StatRow
                    label="Technologies"
                    value={
                        data.knowledge_graph.technologies
                    }
                />

                <StatRow
                    label="Databases"
                    value={
                        data.knowledge_graph.databases
                    }
                />

                <StatRow
                    label="Documents"
                    value={
                        data.knowledge_graph.documents
                    }
                />

                <StatRow
                    label="Relationships"
                    value={
                        data.knowledge_graph.total_relationships
                    }
                />

            </SectionCard>

            {/* =========================================
                AI Usage
            ========================================== */}

            <SectionCard title="AI Usage">

                <StatRow
                    label="Total conversations"
                    value={
                        data.conversations.total
                    }
                />

                <StatRow
                    label="User queries"
                    value={
                        data.ai_usage.queries
                    }
                />

                <StatRow
                    label="AI responses"
                    value={
                        data.ai_usage.responses
                    }
                />

            </SectionCard>


            {/* =========================================
                Source Processing Summary
            ========================================== */}

            <SectionCard title="Processing Summary">

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">

                    <SummaryBox
                        label="Files Found"
                        value={
                            data.sync_jobs.files_found
                        }
                    />

                    <SummaryBox
                        label="Files Processed"
                        value={
                            data.sync_jobs.files_processed
                        }
                    />

                    <SummaryBox
                        label="Messages"
                        value={
                            data.conversations.messages
                        }
                    />

                </div>

            </SectionCard>

            {/* =========================================
                Recent Sync Activity
            ========================================== */}

            <div className="rounded-xl border bg-white p-5 shadow-sm">

                <div className="mb-4">

                    <h3 className="text-lg font-semibold text-slate-900">
                        Recent Sync Activity
                    </h3>

                    <p className="mt-1 text-sm text-slate-500">
                        Latest synchronization jobs
                    </p>

                </div>


                {data.recent_activity.length === 0 ? (

                    <p className="py-6 text-center text-sm text-slate-400">
                        No synchronization activity yet.
                    </p>

                ) : (

                    <div className="overflow-x-auto">

                        <table className="w-full text-left text-sm">

                            <thead>

                                <tr className="border-b">

                                    <th className="pb-3 font-medium text-slate-500">
                                        Source
                                    </th>

                                    <th className="pb-3 font-medium text-slate-500">
                                        Status
                                    </th>

                                    <th className="pb-3 font-medium text-slate-500">
                                        Files
                                    </th>

                                    <th className="pb-3 font-medium text-slate-500">
                                        Created
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {data.recent_activity.map(
                                    (activity) => (

                                        <tr
                                            key={activity.id}
                                            className="border-b last:border-b-0"
                                        >

                                            <td className="py-3 font-medium text-slate-800">
                                                {activity.source_name}
                                            </td>


                                            <td className="py-3">

                                                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                                                    {activity.status}
                                                </span>

                                            </td>


                                            <td className="py-3 text-slate-600">

                                                {activity.files_processed}
                                                {" / "}
                                                {activity.files_found}

                                            </td>


                                            <td className="py-3 text-slate-500">

                                                {new Date(
                                                    activity.created_at
                                                ).toLocaleString()}

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    </div>

                )}

            </div>
            
            {/* =========================================
                System Health
            ========================================== */}

            <SectionCard title="System Health">

                <HealthStatus
                    label="PostgreSQL"
                    status={data.system_health.database}
                />

                <HealthStatus
                    label="Ingestion"
                    status={data.system_health.ingestion}
                />

            </SectionCard>

            {/* =========================================
                Last Sync
            ========================================== */}

            <div className="rounded-xl border bg-white p-5 shadow-sm">

                <p className="text-sm font-medium text-slate-700">
                    Last synchronization
                </p>

                <p className="mt-2 text-sm text-slate-500">

                    {data.sources.last_synced_at
                        ? new Date(
                            data.sources.last_synced_at
                        ).toLocaleString()
                        : "No synchronization recorded yet"}

                </p>

            </div>

        </div>
    );
}


/* ================================================
   Main Card
================================================ */

function Card(
    {
        title,
        value,
        icon,
    }: {
        title: string;
        value: string;
        icon: ReactNode;
    }
) {

    return (

        <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

                <div>

                    <p className="text-sm text-slate-500">
                        {title}
                    </p>

                    <h2 className="mt-2 text-3xl font-bold text-slate-900">
                        {value}
                    </h2>

                </div>


                <div className="rounded-lg bg-slate-100 p-3 text-slate-700">

                    {icon}

                </div>

            </div>

        </div>
    );
}


/* ================================================
   Section Card
================================================ */

function SectionCard(
    {
        title,
        children,
    }: {
        title: string;
        children: ReactNode;
    }
) {

    return (

        <div className="rounded-xl border bg-white p-5 shadow-sm">

            <h3 className="mb-4 text-lg font-semibold text-slate-900">
                {title}
            </h3>

            <div className="space-y-3">
                {children}
            </div>

        </div>
    );
}


/* ================================================
   Stat Row
================================================ */

function StatRow(
    {
        label,
        value,
    }: {
        label: string;
        value: number;
    }
) {

    return (

        <div className="flex items-center justify-between border-b pb-2 last:border-b-0">

            <span className="text-sm text-slate-500">
                {label}
            </span>

            <span className="font-semibold text-slate-800">
                {value}
            </span>

        </div>
    );
}

function HealthStatus(
    {
        label,
        status,
    }: {
        label: string;
        status: string;
    }
) {

    return (

        <div className="flex items-center justify-between border-b pb-2 last:border-b-0">

            <span className="text-sm text-slate-500">
                {label}
            </span>

            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                {status}
            </span>

        </div>
    );
}


/* ================================================
   Summary Box
================================================ */

function SummaryBox(
    {
        label,
        value,
    }: {
        label: string;
        value: number;
    }
) {

    return (

        <div className="rounded-lg bg-slate-50 p-4">

            <p className="text-sm text-slate-500">
                {label}
            </p>

            <p className="mt-2 text-2xl font-bold text-slate-900">
                {value}
            </p>

        </div>
    );
}

function Dashboard() {

    const { user } = useAuth();

    if (user?.role === "employee") {

        return <EmployeeDashboard />;

    }

    return <AdminDashboard />;
}


export default Dashboard;