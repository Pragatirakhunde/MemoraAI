import {
    BrowserRouter,
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

import AppLayout from "../layouts/AppLayout";

import Login from "../pages/Login";
import ProtectedRoute from "./ProtectedRoute";

import Dashboard from "../pages/Dashboard/Dashboard";
import Chat from "../pages/Chat";
import Documents from "../pages/Documents/Documents";
import Connectors from "../pages/Connectors/Connectors";
import KnowledgeGraph from "../pages/KnowledgeGraph/KnowledgeGraph";
import Search from "../pages/Search/Search";
import Settings from "../pages/Settings/Settings";
import Organization from "../pages/Organization/Organization";
import Register from "../pages/Register";


function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>

                {/* =========================
                    PUBLIC ROUTES
                ========================== */}

                <Route
                    path="/login"
                    element={<Login />}
                />
                <Route
                    path="/register"
                    element={<Register />}
                />


                {/* =========================
                    PROTECTED ROUTES
                ========================== */}

                <Route element={<ProtectedRoute />}>
                    

                    {/* Main application layout */}
                    <Route element={<AppLayout />}>

                        <Route
                            path="/"
                            element={
                                <Navigate
                                    to="/dashboard"
                                    replace
                                />
                            }
                        />

                        <Route
                            path="/dashboard"
                            element={<Dashboard />}
                        />

                        <Route
                            path="/chat"
                            element={<Chat />}
                        />

                        <Route
                            path="/documents"
                            element={<Documents />}
                        />

                        <Route
                            path="/connectors"
                            element={<Connectors />}
                        />
                        
                        <Route
                            path="/graph"
                            element={<KnowledgeGraph />}
                        />                        

                        <Route
                            path="/search"
                            element={<Search />}
                        />

                        <Route
                            path="/organization"
                            element={<Organization />}
                        />

                        <Route
                            path="/settings"
                            element={<Settings />}
                        />

                    </Route>

                </Route>

            </Routes>
        </BrowserRouter>
    );
}

export default AppRouter;