import {
    LayoutDashboard,
    Building2,
    PlugZap,
    FileText,
    Network,
    Bot,
    Search,
    Settings
} from "lucide-react";

import { NavLink } from "react-router-dom";

const menus = [

    {
        title: "Dashboard",
        icon: LayoutDashboard,
        path: "/dashboard"
    },

    {
        title: "Organization",
        icon: Building2,
        path: "/organization"
    },

    {
        title: "Data Sources",
        icon: PlugZap,
        path: "/connectors"
    },

    {
        title: "Documents",
        icon: FileText,
        path: "/documents"
    },

    {
        title: "Knowledge Graph",
        icon: Network,
        path: "/graph"
    },

    {
        title: "AI Assistant",
        icon: Bot,
        path: "/chat"
    },

    {
        title: "Search",
        icon: Search,
        path: "/search"
    },

    {
        title: "Settings",
        icon: Settings,
        path: "/settings"
    }

];

function Sidebar() {

    return (

        <aside className="w-64 bg-slate-900 text-white">

            <div className="border-b border-slate-700 p-6">

                <h1 className="text-xl font-bold">
                    EME
                </h1>

                <p className="text-sm text-slate-400">
                    Enterprise Memory Engine
                </p>

            </div>

            <nav className="mt-4">

                {
                    menus.map((menu) => {

                        const Icon = menu.icon;

                        return (

                            <NavLink

                                key={menu.path}

                                to={menu.path}

                                className={({ isActive }) =>

                                    `mx-2 mb-2 flex items-center gap-3 rounded-lg px-4 py-3 transition
                                    
                                    ${
                                        isActive
                                        ? "bg-blue-600"
                                        : "hover:bg-slate-800"
                                    }`

                                }

                            >

                                <Icon size={20} />

                                {menu.title}

                            </NavLink>

                        );

                    })
                }

            </nav>

        </aside>

    );

}

export default Sidebar;