import api from "../axios";

export interface Project {
    id: number;
    organization_id: number;
    name: string;
    slug: string;
    description: string | null;
    status: "active" | "archived";
    created_at: string;
    updated_at: string;
}

export async function getProjects(): Promise<Project[]> {
    const response = await api.get("/projects");

    return response.data;
}

export async function getMyProjects(): Promise<Project[]> {
    const response = await api.get("/projects/my");
    return response.data;
}
