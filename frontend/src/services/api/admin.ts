import api from "../axios";

export interface AdminUser {
    id: number;
    organization_id: number;
    department_id: number | null;
    name: string;
    email: string;
    role: string;
    approval_status: string;
    is_active: boolean;
}

export interface Department { id: number; organization_id: number; name: string; description: string | null; }
export interface AdminProject { id: number; organization_id: number; name: string; slug: string; description: string | null; status: string; }
export interface Organization { id: number; name: string; slug: string; description: string | null; }

export const getUsers = async () => (await api.get<AdminUser[]>("/users")).data;
export const getPendingUsers = async () => (await api.get<AdminUser[]>("/users/pending")).data;
export const approveUser = async (id: number) => (await api.patch<AdminUser>(`/users/${id}/approve`)).data;
export const rejectUser = async (id: number) => (await api.patch<AdminUser>(`/users/${id}/reject`)).data;
export const deactivateUser = async (id: number) => (await api.patch<AdminUser>(`/users/${id}/deactivate`)).data;
export const assignDepartment = async (id: number, department_id: number | null) => (await api.patch<AdminUser>(`/users/${id}/department`, { department_id })).data;
export const getDepartments = async () => (await api.get<Department[]>("/departments")).data;
export const createDepartment = async (payload: { name: string; description?: string }) => (await api.post<Department>("/departments", payload)).data;
export const getProjectsAdmin = async () => (await api.get<AdminProject[]>("/projects")).data;
export const createProjectAdmin = async (payload: { name: string; slug: string; description?: string }) => (await api.post<AdminProject>("/projects", payload)).data;
export const archiveProjectAdmin = async (projectId: number) => (await api.patch<AdminProject>(`/projects/${projectId}/archive`)).data;
export const getProjectMembers = async (projectId: number) => (await api.get(`/projects/${projectId}/members`)).data;
export const assignProjectMember = async (projectId: number, userId: number, permission = "PROJECT_MEMBER") => (await api.post(`/projects/${projectId}/members`, { user_id: userId, permission })).data;
export const removeProjectMember = async (projectId: number, userId: number) => api.delete(`/projects/${projectId}/members/${userId}`);
export const getOrganizationAdmin = async (organizationId: number) => (await api.get<Organization>(`/organizations/${organizationId}`)).data;
export const updateOrganizationAdmin = async (organizationId: number, payload: { name: string; description?: string }) => (await api.patch<Organization>(`/organizations/${organizationId}`, payload)).data;
