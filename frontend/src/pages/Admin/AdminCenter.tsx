import { useEffect, useState, type ReactNode } from "react";
import { Archive, Check, Plus, RefreshCw, UserCheck, Users, FolderKanban, Building2, Trash2, Code2 } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import {
    approveUser,
    assignDepartment,
    assignProjectMember,
    archiveProjectAdmin,
    createDepartment,
    createProjectAdmin,
    deactivateUser,
    getDepartments,
    getOrganizationAdmin,
    getPendingUsers,
    getProjectMembers,
    getProjectsAdmin,
    getUsers,
    rejectUser,
    removeProjectMember,
    updateOrganizationAdmin,
} from "../../services/api/admin";
import {
    createCodeRepository,
    indexCodeRepository,
    listCodeRepositories,
    validateCodeRepository,
} from "../../services/api/codemind";

interface Member { id: number; project_id: number; user_id: number; permission: string; created_at: string; updated_at: string; }

export default function AdminCenter() {
    const { user } = useAuth();
    const [tab, setTab] = useState("overview");
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [users, setUsers] = useState<any[]>([]);
    const [pending, setPending] = useState<any[]>([]);
    const [departments, setDepartments] = useState<any[]>([]);
    const [projects, setProjects] = useState<any[]>([]);
    const [repositories, setRepositories] = useState<any[]>([]);
    const [org, setOrg] = useState<any>(null);
    const [newDept, setNewDept] = useState("");
    const [newProject, setNewProject] = useState("");
    const [repoForm, setRepoForm] = useState({ projectId: "", name: "", provider: "local" as "local" | "github", localPath: "", remoteUrl: "", branch: "main" });
    const [members, setMembers] = useState<Record<number, Member[]>>({});
    const [loadingMembers, setLoadingMembers] = useState<number | null>(null);
    const [indexing, setIndexing] = useState(false);

    const load = async () => {
        if (!user) return;
        setLoading(true); setError("");
        try {
            const [u, p, d, pr, o, r] = await Promise.all([
                getUsers(),
                getPendingUsers(),
                getDepartments(),
                getProjectsAdmin(),
                getOrganizationAdmin(user.organization_id),
                listCodeRepositories(),
            ]);
            setUsers(u); setPending(p); setDepartments(d); setProjects(pr); setOrg(o); setRepositories(r);
        } catch (e: any) {
            setError(e?.response?.data?.detail || "Unable to load admin data");
        } finally { setLoading(false); }
    };

    useEffect(() => { load(); }, [user?.organization_id]);

    const run = async (fn: () => Promise<any>, success = "Done") => {
        try { setError(""); await fn(); setMessage(success); await load(); }
        catch (e: any) { setError(e?.response?.data?.detail || e.message || "Operation failed"); }
    };

    const toggleMembers = async (projectId: number) => {
        if (members[projectId]) {
            setMembers(current => { const next = { ...current }; delete next[projectId]; return next; });
            return;
        }
        setLoadingMembers(projectId); setError("");
        try {
            const data = await getProjectMembers(projectId);
            setMembers(current => ({ ...current, [projectId]: data }));
        } catch (e: any) {
            setError(e?.response?.data?.detail || "Unable to load project members");
        }
        finally { setLoadingMembers(null); }
    };

    const submitRepository = async () => {
        if (!repoForm.projectId || !repoForm.name.trim()) {
            setError("Select a project and enter a repository name."); return;
        }
        setIndexing(true); setError(""); setMessage("");
        try {
            const repo = await createCodeRepository({
                project_id: Number(repoForm.projectId),
                name: repoForm.name.trim(),
                provider: repoForm.provider,
                local_path: repoForm.provider === "local" ? repoForm.localPath.trim() || null : null,
                remote_url: repoForm.provider === "github" ? repoForm.remoteUrl.trim() || null : null,
                default_branch: repoForm.branch.trim() || "main",
            } as any);
            const validation = await validateCodeRepository(repo.id);
            if (!validation.valid) throw new Error(validation.error || "Repository validation failed");
            await indexCodeRepository(repo.id);
            setMessage(`CodeMind indexed ${repoForm.name} successfully.`);
            setRepositories(await listCodeRepositories());
        } catch (e: any) {
            setError(e?.response?.data?.detail || e.message || "CodeMind indexing failed");
        } finally { setIndexing(false); }
    };

    if (loading) return <div className="p-8">Loading admin center...</div>;

    return <div className="space-y-6">
        <div className="flex items-center justify-between gap-4">
            <div><h1 className="text-3xl font-bold text-slate-900">Admin Center</h1><p className="mt-1 text-sm text-slate-500">Manage organization access, projects, employees and CodeMind sources.</p></div>
            <button onClick={load} className="inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm"><RefreshCw size={16}/>Refresh</button>
        </div>
        {(error || message) && <div className={`rounded-lg border p-3 text-sm ${error ? "border-red-200 bg-red-50 text-red-700" : "border-green-200 bg-green-50 text-green-700"}`}>{error || message}</div>}
        <div className="flex flex-wrap gap-2">
            {["overview","requests","employees","departments","projects","organization","codemind"].map(x => <button key={x} onClick={() => setTab(x)} className={`rounded-lg px-4 py-2 text-sm font-medium ${tab===x?"bg-slate-900 text-white":"border bg-white text-slate-700"}`}>{x[0].toUpperCase()+x.slice(1)}</button>)}
        </div>

        {tab === "overview" && <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <Stat label="Employees" value={users.filter(u => u.role === "employee").length} icon={<Users size={20}/>}/>
            <Stat label="Pending" value={pending.length} icon={<UserCheck size={20}/>}/>
            <Stat label="Departments" value={departments.length} icon={<Building2 size={20}/>}/>
            <Stat label="Active Projects" value={projects.filter(p=>p.status === "active").length} icon={<FolderKanban size={20}/>}/>
        </div>}

        {tab === "requests" && <Section title="Pending registration requests"><div className="space-y-3">{pending.length===0 ? <Empty/> : pending.map(u => <div key={u.id} className="flex items-center justify-between gap-3 rounded-lg border p-4"><div><div className="font-medium">{u.name}</div><div className="text-sm text-slate-500">{u.email}</div></div><div className="flex gap-2"><button onClick={()=>run(()=>approveUser(u.id),"Employee approved")} className="inline-flex items-center gap-1 rounded-lg bg-emerald-600 px-3 py-2 text-sm text-white"><Check size={15}/>Approve</button><button onClick={()=>run(()=>rejectUser(u.id),"Employee rejected")} className="rounded-lg border px-3 py-2 text-sm">Reject</button></div></div>)}</div></Section>}

        {tab === "employees" && <Section title="Employees"><div className="overflow-auto"><table className="min-w-full text-sm"><thead><tr className="border-b text-left"><th className="p-2">Name</th><th className="p-2">Email</th><th className="p-2">Status</th><th className="p-2">Department</th><th className="p-2">Actions</th></tr></thead><tbody>{users.filter(u=>u.role==="employee").map(u=><tr key={u.id} className="border-b"><td className="p-2">{u.name}</td><td className="p-2">{u.email}</td><td className="p-2">{u.approval_status}/{u.is_active?"active":"inactive"}</td><td className="p-2"><select value={u.department_id ?? ""} onChange={e=>run(()=>assignDepartment(u.id,e.target.value?Number(e.target.value):null))} className="rounded border px-2 py-1"><option value="">Unassigned</option>{departments.map(d=><option key={d.id} value={d.id}>{d.name}</option>)}</select></td><td className="p-2"><button onClick={()=>run(()=>deactivateUser(u.id),"Employee deactivated")} disabled={!u.is_active} className="rounded border px-3 py-1 disabled:opacity-50">Deactivate</button></td></tr>)}</tbody></table></div></Section>}

        {tab === "departments" && <Section title="Departments"><div className="mb-4 flex gap-2"><input value={newDept} onChange={e=>setNewDept(e.target.value)} placeholder="Department name" className="flex-1 rounded-lg border px-3 py-2"/><button onClick={()=>newDept.trim()&&run(async()=>{await createDepartment({name:newDept.trim()});setNewDept("");},"Department created")} className="inline-flex items-center gap-1 rounded-lg bg-blue-600 px-4 py-2 text-white"><Plus size={15}/>Add</button></div><div className="grid gap-3 md:grid-cols-2">{departments.map(d=><div key={d.id} className="rounded-lg border p-4"><div className="font-medium">{d.name}</div><div className="text-sm text-slate-500">{d.description || ""}</div></div>)}</div></Section>}

        {tab === "projects" && <Section title="Projects"><div className="mb-4 flex gap-2"><input value={newProject} onChange={e=>setNewProject(e.target.value)} placeholder="Project name" className="flex-1 rounded-lg border px-3 py-2"/><button onClick={()=>newProject.trim()&&run(async()=>{const slug=newProject.toLowerCase().trim().replace(/[^a-z0-9]+/g,"-");await createProjectAdmin({name:newProject.trim(),slug});setNewProject("");},"Project created")} className="inline-flex items-center gap-1 rounded-lg bg-blue-600 px-4 py-2 text-white"><Plus size={15}/>Create</button></div><div className="space-y-4">{projects.map(p=><ProjectCard key={p.id} project={p} users={users} members={members[p.id]} membersLoading={loadingMembers===p.id} onToggleMembers={()=>toggleMembers(p.id)} onAssign={(uid)=>run(()=>assignProjectMember(p.id,uid),"Member assigned")} onRemove={(uid)=>run(()=>removeProjectMember(p.id,uid),"Member removed")} onArchive={()=>run(()=>archiveProjectAdmin(p.id),"Project archived")}/>)}</div></Section>}

        {tab === "organization" && <Section title="Organization"><div className="grid gap-4 md:grid-cols-2"><label className="text-sm">Name<input value={org?.name || ""} onChange={e=>setOrg({...org,name:e.target.value})} className="mt-1 w-full rounded border px-3 py-2"/></label><label className="text-sm">Slug<input value={org?.slug || ""} disabled className="mt-1 w-full rounded border bg-slate-50 px-3 py-2"/></label><label className="text-sm md:col-span-2">Description<textarea value={org?.description || ""} onChange={e=>setOrg({...org,description:e.target.value})} className="mt-1 w-full rounded border px-3 py-2" rows={5}/></label></div><button onClick={()=>run(()=>updateOrganizationAdmin(org.id,{name:org.name,description:org.description}),"Organization updated")} className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-white">Save organization</button></Section>}

        {tab === "codemind" && <Section title="CodeMind repositories"><p className="text-sm text-slate-600">Create a repository source for a specific project and index it. Local paths can point to a checked-out repository; GitHub repositories can be added by remote URL.</p><div className="mt-5 grid gap-3 md:grid-cols-2 lg:grid-cols-3"><label className="text-sm">Project<select value={repoForm.projectId} onChange={e=>setRepoForm({...repoForm,projectId:e.target.value})} className="mt-1 w-full rounded border px-3 py-2"><option value="">Select project</option>{projects.filter(p=>p.status==="active").map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label><label className="text-sm">Repository name<input value={repoForm.name} onChange={e=>setRepoForm({...repoForm,name:e.target.value})} className="mt-1 w-full rounded border px-3 py-2" placeholder="PayFlow Codebase"/></label><label className="text-sm">Provider<select value={repoForm.provider} onChange={e=>setRepoForm({...repoForm,provider:e.target.value as "local"|"github"})} className="mt-1 w-full rounded border px-3 py-2"><option value="local">Local</option><option value="github">GitHub</option></select></label>{repoForm.provider==="local"?<label className="text-sm md:col-span-2">Local path<input value={repoForm.localPath} onChange={e=>setRepoForm({...repoForm,localPath:e.target.value})} className="mt-1 w-full rounded border px-3 py-2 font-mono" placeholder="..\\datasets\\technova\\payflow"/></label>:<label className="text-sm md:col-span-2">Remote URL<input value={repoForm.remoteUrl} onChange={e=>setRepoForm({...repoForm,remoteUrl:e.target.value})} className="mt-1 w-full rounded border px-3 py-2" placeholder="https://github.com/org/repo.git"/></label>}<label className="text-sm">Branch<input value={repoForm.branch} onChange={e=>setRepoForm({...repoForm,branch:e.target.value})} className="mt-1 w-full rounded border px-3 py-2"/></label></div><button onClick={submitRepository} disabled={indexing} className="mt-4 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-white disabled:opacity-50"><Code2 size={16}/>{indexing?"Indexing...":"Create & index repository"}</button><div className="mt-6 space-y-2">{repositories.length===0?<Empty/>:repositories.map(r=><div key={r.id} className="flex flex-wrap items-center justify-between gap-3 rounded-lg border p-3 text-sm"><div><div className="font-medium">{r.name}</div><div className="text-slate-500">Project #{r.project_id} · {r.provider} · {r.index_status}</div></div><span className="text-xs text-slate-500">{r.last_indexed_at?new Date(r.last_indexed_at).toLocaleString():"Not indexed"}</span></div>)}</div></Section>}
    </div>
}

function Section({title,children}:{title:string;children:ReactNode}) { return <div className="rounded-xl border bg-white p-6 shadow-sm"><h2 className="text-xl font-semibold">{title}</h2><div className="mt-5">{children}</div></div> }
function Empty(){ return <div className="rounded-lg border border-dashed p-8 text-center text-sm text-slate-500">Nothing to review.</div> }
function Stat({label,value,icon}:{label:string;value:number;icon:ReactNode}){return <div className="rounded-xl border bg-white p-5"><div className="flex items-center justify-between text-slate-500"><span>{label}</span>{icon}</div><div className="mt-3 text-3xl font-bold">{value}</div></div>}
function ProjectCard({project,users,members,membersLoading,onToggleMembers,onAssign,onRemove,onArchive}:{project:any;users:any[];members?:Member[];membersLoading:boolean;onToggleMembers:()=>void;onAssign:(id:number)=>void;onRemove:(id:number)=>void;onArchive:()=>void}){const [uid,setUid]=useState("");return <div className="rounded-xl border p-4"><div className="flex flex-wrap items-center justify-between gap-3"><div><div className="font-semibold">{project.name}</div><div className="text-xs text-slate-500">{project.slug} · {project.status}</div></div><div className="flex gap-2"><button onClick={onToggleMembers} className="rounded-lg border px-3 py-2 text-sm">{members?"Hide members":"Members"}</button>{project.status==="active"&&<button onClick={onArchive} className="inline-flex items-center gap-1 rounded-lg border border-amber-200 px-3 py-2 text-sm text-amber-700"><Archive size={15}/>Archive</button>}</div></div><div className="mt-4 flex gap-2"><select value={uid} onChange={e=>setUid(e.target.value)} className="flex-1 rounded border px-3 py-2"><option value="">Assign employee...</option>{users.filter(u=>u.role==="employee"&&u.approval_status==="APPROVED"&&u.is_active).map(u=><option key={u.id} value={u.id}>{u.name}</option>)}</select><button disabled={!uid || project.status!=="active"} onClick={()=>{onAssign(Number(uid));setUid("")}} className="rounded-lg border px-4 py-2 text-sm disabled:opacity-50">Assign</button></div>{membersLoading&&<div className="mt-4 text-sm text-slate-500">Loading members...</div>}{members&&<div className="mt-4 space-y-2">{members.length===0?<Empty/>:members.map(m=>{const u=users.find(x=>x.id===m.user_id);return <div key={m.id} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"><div><span className="font-medium">{u?.name||`User ${m.user_id}`}</span><span className="ml-2 text-slate-500">{m.permission}</span></div><button onClick={()=>onRemove(m.user_id)} className="inline-flex items-center gap-1 text-red-600"><Trash2 size={14}/>Remove</button></div>})}</div>}</div>}
