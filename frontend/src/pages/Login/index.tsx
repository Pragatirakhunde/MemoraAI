import { useState } from "react";
import type { FormEvent } from "react";

import { Navigate, useNavigate , Link } from "react-router-dom";

import {
    Bot,
    Loader2,
    Lock,
    Mail,
} from "lucide-react";

import { useAuth } from "../../context/AuthContext";


export default function Login() {

    const {
        login,
        isAuthenticated,
    } = useAuth();

    const navigate = useNavigate();

    const [email, setEmail] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");


    if (isAuthenticated) {
        return (
            <Navigate
                to="/dashboard"
                replace
            />
        );
    }


    const handleSubmit = async (
        event: FormEvent
    ) => {

        event.preventDefault();

        setError("");
        setLoading(true);

        try {

            await login(
                email,
                password
            );

            navigate(
                "/dashboard",
                { replace: true }
            );

        } catch (err: any) {

            setError(
                err?.response?.data?.detail ||
                "Invalid email or password."
            );

        } finally {
            setLoading(false);
        }
    };


    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">

            <div className="w-full max-w-md">

                <div className="rounded-2xl border bg-white p-8 shadow-sm">

                    <div className="mb-8 text-center">

                        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-900">

                            <Bot
                                className="text-white"
                                size={24}
                            />

                        </div>

                        <h1 className="text-2xl font-semibold text-slate-900">
                            Enterprise Memory Engine
                        </h1>

                        <p className="mt-2 text-sm text-slate-500">
                            Sign in to access organizational knowledge
                        </p>

                    </div>


                    <form
                        onSubmit={handleSubmit}
                        className="space-y-5"
                    >

                        <div>

                            <label className="mb-2 block text-sm font-medium text-slate-700">
                                Email
                            </label>

                            <div className="relative">

                                <Mail
                                    size={18}
                                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                                />

                                <input
                                    type="email"
                                    value={email}
                                    onChange={(event) =>
                                        setEmail(
                                            event.target.value
                                        )
                                    }
                                    required
                                    placeholder="admin@technova.com"
                                    className="w-full rounded-lg border border-slate-300 py-3 pl-10 pr-3 text-sm outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
                                />

                            </div>

                        </div>


                        <div>

                            <label className="mb-2 block text-sm font-medium text-slate-700">
                                Password
                            </label>

                            <div className="relative">

                                <Lock
                                    size={18}
                                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                                />

                                <input
                                    type="password"
                                    value={password}
                                    onChange={(event) =>
                                        setPassword(
                                            event.target.value
                                        )
                                    }
                                    required
                                    placeholder="Enter your password"
                                    className="w-full rounded-lg border border-slate-300 py-3 pl-10 pr-3 text-sm outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
                                />

                            </div>

                        </div>


                        {error && (
                            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                                {error}
                            </div>
                        )}


                        <button
                            type="submit"
                            disabled={loading}
                            className="flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 py-3 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                        >

                            {loading && (
                                <Loader2
                                    size={18}
                                    className="animate-spin"
                                />
                            )}

                            {loading
                                ? "Signing in..."
                                : "Sign in"}

                        </button>

                        <div className="mt-6 text-center text-sm text-slate-500">
                            Don't have an account?{" "}

                            <Link
                                to="/register"
                                className="font-medium text-slate-900 hover:underline"
                            >
                                Create account
                            </Link>
                        </div>

                    </form>

                </div>

            </div>

        </div>
    );
}