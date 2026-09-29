import { LayoutDashboard, Building2, PlugZap, FileText, Network, Bot, Search, Settings, ShieldCheck, Code2 } from "lucide-react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Sidebar(){
 const {user}=useAuth();
 const common=[
  {title:"Dashboard",icon:LayoutDashboard,path:"/dashboard"},
  {title:"Organization",icon:Building2,path:"/organization"},
  {title:"Documents",icon:FileText,path:"/documents"},
  {title:"Knowledge Graph",icon:Network,path:"/graph"},
  {title:"AI Assistant",icon:Bot,path:"/chat"},
  {title:"CodeMind",icon:Code2,path:"/codemind"},
  {title:"Search",icon:Search,path:"/search"},
  {title:"Settings",icon:Settings,path:"/settings"},
 ];
 const menus=user?.role==="admin"?[{title:"Data Sources",icon:PlugZap,path:"/connectors"},...common,{title:"Admin Center",icon:ShieldCheck,path:"/admin"}]:common;
 return <aside className="w-64 bg-slate-900 text-white"><div className="border-b border-slate-700 p-6"><h1 className="text-xl font-bold">Memora AI</h1><p className="text-sm text-slate-400">Enterprise Organizational Memory</p></div><nav className="mt-4">{menus.map(m=>{const Icon=m.icon;return <NavLink key={m.path} to={m.path} className={({isActive})=>`mx-2 mb-2 flex items-center gap-3 rounded-lg px-4 py-3 transition ${isActive?"bg-blue-600":"hover:bg-slate-800"}`}><Icon size={20}/>{m.title}</NavLink>})}</nav></aside>;
}
