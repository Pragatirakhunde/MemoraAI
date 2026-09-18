import api from "../axios";


export interface LoginRequest {
    email: string;
    password: string;
}


export interface TokenResponse {
    access_token: string;
    token_type: string;
}


export interface CurrentUser {
    id: number;
    name: string;
    email: string;
    role: string;
    organization_id: number;
}


export const loginUser = async (
    data: LoginRequest
): Promise<TokenResponse> => {

    const response =
        await api.post<TokenResponse>(
            "/auth/login",
            data
        );

    return response.data;
};


export const getCurrentUser = async (): Promise<CurrentUser> => {

    const response =
        await api.get<CurrentUser>(
            "/auth/me"
        );

    return response.data;
};

export interface RegisterRequest {
    name: string;
    email: string;
    password: string;
}

export const registerUser = async (
    data: RegisterRequest
): Promise<CurrentUser> => {

    const response =
        await api.post<CurrentUser>(
            "/auth/register",
            data
        );

    return response.data;
};