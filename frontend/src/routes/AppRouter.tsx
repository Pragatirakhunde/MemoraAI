import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "../layouts/AppLayout";
import Login from "../pages/Login";
import Register from "../pages/Register";
import ProtectedRoute from "./ProtectedRoute";
import RoleRoute from "./RoleRoute";
import Dashboard from "../pages/Dashboard/Dashboard";
import Chat from "../pages/Chat";
import Documents from "../pages/Documents/Documents";
import Connectors from "../pages/Connectors/Connectors";
import KnowledgeGraph from "../pages/KnowledgeGraph/KnowledgeGraph";
import Search from "../pages/Search/Search";
import Settings from "../pages/Settings/Settings";
import Organization from "../pages/Organization/Organization";
import AdminCenter from "../pages/Admin/AdminCenter";
import CodeMind from "../pages/CodeMind/CodeMind";

export default function AppRouter(){
 return <BrowserRouter><Routes>
  <Route path="/login" element={<Login/>}/><Route path="/register" element={<Register/>}/>
  <Route element={<ProtectedRoute/>}><Route element={<AppLayout/>}>
   <Route path="/" element={<Navigate to="/dashboard" replace/>}/>
   <Route path="/dashboard" element={<Dashboard/>}/>
   <Route path="/chat" element={<Chat/>}/>
   <Route path="/documents" element={<Documents/>}/>
   <Route path="/graph" element={<KnowledgeGraph/>}/>
   <Route path="/search" element={<Search/>}/>
   <Route path="/organization" element={<Organization/>}/>
   <Route path="/settings" element={<Settings/>}/>
   <Route path="/codemind" element={<CodeMind/>}/>
  </Route></Route>
  <Route element={<ProtectedRoute/>}><Route element={<RoleRoute role="admin"/>}><Route element={<AppLayout/>}><Route path="/connectors" element={<Connectors/>}/><Route path="/admin" element={<AdminCenter/>}/></Route></Route></Route>
 </Routes></BrowserRouter>
}
