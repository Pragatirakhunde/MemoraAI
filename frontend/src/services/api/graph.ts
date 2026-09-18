import api from "../axios";


export interface GraphNode {
    id: string;
    label: string;
    type: string;
}


export interface GraphEdge {
    source: string;
    target: string;
    relationship: string;
}


export interface GraphData {
    nodes: GraphNode[];
    edges: GraphEdge[];
}


export interface GraphProject {
    name: string;
    key?: string;
    confidence?: number;
}


export interface ProjectGraphResponse {
    nodes: GraphNode[];
    edges: GraphEdge[];
}


// -------------------------------------------------
// Get projects
// -------------------------------------------------

export const getGraphProjects = async (): Promise<GraphProject[]> => {

    const response = await api.get(
        "/graph/projects"
    );

    console.log(
        "RAW GRAPH PROJECT API RESPONSE:",
        response.data
    );

    const body = response.data;

    // Supports:
    // { projects: [...] }
    // [...]
    // { data: { projects: [...] } }
    // { success: true, data: { projects: [...] } }

    if (Array.isArray(body)) {
        return body;
    }

    if (Array.isArray(body?.projects)) {
        return body.projects;
    }

    if (Array.isArray(body?.data?.projects)) {
        return body.data.projects;
    }

    console.error(
        "Unexpected graph projects response:",
        body
    );

    return [];
};


// -------------------------------------------------
// Get selected project graph
// -------------------------------------------------

export const getProjectGraph = async (
    projectName: string
): Promise<ProjectGraphResponse> => {

    const response = await api.get(
        `/graph/project/${encodeURIComponent(projectName)}/graph`
    );

    console.log(
        "RAW PROJECT GRAPH RESPONSE:",
        response.data
    );

    const body = response.data;

    if (
        body &&
        Array.isArray(body.nodes) &&
        Array.isArray(body.edges)
    ) {
        return body;
    }

    if (
        body?.data &&
        Array.isArray(body.data.nodes) &&
        Array.isArray(body.data.edges)
    ) {
        return body.data;
    }

    return {
        nodes: [],
        edges: [],
    };
};


// -------------------------------------------------
// Entity neighborhood
// -------------------------------------------------

export const getEntityNeighborhood = async (
    entityName: string
) => {

    const response = await api.get(
        `/graph/entity/${encodeURIComponent(entityName)}`
    );

    return response.data;
};


// -------------------------------------------------
// Entity expansion
// -------------------------------------------------

export const expandEntity = async (
    entityName: string,
    maxHops: number = 2,
    limit: number = 20
) => {

    const response = await api.get(
        `/graph/entity/${encodeURIComponent(entityName)}/expand`,
        {
            params: {
                max_hops: maxHops,
                limit,
            },
        }
    );

    const body = response.data;

    console.log(
        "RAW ENTITY EXPANSION RESPONSE:",
        body
    );

    if (Array.isArray(body)) {
        return body;
    }

    if (Array.isArray(body?.results)) {
        return body.results;
    }

    if (Array.isArray(body?.paths)) {
        return body.paths;
    }

    if (Array.isArray(body?.data)) {
        return body.data;
    }

    return [];
};