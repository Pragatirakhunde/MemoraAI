import { Bell, ChevronDown, LogOut, UserCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";


export default function Header() {

    const {
        user,
        logout,
    } = useAuth();

    const navigate = useNavigate();


    const handleLogout = () => {

        logout();

        navigate(
            "/login",
            { replace: true }
        );
    };


    return (
        <header className="flex h-16 items-center justify-between border-b bg-white px-6">

            {/* ---------------------------------------------
                Left
            ---------------------------------------------- */}

            <div>
                <h1 className="text-lg font-semibold text-slate-900">
                    Enterprise Memory Engine
                </h1>
            </div>


            {/* ---------------------------------------------
                Right
            ---------------------------------------------- */}

            <div className="flex items-center gap-4">

                {/* Search */}

                <div className="hidden md:block">

                    <input
                        type="text"
                        placeholder="Search..."
                        className="w-56 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
                    />

                </div>


                {/* Notifications */}

                <button
                    type="button"
                    className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800"
                >
                    <Bell size={20} />
                </button>


                {/* User */}

                <div className="group relative">

                    <button
                        type="button"
                        className="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-slate-100"
                    >

                        <UserCircle
                            size={30}
                            className="text-slate-600"
                        />

                        <div className="hidden text-left sm:block">

                            <p className="max-w-32 truncate text-sm font-medium text-slate-800">
                                {user?.name || "User"}
                            </p>

                            <p className="max-w-32 truncate text-xs text-slate-500">
                                {user?.role || "Employee"}
                            </p>

                        </div>

                        <ChevronDown
                            size={16}
                            className="text-slate-400"
                        />

                    </button>


                    {/* Dropdown */}

                    <div className="invisible absolute right-0 top-full z-50 mt-2 w-56 translate-y-1 rounded-xl border bg-white p-2 opacity-0 shadow-lg transition-all group-hover:visible group-hover:translate-y-0 group-hover:opacity-100">

                        <div className="border-b px-3 py-2">

                            <p className="truncate text-sm font-medium text-slate-800">
                                {user?.name || "User"}
                            </p>

                            <p className="truncate text-xs text-slate-500">
                                {user?.email || ""}
                            </p>

                        </div>


                        <button
                            type="button"
                            onClick={handleLogout}
                            className="mt-2 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                        >

                            <LogOut size={17} />

                            Logout

                        </button>

                    </div>

                </div>

            </div>

        </header>
    );
}