import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function RoleRoute({ role }: { role: "admin" | "employee" }) {
    const { user, isAuthenticated, loading } = useAuth();
    if (loading) return <div className="flex min-h-screen items-center justify-center">Loading...</div>;
    if (!isAuthenticated) return <Navigate to="/login" replace />;
    if (user?.role !== role) return <Navigate to="/dashboard" replace />;
    return <Outlet />;
}
