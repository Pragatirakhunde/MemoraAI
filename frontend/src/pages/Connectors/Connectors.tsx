import {
    useEffect,
    useState,
} from "react";

import {
    AlertCircle,
    CheckCircle2,
    Loader2,
    Plus,
    RefreshCw,
    Trash2,
} from "lucide-react";

import {
    getProjects,
} from "../../services/api/projects";

import type {
    Project,
} from "../../services/api/projects";

import {
    createDataSource,
    deactivateDataSource,
    getDataSources,
    validateDataSource,
} from "../../services/api/dataSources";

import type {
    DataSource,
} from "../../services/api/dataSources";

import {
    queueBackgroundSync,
} from "../../services/api/sync";


function Connectors() {

    const [projects, setProjects] =
        useState<Project[]>([]);

    const [dataSources, setDataSources] =
        useState<DataSource[]>([]);

    const [loading, setLoading] =
        useState(true);

    const [saving, setSaving] =
        useState(false);

    const [actionId, setActionId] =
        useState<number | null>(null);

    const [error, setError] =
        useState("");

    const [message, setMessage] =
        useState("");

    const [showForm, setShowForm] =
        useState(false);

    const [name, setName] =
        useState("");

    const [sourceType, setSourceType] =
        useState<
            "local_directory" | "git"
        >("local_directory");

    const [projectId, setProjectId] =
        useState("");

    const [configText, setConfigText] =
        useState("{}");


    const loadData = async () => {

        setLoading(true);
        setError("");

        try {

            const [
                projectData,
                sourceData,
            ] = await Promise.all([
                getProjects(),
                getDataSources(),
            ]);

            setProjects(projectData);
            setDataSources(sourceData);

        } catch (err: any) {

            console.error(
                "Failed to load data sources:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to load data sources."
            );

        } finally {

            setLoading(false);

        }
    };


    useEffect(() => {
        loadData();
    }, []);


    const resetForm = () => {

        setName("");
        setSourceType("local_directory");
        setProjectId("");
        setConfigText("{}");
        setShowForm(false);

    };


    const handleCreate = async (
        event: React.FormEvent
    ) => {

        event.preventDefault();

        setError("");
        setMessage("");

        if (!name.trim()) {

            setError(
                "Data source name is required."
            );

            return;
        }

        let config: Record<
            string,
            unknown
        >;

        try {

            config = JSON.parse(
                configText
            );

        } catch {

            setError(
                "Configuration must be valid JSON."
            );

            return;
        }

        if (
            typeof config !== "object" ||
            config === null ||
            Array.isArray(config)
        ) {

            setError(
                "Configuration must be a JSON object."
            );

            return;
        }

        setSaving(true);

        try {

            await createDataSource({
                name: name.trim(),
                source_type: sourceType,
                config,
                project_id:
                    projectId === ""
                        ? null
                        : Number(projectId),
            });

            setMessage(
                "Data source created successfully."
            );

            resetForm();

            await loadData();

        } catch (err: any) {

            console.error(
                "Failed to create data source:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to create data source."
            );

        } finally {

            setSaving(false);

        }
    };


    const handleValidate = async (
        dataSourceId: number
    ) => {

        setActionId(dataSourceId);
        setError("");
        setMessage("");

        try {

            const result =
                await validateDataSource(
                    dataSourceId
                );

            if (result.valid) {

                setMessage(
                    "Data source validation succeeded."
                );

            } else {

                setError(
                    result.message ||
                    "Data source validation failed."
                );

            }

            await loadData();

        } catch (err: any) {

            console.error(
                "Failed to validate data source:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to validate data source."
            );

        } finally {

            setActionId(null);

        }
    };


    const handleSync = async (
        dataSourceId: number
    ) => {

        setActionId(dataSourceId);
        setError("");
        setMessage("");

        try {

            await queueBackgroundSync(
                dataSourceId
            );

            setMessage(
                "Background synchronization queued."
            );

        } catch (err: any) {

            console.error(
                "Failed to queue synchronization:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to queue synchronization."
            );

        } finally {

            setActionId(null);

        }
    };


    const handleDeactivate = async (
        dataSourceId: number
    ) => {

        setActionId(dataSourceId);
        setError("");
        setMessage("");

        try {

            await deactivateDataSource(
                dataSourceId
            );

            setMessage(
                "Data source deactivated."
            );

            await loadData();

        } catch (err: any) {

            console.error(
                "Failed to deactivate data source:",
                err
            );

            setError(
                err?.response?.data?.detail ||
                "Failed to deactivate data source."
            );

        } finally {

            setActionId(null);

        }
    };


    const getProjectName = (
        id: number | null
    ) => {

        if (id === null) {
            return "Organization Memory";
        }

        const project =
            projects.find(
                (item) => item.id === id
            );

        return project?.name ||
            `Project #${id}`;
    };


    if (loading) {

        return (

            <div className="flex min-h-100 items-center justify-center">

                <div className="flex items-center gap-2 text-sm text-slate-500">

                    <Loader2
                        size={20}
                        className="animate-spin"
                    />

                    Loading data sources...

                </div>

            </div>
        );
    }


    return (

        <div className="space-y-6">

            <div className="flex items-center justify-between">

                <div>

                    <h2 className="text-3xl font-bold text-slate-900">
                        Data Sources
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                        Manage organization and project knowledge sources.
                    </p>

                </div>


                <div className="flex items-center gap-3">

                    <button
                        onClick={loadData}
                        className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                    >
                        <RefreshCw size={16} />
                        Refresh
                    </button>


                    <button
                        onClick={() =>
                            setShowForm(
                                !showForm
                            )
                        }
                        className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                    >
                        <Plus size={16} />
                        Add Data Source
                    </button>

                </div>

            </div>


            {error && (

                <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">

                    <AlertCircle
                        size={18}
                        className="mt-0.5"
                    />

                    <span>
                        {error}
                    </span>

                </div>

            )}


            {message && (

                <div className="flex items-start gap-3 rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-700">

                    <CheckCircle2
                        size={18}
                        className="mt-0.5"
                    />

                    <span>
                        {message}
                    </span>

                </div>

            )}


            {showForm && (

                <form
                    onSubmit={handleCreate}
                    className="rounded-xl border bg-white p-6 shadow-sm"
                >

                    <h3 className="text-lg font-semibold text-slate-900">
                        Create Data Source
                    </h3>

                    <p className="mt-1 text-sm text-slate-500">
                        Choose whether this source belongs to organizational memory or a project.
                    </p>


                    <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2">

                        <div>

                            <label className="mb-2 block text-sm font-medium text-slate-700">
                                Name
                            </label>

                            <input
                                value={name}
                                onChange={(event) =>
                                    setName(
                                        event.target.value
                                    )
                                }
                                placeholder="PayFlow Knowledge Source"
                                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500"
                            />

                        </div>


                        <div>

                            <label className="mb-2 block text-sm font-medium text-slate-700">
                                Source Type
                            </label>

                            <select
                                value={sourceType}
                                onChange={(event) =>
                                    setSourceType(
                                        event.target.value as
                                            | "local_directory"
                                            | "git"
                                    )
                                }
                                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500"
                            >

                                <option value="local_directory">
                                    Local Directory
                                </option>

                                <option value="git">
                                    Git
                                </option>

                            </select>

                        </div>


                        <div>

                            <label className="mb-2 block text-sm font-medium text-slate-700">
                                Project
                            </label>

                            <select
                                value={projectId}
                                onChange={(event) =>
                                    setProjectId(
                                        event.target.value
                                    )
                                }
                                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500"
                            >

                                <option value="">
                                    Organization Memory
                                </option>

                                {projects
                                    .filter(
                                        (project) =>
                                            project.status ===
                                            "active"
                                    )
                                    .map(
                                        (project) => (

                                            <option
                                                key={project.id}
                                                value={project.id}
                                            >
                                                {project.name}
                                            </option>

                                        )
                                    )}

                            </select>

                        </div>


                        <div>

                            <label className="mb-2 block text-sm font-medium text-slate-700">
                                Configuration JSON
                            </label>

                            <textarea
                                value={configText}
                                onChange={(event) =>
                                    setConfigText(
                                        event.target.value
                                    )
                                }
                                rows={6}
                                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 font-mono text-sm outline-none focus:border-blue-500"
                            />

                        </div>

                    </div>


                    <div className="mt-6 flex justify-end gap-3">

                        <button
                            type="button"
                            onClick={resetForm}
                            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            disabled={saving}
                            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                        >

                            {saving && (
                                <Loader2
                                    size={16}
                                    className="animate-spin"
                                />
                            )}

                            Create Data Source

                        </button>

                    </div>

                </form>

            )}


            <div className="rounded-xl border bg-white shadow-sm">

                <div className="border-b p-5">

                    <h3 className="text-lg font-semibold text-slate-900">
                        Existing Data Sources
                    </h3>

                    <p className="mt-1 text-sm text-slate-500">
                        {dataSources.length} data source
                        {dataSources.length === 1
                            ? ""
                            : "s"}
                    </p>

                </div>


                {dataSources.length === 0 ? (

                    <div className="p-10 text-center">

                        <p className="text-sm text-slate-500">
                            No data sources created yet.
                        </p>

                    </div>

                ) : (

                    <div className="overflow-x-auto">

                        <table className="w-full text-left text-sm">

                            <thead>

                                <tr className="border-b bg-slate-50">

                                    <th className="px-5 py-3 font-medium text-slate-500">
                                        Name
                                    </th>

                                    <th className="px-5 py-3 font-medium text-slate-500">
                                        Type
                                    </th>

                                    <th className="px-5 py-3 font-medium text-slate-500">
                                        Scope
                                    </th>

                                    <th className="px-5 py-3 font-medium text-slate-500">
                                        Status
                                    </th>

                                    <th className="px-5 py-3 font-medium text-slate-500">
                                        Last Synced
                                    </th>

                                    <th className="px-5 py-3 text-right font-medium text-slate-500">
                                        Actions
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {dataSources.map(
                                    (source) => {

                                        const busy =
                                            actionId ===
                                            source.id;

                                        return (

                                            <tr
                                                key={source.id}
                                                className="border-b last:border-b-0"
                                            >

                                                <td className="px-5 py-4">

                                                    <div className="font-medium text-slate-800">
                                                        {source.name}
                                                    </div>

                                                </td>


                                                <td className="px-5 py-4 text-slate-600">
                                                    {source.source_type}
                                                </td>


                                                <td className="px-5 py-4">

                                                    <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                                                        {getProjectName(
                                                            source.project_id
                                                        )}
                                                    </span>

                                                </td>


                                                <td className="px-5 py-4">

                                                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                                                        {source.status}
                                                    </span>

                                                </td>


                                                <td className="px-5 py-4 text-slate-500">

                                                    {source.last_synced_at
                                                        ? new Date(
                                                            source.last_synced_at
                                                        ).toLocaleString()
                                                        : "Never"}

                                                </td>


                                                <td className="px-5 py-4">

                                                    <div className="flex justify-end gap-2">

                                                        <button
                                                            onClick={() =>
                                                                handleValidate(
                                                                    source.id
                                                                )
                                                            }
                                                            disabled={busy}
                                                            className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                                                        >
                                                            Validate
                                                        </button>


                                                        <button
                                                            onClick={() =>
                                                                handleSync(
                                                                    source.id
                                                                )
                                                            }
                                                            disabled={
                                                                busy ||
                                                                source.status ===
                                                                    "inactive"
                                                            }
                                                            className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                                                        >
                                                            Sync
                                                        </button>


                                                        {source.status !==
                                                            "inactive" && (

                                                            <button
                                                                onClick={() =>
                                                                    handleDeactivate(
                                                                        source.id
                                                                    )
                                                                }
                                                                disabled={busy}
                                                                className="inline-flex items-center gap-1 rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
                                                            >
                                                                <Trash2
                                                                    size={13}
                                                                />
                                                                Deactivate
                                                            </button>

                                                        )}

                                                    </div>

                                                </td>

                                            </tr>

                                        );
                                    }
                                )}

                            </tbody>

                        </table>

                    </div>

                )}

            </div>

        </div>
    );
}


export default Connectors;