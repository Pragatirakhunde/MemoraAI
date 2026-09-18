import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import {
    getCurrentUser,
    loginUser,
} from "../services/api/auth";


export interface User {
    id: number;
    name: string;
    email: string;
    role: string;
    organization_id: number;
}


interface AuthContextType {
    user: User | null;
    token: string | null;
    loading: boolean;

    login: (
        email: string,
        password: string
    ) => Promise<void>;

    logout: () => void;

    isAuthenticated: boolean;
}


const AuthContext = createContext<
    AuthContextType | undefined
>(undefined);


export function AuthProvider({
    children,
}: {
    children: React.ReactNode;
}) {
    const [user, setUser] = useState<User | null>(null);

    const [token, setToken] = useState<string | null>(
        localStorage.getItem("access_token")
    );

    const [loading, setLoading] = useState(true);


    useEffect(() => {
        const loadUser = async () => {
            const storedToken =
                localStorage.getItem("access_token");

            if (!storedToken) {
                setLoading(false);
                return;
            }

            try {
                const currentUser =
                    await getCurrentUser();

                setUser(currentUser);
            } catch {
                localStorage.removeItem(
                    "access_token"
                );

                setToken(null);
                setUser(null);
            } finally {
                setLoading(false);
            }
        };

        loadUser();
    }, []);


    const login = async (
        email: string,
        password: string
    ) => {
        const response = await loginUser({
            email,
            password,
        });

        localStorage.setItem(
            "access_token",
            response.access_token
        );

        setToken(response.access_token);

        const currentUser =
            await getCurrentUser();

        setUser(currentUser);
    };


    const logout = () => {
        localStorage.removeItem(
            "access_token"
        );

        setToken(null);
        setUser(null);
    };


    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                loading,
                login,
                logout,
                isAuthenticated:
                    !!token && !!user,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}


export function useAuth() {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error(
            "useAuth must be used inside AuthProvider"
        );
    }

    return context;
}