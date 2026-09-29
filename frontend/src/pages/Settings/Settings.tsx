import { useState } from "react";
import { LogOut, ShieldCheck, UserRound } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Settings() {
    const { user, logout } = useAuth();
    const [message, setMessage] = useState("");

    const handleLogout = () => {
        logout();
        setMessage("Logged out successfully.");
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
                <p className="mt-1 text-sm text-slate-500">Review your Memora account and security details.</p>
            </div>

            {message && <div className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">{message}</div>}

            <div className="grid gap-5 md:grid-cols-2">
                <section className="rounded-xl border bg-white p-6 shadow-sm">
                    <div className="flex items-center gap-3">
                        <UserRound size={22} className="text-slate-600" />
                        <h2 className="text-lg font-semibold">Account</h2>
                    </div>
                    <div className="mt-5 space-y-3 text-sm">
                        <Info label="Name" value={user?.name || "-"} />
                        <Info label="Email" value={user?.email || "-"} />
                        <Info label="Role" value={user?.role || "-"} />
                        <Info label="Organization ID" value={String(user?.organization_id ?? "-")} />
                        <Info label="Department ID" value={String(user?.department_id ?? "Not assigned")} />
                    </div>
                </section>

                <section className="rounded-xl border bg-white p-6 shadow-sm">
                    <div className="flex items-center gap-3">
                        <ShieldCheck size={22} className="text-slate-600" />
                        <h2 className="text-lg font-semibold">Access & security</h2>
                    </div>
                    <div className="mt-5 space-y-3 text-sm">
                        <Info label="Approval status" value={user?.approval_status || "-"} />
                        <Info label="Account status" value={user?.is_active ? "Active" : "Inactive"} />
                        <p className="text-slate-500">Project and CodeMind access is controlled by server-side organization and project authorization.</p>
                    </div>
                    <button onClick={handleLogout} className="mt-6 inline-flex items-center gap-2 rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50">
                        <LogOut size={16} /> Log out
                    </button>
                </section>
            </div>
        </div>
    );
}

function Info({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between gap-4 border-b pb-2 last:border-0">
            <span className="text-slate-500">{label}</span>
            <span className="font-medium text-slate-800">{value}</span>
        </div>
    );
}
