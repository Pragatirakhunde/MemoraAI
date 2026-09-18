import { useEffect, useMemo, useState } from "react";
import type { MouseEvent } from "react";

import {
    Background,
    Controls,
    MiniMap,
    Panel,
    ReactFlow,
} from "@xyflow/react";

import type {
    Edge,
    Node,
} from "@xyflow/react";

import {
    expandEntity,
    getGraphProjects,
    getProjectGraph,
} from "../../services/api/graph";

import type {
    GraphProject,
} from "../../services/api/graph";


// =====================================================
// React Flow Types
// =====================================================

type GraphNodeData = {
    label: string;
    entityType: string;
    [key: string]: unknown;
};

type GraphFlowNode = Node<
    GraphNodeData,
    "default"
>;


// =====================================================
// Component
// =====================================================

export default function KnowledgeGraph() {

    // -------------------------------------------------
    // Projects
    // -------------------------------------------------

    const [projects, setProjects] =
        useState<GraphProject[]>([]);

    const [selectedProject, setSelectedProject] =
        useState("");

    // -------------------------------------------------
    // Graph
    // -------------------------------------------------

    const [nodes, setNodes] =
        useState<GraphFlowNode[]>([]);

    const [edges, setEdges] =
        useState<Edge[]>([]);

    // -------------------------------------------------
    // Loading / Error
    // -------------------------------------------------

    const [loadingProjects, setLoadingProjects] =
        useState(false);

    const [loadingGraph, setLoadingGraph] =
        useState(false);

    const [error, setError] =
        useState("");

    // -------------------------------------------------
    // Selection
    // -------------------------------------------------

    const [selectedNode, setSelectedNode] =
        useState<GraphFlowNode | null>(null);

    const [selectedEntityId, setSelectedEntityId] =
        useState<string | null>(null);

    const [selectedEdge, setSelectedEdge] =
        useState<Edge | null>(null);

    // -------------------------------------------------
    // Expansion
    // -------------------------------------------------

    const [expanding, setExpanding] =
        useState(false);

    const [expansionHops, setExpansionHops] =
        useState(1);

    // -------------------------------------------------
    // P11.6 Search + Filtering
    // -------------------------------------------------

    const [searchTerm, setSearchTerm] =
        useState("");

    const [entityTypeFilter, setEntityTypeFilter] =
        useState("all");


    // =================================================
    // Load Projects
    // =================================================

    useEffect(() => {

        const loadProjects = async () => {

            setLoadingProjects(true);
            setError("");

            try {

                const data =
                    await getGraphProjects();

                setProjects(data);

                if (data.length > 0) {

                    setSelectedProject(
                        (current) =>
                            current || data[0].name
                    );
                }

            } catch (err: any) {

                console.error(
                    "Failed to load graph projects:",
                    err
                );

                setError(
                    err?.response?.data?.detail ||
                    err?.message ||
                    "Failed to load graph projects."
                );

            } finally {

                setLoadingProjects(false);
            }
        };

        loadProjects();

    }, []);


    // =================================================
    // Load Project Graph
    // =================================================

    useEffect(() => {

        if (!selectedProject) {
            return;
        }

        const loadProjectGraph =
            async () => {

                setLoadingGraph(true);
                setError("");

                setSelectedNode(null);
                setSelectedEntityId(null);
                setSelectedEdge(null);

                try {

                    const graph =
                        await getProjectGraph(
                            selectedProject
                        );

                    const apiNodes =
                        Array.isArray(graph?.nodes)
                            ? graph.nodes
                            : [];

                    const apiEdges =
                        Array.isArray(graph?.edges)
                            ? graph.edges
                            : [];


                    // ---------------------------------
                    // Convert API Nodes
                    // ---------------------------------

                    const projectNode =
                        apiNodes.find(
                            (node) =>
                                String(
                                    node.type || ""
                                ).toLowerCase() ===
                                "project"
                        );

                    const otherNodes =
                        apiNodes.filter(
                            (node) =>
                                node !== projectNode
                        );


                    const graphNodes:
                        GraphFlowNode[] = [];


                    // ---------------------------------
                    // Project Root Node
                    // ---------------------------------

                    if (projectNode) {

                        graphNodes.push({

                            id: String(
                                projectNode.id
                            ),

                            type: "default",

                            position: {
                                x: 400,
                                y: 250,
                            },

                            data: {
                                label:
                                    projectNode.label,

                                entityType:
                                    projectNode.type,
                            },

                            style: {

                                background:
                                    "#0f172a",

                                color:
                                    "#ffffff",

                                border:
                                    "1px solid #0f172a",

                                borderRadius:
                                    "12px",

                                padding:
                                    "12px 18px",

                                fontWeight:
                                    600,

                                minWidth:
                                    "180px",

                                textAlign:
                                    "center",
                            },
                        });
                    }


                    // ---------------------------------
                    // Other Nodes
                    // ---------------------------------

                    const radius =
                        300;

                    otherNodes.forEach(
                        (
                            node,
                            index
                        ) => {

                            const angle =
                                (
                                    index /
                                    Math.max(
                                        otherNodes.length,
                                        1
                                    )
                                ) *
                                Math.PI *
                                2;

                            const x =
                                400 +
                                radius *
                                Math.cos(
                                    angle
                                );

                            const y =
                                250 +
                                radius *
                                Math.sin(
                                    angle
                                );


                            const entityType =
                                String(
                                    node.type ||
                                    "Entity"
                                );


                            graphNodes.push({

                                id: String(
                                    node.id
                                ),

                                type: "default",

                                position: {
                                    x,
                                    y,
                                },

                                data: {

                                    label:
                                        node.label,

                                    entityType:
                                        entityType,
                                },

                                style:
                                    getNodeStyle(
                                        entityType
                                    ),
                            });
                        }
                    );


                    // ---------------------------------
                    // Convert API Edges
                    // ---------------------------------

                    const graphEdges:
                        Edge[] =
                        apiEdges.map(
                            (
                                edge,
                                index
                            ) => ({

                                id:
                                    `edge-${index}-${String(
                                        edge.source
                                    )}-${String(
                                        edge.target
                                    )}`,

                                source:
                                    String(
                                        edge.source
                                    ),

                                target:
                                    String(
                                        edge.target
                                    ),

                                label:
                                    edge.relationship,

                                type:
                                    "default",

                                animated:
                                    false,

                                style: {
                                    stroke:
                                        "#94a3b8",

                                    strokeWidth:
                                        1.5,
                                },

                                labelStyle: {
                                    fill:
                                        "#475569",

                                    fontSize:
                                        11,

                                    fontWeight:
                                        500,
                                },

                                labelBgStyle: {
                                    fill:
                                        "#ffffff",

                                    fillOpacity:
                                        0.9,
                                },
                            })
                        );


                    setNodes(
                        graphNodes
                    );

                    setEdges(
                        graphEdges
                    );

                } catch (err: any) {

                    console.error(
                        "Failed to load project graph:",
                        err
                    );

                    setNodes([]);
                    setEdges([]);

                    setError(
                        err?.response?.data?.detail ||
                        err?.message ||
                        "Failed to load project graph."
                    );

                } finally {

                    setLoadingGraph(false);
                }
            };


        loadProjectGraph();

    }, [selectedProject]);


    // =================================================
    // Search / Filter Data
    // =================================================

    const entityTypes =
        useMemo(() => {

            const types =
                new Set<string>();

            nodes.forEach(
                (node) => {

                    if (
                        node.data?.entityType
                    ) {

                        types.add(
                            String(
                                node.data.entityType
                            )
                        );
                    }
                }
            );

            return Array.from(
                types
            ).sort();

        }, [nodes]);


    const filteredNodes =
        useMemo(() => {

            const search =
                searchTerm
                    .trim()
                    .toLowerCase();


            return nodes.filter(
                (node) => {

                    const label =
                        String(
                            node.data?.label ||
                            ""
                        ).toLowerCase();

                    const type =
                        String(
                            node.data?.entityType ||
                            ""
                        ).toLowerCase();

                    const id =
                        String(
                            node.id || ""
                        ).toLowerCase();


                    const matchesSearch =
                        !search ||
                        label.includes(
                            search
                        ) ||
                        type.includes(
                            search
                        ) ||
                        id.includes(
                            search
                        );


                    const matchesType =
                        entityTypeFilter ===
                            "all" ||
                        type ===
                            entityTypeFilter.toLowerCase();


                    return (
                        matchesSearch &&
                        matchesType
                    );
                }
            );

        }, [
            nodes,
            searchTerm,
            entityTypeFilter,
        ]);


    const filteredNodeIds =
        useMemo(
            () =>
                new Set(
                    filteredNodes.map(
                        (node) =>
                            node.id
                    )
                ),
            [filteredNodes]
        );


    const filteredEdges =
        useMemo(
            () =>
                edges.filter(
                    (edge) =>
                        filteredNodeIds.has(
                            edge.source
                        ) &&
                        filteredNodeIds.has(
                            edge.target
                        )
                ),
            [
                edges,
                filteredNodeIds,
            ]
        );


    // =================================================
    // Clear Selection When Filter Hides Node
    // =================================================

    useEffect(() => {

        if (
            selectedEntityId &&
            !filteredNodeIds.has(
                selectedEntityId
            )
        ) {

            setSelectedEntityId(
                null
            );

            setSelectedNode(
                null
            );
        }

    }, [
        selectedEntityId,
        filteredNodeIds,
    ]);


    // =================================================
    // Keep Selected Node Highlighted
    // =================================================

    useEffect(() => {

        setNodes(
            (currentNodes) =>
                currentNodes.map(
                    (node) => {

                        const isSelected =
                            String(node.id) ===
                            String(selectedEntityId);

                        return {
                            ...node,

                            selected:
                                isSelected,

                            style: {
                                ...node.style,

                                boxShadow:
                                    isSelected
                                        ? "0 0 0 3px rgba(15, 23, 42, 0.25)"
                                        : undefined,
                            },
                        };
                    }
                )
        );

    }, [selectedEntityId]);


    // =================================================
    // Node Click
    // =================================================

    const handleNodeClick = (
        _event: MouseEvent,
        node: GraphFlowNode
    ) => {

        setSelectedNode(
            node
        );

        setSelectedEntityId(
            String(node.id)
        );

        setSelectedEdge(
            null
        );
    };


    // =================================================
    // Edge Click
    // =================================================

    const handleEdgeClick = (
        _event: MouseEvent,
        edge: Edge
    ) => {

        setSelectedEdge(
            edge
        );

        setSelectedNode(
            null
        );

        setSelectedEntityId(
            null
        );
    };


    // =================================================
    // Expand Selected Entity
    // =================================================

    const handleExpandEntity =
        async () => {

            if (
                !selectedNode
            ) {
                return;
            }

            const entityName =
                String(
                    selectedNode.data
                        ?.label || ""
                ).trim();


            if (!entityName) {
                return;
            }


            setExpanding(
                true
            );

            setError("");


            try {

                const results =
                    await expandEntity(
                        entityName,
                        expansionHops
                    );


                if (
                    !Array.isArray(
                        results
                    ) ||
                    results.length === 0
                ) {

                    return;
                }


                // ---------------------------------
                // Existing graph
                // ---------------------------------

                const nextNodes =
                    [
                        ...nodes,
                    ];

                const nextEdges =
                    [
                        ...edges,
                    ];


                // ---------------------------------
                // Helper: Find Node By Label
                // ---------------------------------

                const findNodeByLabel =
                    (
                        label: string
                    ) => {

                        return nextNodes.find(
                            (node) =>
                                String(
                                    node.data
                                        ?.label ||
                                    ""
                                ).toLowerCase() ===
                                String(
                                    label
                                ).toLowerCase()
                        );
                    };


                // ---------------------------------
                // Helper: Create Node
                // ---------------------------------

                const createNode =
                    (
                        label: string,
                        entityType: string
                    ) => {

                        const existing =
                            findNodeByLabel(
                                label
                            );

                        if (existing) {
                            return existing;
                        }


                        const index =
                            nextNodes.length;


                        const angle =
                            (
                                index /
                                Math.max(
                                    nextNodes.length +
                                    1,
                                    1
                                )
                            ) *
                            Math.PI *
                            2;


                        const newNode:
                            GraphFlowNode = {

                            id:
                                `expanded-${Date.now()}-${index}`,

                            type:
                                "default",

                            position: {

                                x:
                                    400 +
                                    420 *
                                    Math.cos(
                                        angle
                                    ),

                                y:
                                    250 +
                                    420 *
                                    Math.sin(
                                        angle
                                    ),
                            },

                            data: {

                                label,

                                entityType:
                                    entityType ||
                                    "Entity",
                            },

                            style:
                                getNodeStyle(
                                    entityType ||
                                    "Entity"
                                ),
                        };


                        nextNodes.push(
                            newNode
                        );

                        return newNode;
                    };


                // ---------------------------------
                // Process Expansion Results
                // ---------------------------------

                results.forEach(
                    (result: any) => {

                        const pathNodes =
                            Array.isArray(
                                result.path_nodes
                            )
                                ? result.path_nodes
                                : [];


                        const pathRelations =
                            Array.isArray(
                                result.path_relationships
                            )
                                ? result.path_relationships
                                : [];


                        if (
                            pathNodes.length === 0
                        ) {
                            return;
                        }


                        const sourceName =
                            String(
                                result.source_name ||
                                pathNodes[0] ||
                                ""
                            );

                        let previousNode =
                            findNodeByLabel(
                                sourceName
                            ) ||
                            selectedNode;


                        // ---------------------------------
                        // Path Nodes
                        // ---------------------------------

                        pathNodes.forEach(
                            (
                                pathNodeName:unknown,
                                index: number
                            ) => {

                                const name =
                                    String(
                                        pathNodeName
                                    );


                                if (
                                    index === 0
                                ) {
                                    return;
                                }


                                const entityType =
                                    index ===
                                        pathNodes.length - 1
                                        ? getEntityType(
                                            result.target_type
                                        )
                                        : "Entity";


                                const currentNode =
                                    createNode(
                                        name,
                                        entityType
                                    );


                                const relationship =
                                    String(
                                        pathRelations[
                                            index - 1
                                        ] ||
                                        "RELATED_TO"
                                    );


                                if (
                                    previousNode &&
                                    currentNode
                                ) {

                                    const edgeExists =
                                        nextEdges.some(
                                            (
                                                edge
                                            ) =>
                                                edge.source ===
                                                    String(
                                                        previousNode.id
                                                    ) &&
                                                edge.target ===
                                                    String(
                                                        currentNode.id
                                                    ) &&
                                                String(
                                                    edge.label
                                                ) ===
                                                    relationship
                                        );


                                    if (
                                        !edgeExists
                                    ) {

                                        nextEdges.push({

                                            id:
                                                `expanded-edge-${Date.now()}-${Math.random()}`,

                                            source:
                                                String(
                                                    previousNode.id
                                                ),

                                            target:
                                                String(
                                                    currentNode.id
                                                ),

                                            label:
                                                relationship,

                                            type:
                                                "default",

                                            style: {

                                                stroke:
                                                    "#64748b",

                                                strokeWidth:
                                                    1.5,
                                            },

                                            labelStyle: {

                                                fill:
                                                    "#475569",

                                                fontSize:
                                                    11,

                                                fontWeight:
                                                    500,
                                            },

                                            labelBgStyle: {

                                                fill:
                                                    "#ffffff",

                                                fillOpacity:
                                                    0.9,
                                            },
                                        });
                                    }
                                }


                                previousNode =
                                    currentNode;
                            }
                        );
                    }
                );


                setNodes(
                    nextNodes
                );

                setEdges(
                    nextEdges
                );

            } catch (err: any) {

                console.error(
                    "Failed to expand entity:",
                    err
                );

                setError(
                    err?.response?.data?.detail ||
                    err?.message ||
                    "Failed to expand entity."
                );

            } finally {

                setExpanding(
                    false
                );
            }
        };


    // =================================================
    // Selected Node Relationships
    // =================================================

    const selectedNodeRelationships =
        useMemo(() => {

            if (
                !selectedNode
            ) {
                return [];
            }


            const selectedId =
                String(
                    selectedNode.id
                );


            return edges.filter(
                (edge) =>
                    String(
                        edge.source
                    ) ===
                        selectedId ||
                    String(
                        edge.target
                    ) ===
                        selectedId
            );

        }, [
            edges,
            selectedNode,
        ]);


    // =================================================
    // Selected Edge Source / Target
    // =================================================

    const selectedEdgeSource =
        useMemo(() => {

            if (
                !selectedEdge
            ) {
                return null;
            }

            return nodes.find(
                (node) =>
                    String(
                        node.id
                    ) ===
                    String(
                        selectedEdge.source
                    )
            ) || null;

        }, [
            nodes,
            selectedEdge,
        ]);


    const selectedEdgeTarget =
        useMemo(() => {

            if (
                !selectedEdge
            ) {
                return null;
            }

            return nodes.find(
                (node) =>
                    String(
                        node.id
                    ) ===
                    String(
                        selectedEdge.target
                    )
            ) || null;

        }, [
            nodes,
            selectedEdge,
        ]);


    // =================================================
    // Clear Search / Filter
    // =================================================

    const clearFilters = () => {

        setSearchTerm("");

        setEntityTypeFilter(
            "all"
        );
    };


    // =================================================
    // Render
    // =================================================

    return (

        <div className="flex min-h-screen w-full flex-col bg-slate-50">

            {/* =========================================
                Header
            ========================================== */}

            <div className="border-b bg-white px-6 py-4">

                <div className="flex flex-wrap items-center justify-between gap-4">

                    {/* ---------------------------------
                        Title
                    --------------------------------- */}

                    <div>

                        <h1 className="text-xl font-semibold text-slate-900">
                            Knowledge Graph
                        </h1>

                        <p className="mt-1 text-sm text-slate-500">
                            Explore projects, technologies,
                            databases, documents and
                            relationships.
                        </p>

                    </div>


                    {/* ---------------------------------
                        Controls
                    --------------------------------- */}

                    <div className="flex flex-wrap items-center gap-2">

                        {/* Project */}

                        <select
                            value={
                                selectedProject
                            }
                            onChange={(event) =>
                                setSelectedProject(
                                    event.target.value
                                )
                            }
                            disabled={
                                loadingProjects ||
                                projects.length === 0
                            }
                            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none focus:border-slate-500 disabled:bg-slate-100"
                        >

                            {projects.length === 0 ? (

                                <option value="">
                                    No projects
                                </option>

                            ) : (

                                projects.map(
                                    (project) => (

                                        <option
                                            key={
                                                project.name
                                            }
                                            value={
                                                project.name
                                            }
                                        >
                                            {
                                                project.name
                                            }
                                        </option>

                                    )
                                )
                            )}

                        </select>


                        {/* Search */}

                        <input
                            id="graph-search"
                            type="text"
                            value={
                                searchTerm
                            }
                            onChange={(event) =>
                                setSearchTerm(
                                    event.target.value
                                )
                            }
                            placeholder="Search nodes..."
                            className="h-10 w-56 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none placeholder:text-slate-400 focus:border-slate-500"
                        />


                        {/* Entity Type */}

                        <select
                            id="entity-type-filter"
                            value={
                                entityTypeFilter
                            }
                            onChange={(event) =>
                                setEntityTypeFilter(
                                    event.target.value
                                )
                            }
                            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none focus:border-slate-500"
                        >

                            <option value="all">
                                All Types
                            </option>

                            {entityTypes.map(
                                (type) => (

                                    <option
                                        key={type}
                                        value={type}
                                    >
                                        {type}
                                    </option>

                                )
                            )}

                        </select>


                        {/* Clear */}

                        <button
                            type="button"
                            onClick={
                                clearFilters
                            }
                            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                        >
                            Clear
                        </button>


                        {/* Expansion Hop */}

                        <select
                            value={
                                expansionHops
                            }
                            onChange={(event) =>
                                setExpansionHops(
                                    Number(
                                        event.target.value
                                    )
                                )
                            }
                            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none focus:border-slate-500"
                        >

                            <option value={1}>
                                1 Hop
                            </option>

                            <option value={2}>
                                2 Hops
                            </option>

                        </select>


                        {/* Expand */}

                        <button
                            type="button"
                            onClick={
                                handleExpandEntity
                            }
                            disabled={
                                !selectedNode ||
                                expanding
                            }
                            className="h-10 rounded-md bg-slate-900 px-4 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {expanding
                                ? "Expanding..."
                                : "Expand"}
                        </button>

                    </div>

                </div>


                {/* -------------------------------------
                    Stats
                -------------------------------------- */}

                <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-slate-500">

                    <div>
                        Showing{" "}
                        <span className="font-medium text-slate-700">
                            {
                                filteredNodes.length
                            }
                        </span>{" "}
                        nodes
                    </div>

                    <div>
                        <span className="font-medium text-slate-700">
                            {
                                filteredEdges.length
                            }
                        </span>{" "}
                        relationships
                    </div>


                    {(filteredNodes.length !==
                        nodes.length ||
                        filteredEdges.length !==
                            edges.length) && (

                        <div className="text-slate-400">

                            {nodes.length} total nodes ·{" "}
                            {edges.length} total relationships

                        </div>
                    )}

                </div>

                <div className="mt-2 text-xs text-slate-400">
                    Click a node to inspect it. Click a relationship to inspect the connection.
                </div>

            </div>


            {/* =========================================
                Error
            ========================================== */}

            {error && (

                <div className="mx-6 mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">

                    {error}

                </div>

            )}


            {/* =========================================
                Main Content
            ========================================== */}

            <div className="relative flex-1">

                {/* -------------------------------------
                    Loading Projects
                -------------------------------------- */}

                {loadingProjects && (

                    <div className="flex h-[600px] items-center justify-center">

                        <div className="text-sm text-slate-500">
                            Loading projects...
                        </div>

                    </div>

                )}


                {/* -------------------------------------
                    Loading Graph
                -------------------------------------- */}

                {!loadingProjects &&
                    loadingGraph && (

                        <div className="flex h-[600px] items-center justify-center">

                            <div className="text-sm text-slate-500">
                                Loading knowledge graph...
                            </div>

                        </div>

                    )}


                {/* -------------------------------------
                    Empty Graph
                -------------------------------------- */}

                {!loadingProjects &&
                    !loadingGraph &&
                    nodes.length === 0 && (

                        <div className="flex h-[600px] items-center justify-center">

                            <div className="text-center">

                                <h2 className="text-lg font-medium text-slate-800">
                                    No graph data
                                </h2>

                                <p className="mt-1 text-sm text-slate-500">
                                    No knowledge graph data is available
                                    for this project.
                                </p>

                            </div>

                        </div>

                    )}


                {/* -------------------------------------
                    No Matching Nodes
                -------------------------------------- */}

                {!loadingProjects &&
                    !loadingGraph &&
                    nodes.length > 0 &&
                    filteredNodes.length === 0 && (

                        <div className="flex h-[600px] items-center justify-center">

                            <div className="text-center">

                                <h2 className="text-lg font-medium text-slate-800">
                                    No matching nodes
                                </h2>

                                <p className="mt-1 text-sm text-slate-500">
                                    Try changing the search text
                                    or entity type filter.
                                </p>

                                <button
                                    type="button"
                                    onClick={
                                        clearFilters
                                    }
                                    className="mt-4 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
                                >
                                    Clear filters
                                </button>

                            </div>

                        </div>

                    )}


                {/* -------------------------------------
                    React Flow
                -------------------------------------- */}

                {!loadingProjects &&
                    !loadingGraph &&
                    filteredNodes.length > 0 && (

                        <div
                            className="relative"
                            style={{
                                minHeight:
                                    "600px",
                            }}
                        >

                            <div
                                className="overflow-hidden rounded-lg border border-slate-200 bg-white"
                                style={{
                                    width: "100%",
                                    height: "600px",
                                }}
                            >

                                <ReactFlow<
                                    GraphFlowNode,
                                    Edge
                                >

                                    nodes={
                                        filteredNodes
                                    }

                                    edges={
                                        filteredEdges
                                    }

                                    onNodeClick={
                                        handleNodeClick
                                    }

                                    onEdgeClick={
                                        handleEdgeClick
                                    }

                                    fitView

                                    fitViewOptions={{
                                        padding:
                                            0.25,
                                    }}

                                    nodesDraggable={
                                        true
                                    }

                                    nodesConnectable={
                                        false
                                    }

                                    elementsSelectable={
                                        true
                                    }

                                    panOnDrag={
                                        true
                                    }

                                    zoomOnScroll={
                                        true
                                    }

                                    minZoom={
                                        0.2
                                    }

                                    maxZoom={
                                        2
                                    }

                                    style={{
                                        width:
                                            "100%",

                                        height:
                                            "100%",
                                    }}
                                >

                                    <Background />

                                    <Controls />

                                    <MiniMap
                                        nodeColor={
                                            miniMapNodeColor
                                        }
                                    />

                                    <Panel
                                        position="bottom-left"
                                    >
                                        <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 shadow-sm">

                                            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                                Legend
                                            </p>

                                            <div className="space-y-2 text-xs">

                                                <div className="flex items-center gap-2">
                                                    <span className="h-3 w-3 rounded bg-slate-900" />
                                                    <span className="text-slate-600">
                                                        Project
                                                    </span>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <span className="h-3 w-3 rounded bg-blue-200 border border-blue-300" />
                                                    <span className="text-slate-600">
                                                        Technology
                                                    </span>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <span className="h-3 w-3 rounded bg-green-200 border border-green-300" />
                                                    <span className="text-slate-600">
                                                        Database
                                                    </span>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <span className="h-3 w-3 rounded bg-amber-200 border border-amber-300" />
                                                    <span className="text-slate-600">
                                                        Document
                                                    </span>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <span className="h-3 w-3 rounded bg-slate-100 border border-slate-300" />
                                                    <span className="text-slate-600">
                                                        Other entity
                                                    </span>
                                                </div>

                                            </div>

                                        </div>
                                    </Panel>


                                    {/* ---------------------------------
                                        Graph Stats Panel
                                    ---------------------------------- */}

                                    <Panel
                                        position="top-left"
                                    >
                                        <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 shadow-sm">

                                            <div className="flex items-center gap-2">

                                                <span className="h-2.5 w-2.5 rounded-full bg-green-500" />

                                                <span className="text-sm font-semibold text-slate-800">
                                                    {selectedProject || "Knowledge Graph"}
                                                </span>

                                            </div>

                                            <div className="mt-2 flex items-center gap-3 text-xs text-slate-500">

                                                <span>
                                                    {filteredNodes.length} nodes
                                                </span>

                                                <span>
                                                    {filteredEdges.length} relationships
                                                </span>

                                            </div>

                                        </div>
                                    </Panel>

                                </ReactFlow>

                            </div>


                            {/* =================================
                                Right Details Panel
                            ================================== */}

                            {(selectedNode ||
                                selectedEdge) && (

                                <div className="absolute right-4 top-4 z-10 w-80 max-w-[calc(100vw-2rem)] rounded-xl border border-slate-200 bg-white shadow-lg">

                                    {/* ---------------------------
                                        Node Details
                                    ---------------------------- */}

                                    {selectedNode && (

                                        <div className="p-4">

                                            <div className="flex items-start justify-between gap-3">

                                                <div>

                                                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                                        Node
                                                    </p>

                                                    <h3 className="mt-1 break-words text-base font-semibold text-slate-900">
                                                        {
                                                            String(
                                                                selectedNode.data
                                                                    ?.label ||
                                                                "Unknown"
                                                            )
                                                        }
                                                    </h3>

                                                </div>


                                                <button
                                                    type="button"
                                                    onClick={() => {

                                                        setSelectedNode(
                                                            null
                                                        );

                                                        setSelectedEntityId(
                                                            null
                                                        );
                                                    }}
                                                    className="text-sm text-slate-400 hover:text-slate-700"
                                                >
                                                    ✕
                                                </button>

                                            </div>


                                            <div className="mt-4 space-y-3">

                                                <div>

                                                    <p className="text-xs font-medium text-slate-400">
                                                        Entity Type
                                                    </p>

                                                    <p className="mt-1 text-sm text-slate-700">
                                                        {
                                                            String(
                                                                selectedNode.data
                                                                    ?.entityType ||
                                                                "Unknown"
                                                            )
                                                        }
                                                    </p>

                                                </div>


                                                <div>

                                                    <p className="text-xs font-medium text-slate-400">
                                                        Node ID
                                                    </p>

                                                    <p
                                                        title={String(selectedNode.id)}
                                                        className="mt-1 truncate text-sm text-slate-700"
                                                    >
                                                        {String(selectedNode.id)}
                                                    </p>

                                                </div>


                                                <div>

                                                    <p className="text-xs font-medium text-slate-400">
                                                        Relationships
                                                    </p>

                                                    <p className="mt-1 text-sm text-slate-700">
                                                        {
                                                            selectedNodeRelationships.length
                                                        }
                                                    </p>

                                                </div>

                                            </div>


                                            {/* Relationship List */}

                                            {selectedNodeRelationships.length >
                                                0 && (

                                                <div className="mt-5 border-t pt-4">

                                                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                                                        Connected relationships
                                                    </p>

                                                    <div className="max-h-52 space-y-2 overflow-y-auto">

                                                        {selectedNodeRelationships.map(
                                                            (
                                                                edge
                                                            ) => {

                                                                const isSource =
                                                                    String(
                                                                        edge.source
                                                                    ) ===
                                                                    String(
                                                                        selectedNode.id
                                                                    );

                                                                const otherNode =
                                                                    nodes.find(
                                                                        (
                                                                            node
                                                                        ) =>
                                                                            String(
                                                                                node.id
                                                                            ) ===
                                                                            String(
                                                                                isSource
                                                                                    ? edge.target
                                                                                    : edge.source
                                                                            )
                                                                    );


                                                                return (

                                                                    <button
                                                                        key={
                                                                            edge.id
                                                                        }
                                                                        type="button"
                                                                        onClick={() =>
                                                                            handleEdgeClick(
                                                                                {} as MouseEvent,
                                                                                edge
                                                                            )
                                                                        }
                                                                        className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-left transition hover:bg-slate-100"
                                                                    >

                                                                        <p className="text-xs font-medium text-slate-700">

                                                                            {
                                                                                String(
                                                                                    edge.label ||
                                                                                    edge.data?.relationship ||
                                                                                    "RELATED_TO"
                                                                                )
                                                                            }

                                                                        </p>

                                                                        <p className="mt-1 truncate text-xs text-slate-500">

                                                                            {isSource
                                                                                ? "→ "
                                                                                : "← "}

                                                                            {
                                                                                String(
                                                                                    otherNode?.data
                                                                                        ?.label ||
                                                                                    "Unknown"
                                                                                )
                                                                            }

                                                                        </p>

                                                                    </button>

                                                                );
                                                            }
                                                        )}

                                                    </div>

                                                </div>

                                            )}

                                        </div>

                                    )}


                                    {/* ---------------------------
                                        Edge Details
                                    ---------------------------- */}

                                    {selectedEdge && (

                                        <div className="p-4">

                                            <div className="flex items-start justify-between gap-3">

                                                <div>

                                                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                                        Relationship
                                                    </p>

                                                    <h3 className="mt-1 text-base font-semibold text-slate-900">
                                                        {
                                                            String(
                                                                selectedEdge.label ||
                                                                selectedEdge.data?.relationship ||
                                                                "RELATED_TO"
                                                            )
                                                        }
                                                    </h3>

                                                </div>


                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        setSelectedEdge(
                                                            null
                                                        )
                                                    }
                                                    className="text-sm text-slate-400 hover:text-slate-700"
                                                >
                                                    ✕
                                                </button>

                                            </div>


                                            <div className="mt-4 space-y-3">

                                                <div>

                                                    <p className="text-xs font-medium text-slate-400">
                                                        Source
                                                    </p>

                                                    <p className="mt-1 break-words text-sm text-slate-700">
                                                        {
                                                            String(
                                                                selectedEdgeSource?.data
                                                                    ?.label ||
                                                                selectedEdge.source
                                                            )
                                                        }
                                                    </p>

                                                </div>


                                                <div>

                                                    <p className="text-xs font-medium text-slate-400">
                                                        Target
                                                    </p>

                                                    <p className="mt-1 break-words text-sm text-slate-700">
                                                        {
                                                            String(
                                                                selectedEdgeTarget?.data
                                                                    ?.label ||
                                                                selectedEdge.target
                                                            )
                                                        }
                                                    </p>

                                                </div>


                                                <div>

                                                    <p className="text-xs font-medium text-slate-400">
                                                        Edge ID
                                                    </p>

                                                    <p className="mt-1 break-all text-sm text-slate-700">
                                                        {
                                                            String(
                                                                selectedEdge.id
                                                            )
                                                        }
                                                    </p>

                                                </div>

                                            </div>

                                        </div>

                                    )}

                                </div>

                            )}

                        </div>

                    )}

            </div>

        </div>
    );
}


// =====================================================
// Helper Functions
// =====================================================

function getEntityType(
    value: unknown
): string {

    if (
        Array.isArray(value)
    ) {

        if (
            value.length > 0
        ) {

            return String(
                value[
                    value.length - 1
                ]
            );
        }

        return "Entity";
    }


    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return "Entity";
    }


    return String(
        value
    );
}


// =====================================================
// Node Styling
// =====================================================

function getNodeStyle(
    entityType: string
) {

    const type =
        String(
            entityType ||
            "Entity"
        ).toLowerCase();


    if (
        type === "project"
    ) {

        return {

            background:
                "#0f172a",

            color:
                "#ffffff",

            border:
                "1px solid #0f172a",

            borderRadius:
                "12px",

            padding:
                "12px 18px",

            fontWeight:
                600,

            minWidth:
                "180px",

            textAlign:
                "center" as const,
        };
    }


    if (
        type === "technology"
    ) {

        return {

            background:
                "#dbeafe",

            color:
                "#1e3a8a",

            border:
                "1px solid #93c5fd",

            borderRadius:
                "10px",

            padding:
                "10px 14px",

            fontWeight:
                500,
        };
    }


    if (
        type === "database"
    ) {

        return {

            background:
                "#dcfce7",

            color:
                "#166534",

            border:
                "1px solid #86efac",

            borderRadius:
                "10px",

            padding:
                "10px 14px",

            fontWeight:
                500,
        };
    }


    if (
        type === "document"
    ) {

        return {

            background:
                "#fef3c7",

            color:
                "#92400e",

            border:
                "1px solid #fcd34d",

            borderRadius:
                "10px",

            padding:
                "10px 14px",

            fontWeight:
                500,
        };
    }


    return {

        background:
            "#f8fafc",

        color:
            "#334155",

        border:
            "1px solid #cbd5e1",

        borderRadius:
            "10px",

        padding:
            "10px 14px",

        fontWeight:
            500,
    };
}


// =====================================================
// MiniMap Colors
// =====================================================

function miniMapNodeColor(
    node: GraphFlowNode
): string {

    const type =
        String(
            node.data?.entityType ||
            ""
        ).toLowerCase();


    if (
        type === "project"
    ) {
        return "#0f172a";
    }


    if (
        type === "technology"
    ) {
        return "#3b82f6";
    }


    if (
        type === "database"
    ) {
        return "#22c55e";
    }


    if (
        type === "document"
    ) {
        return "#f59e0b";
    }


    return "#64748b";
}