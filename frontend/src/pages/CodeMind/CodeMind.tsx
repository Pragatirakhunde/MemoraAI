import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  Code2,
  Loader2,
  Network,
  Sparkles,
} from "lucide-react";

import { getMyProjects } from "../../services/api/projects";
import {
    askCodeMind,
    businessRule,
    codeSearch,
    getArchitecture,
    getCodeFiles,
    getCodeSymbols,
    getHistory,
    getProjectCodeRepositories,
    getDependencies,
    getImpact,
} from "../../services/api/codemind";

export default function CodeMind() {
    const [projects, setProjects] = useState<any[]>([]);
    const [projectId, setProjectId] = useState<number | "">("");
    const [query, setQuery] = useState("");
    const [answer, setAnswer] = useState("");
    const [refs, setRefs] = useState<any[]>([]);
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [files, setFiles] = useState<any[]>([]);
    const [symbols, setSymbols] = useState<any[]>([]);
    const [architecture, setArchitecture] = useState<any>(null);
    const [repos, setRepos] = useState<any[]>([]);
    const [history, setHistory] = useState<any[]>([]);
    const [dependencies, setDependencies] = useState<any>(null);
    const [impact, setImpact] = useState<any[]>([]);
    const [businessRuleText, setBusinessRuleText] = useState("");
    const [businessRuleResult, setBusinessRuleResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [analysisLoading, setAnalysisLoading] = useState<number | null>(null);
    const [error, setError] = useState("");

    useEffect(() => {
        getMyProjects()
            .then(setProjects)
            .catch((e) => setError(e?.response?.data?.detail || "Unable to load assigned projects"));
    }, []);

    const loadProject = async (id: number) => {
        setProjectId(id);
        setError("");
        setAnswer("");
        setRefs([]);
        setSearchResults([]);
        setDependencies(null);
        setImpact([]);
        setBusinessRuleResult(null);
        setLoading(true);
        try {
            const [f, s, a, r, h] = await Promise.all([
                getCodeFiles(id),
                getCodeSymbols(id),
                getArchitecture(id),
                getProjectCodeRepositories(id),
                getHistory(id),
            ]);
            setFiles(f); setSymbols(s); setArchitecture(a); setRepos(r); setHistory(h);
        } catch (e: any) {
            setError(e?.response?.data?.detail || "Unable to load CodeMind project");
        } finally { setLoading(false); }
    };

    const ask = async () => {
        if (!projectId || !query.trim()) return;
        setLoading(true); setError("");
        try {
            const [a, s] = await Promise.all([
                askCodeMind(Number(projectId), query),
                codeSearch(Number(projectId), query, 8),
            ]);
            setAnswer(a.answer); setRefs(a.references || []); setSearchResults(s || []);
        } catch (e: any) { setError(e?.response?.data?.detail || e.message || "CodeMind failed"); }
        finally { setLoading(false); }
    };

    const inspectSymbol = async (symbolId: number) => {
        if (!projectId) return;
        setAnalysisLoading(symbolId); setError("");
        try {
            const [deps, effects] = await Promise.all([
                getDependencies(Number(projectId), symbolId),
                getImpact(Number(projectId), symbolId),
            ]);
            setDependencies(deps); setImpact(effects || []);
        } catch (e: any) { setError(e?.response?.data?.detail || "Unable to inspect symbol"); }
        finally { setAnalysisLoading(null); }
    };

    const runBusinessRule = async () => {
        if (!projectId || !businessRuleText.trim()) return;
        setLoading(true); setError("");
        try { setBusinessRuleResult(await businessRule(Number(projectId), businessRuleText, 8)); }
        catch (e: any) { setError(e?.response?.data?.detail || "Unable to map business rule"); }
        finally { setLoading(false); }
    };

    const languages = useMemo(() => new Set(files.map(f => f.language).filter(Boolean)).size, [files]);

    return <div className="space-y-6">
        <div><h1 className="flex items-center gap-2 text-3xl font-bold"><Code2/>CodeMind</h1><p className="mt-1 text-sm text-slate-500">Project-scoped code understanding, semantic search and dependency analysis.</p></div>
        {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        <div className="rounded-xl border bg-white p-5 shadow-sm">
            <label className="text-sm font-medium">Assigned project</label>
            <select value={projectId} onChange={e=>e.target.value&&loadProject(Number(e.target.value))} className="mt-2 w-full rounded-lg border px-3 py-2">
                <option value="">Select a project</option>
                {projects.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
        </div>

        {projectId!=="" && <>
            <div className="grid gap-4 md:grid-cols-5">
                <Metric title="Repositories" value={repos.length}/><Metric title="Files" value={files.length}/><Metric title="Symbols" value={symbols.length}/><Metric title="Languages" value={languages}/><Metric title="Commits" value={history.length}/>
            </div>

            <div className="rounded-xl border bg-white p-5 shadow-sm">
                <div className="flex items-center gap-2"><Sparkles size={18}/><h2 className="font-semibold">Ask CodeMind</h2></div>
                <div className="mt-4 flex gap-2"><input value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")ask()}} placeholder="Explain the payment flow..." className="flex-1 rounded-lg border px-3 py-2"/><button onClick={ask} disabled={loading||!query.trim()} className="rounded-lg bg-slate-900 px-4 py-2 text-white disabled:opacity-50">{loading?<Loader2 className="animate-spin" size={18}/> : "Ask"}</button></div>
                {answer && <div className="mt-5 whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-sm leading-6">{answer}</div>}
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
                <Panel title="References">{refs.length===0?<Empty/>:refs.map((r,i)=><div key={i} className="border-b py-3 text-sm last:border-0"><div className="font-medium">{r.file_path}</div><div className="text-slate-500">{r.symbol_name} · lines {r.start_line}-{r.end_line}</div></div>)}</Panel>
                <Panel title="Semantic search"><div className="space-y-2">{searchResults.length===0?<Empty/>:searchResults.map((r,i)=><div key={i} className="rounded-lg border p-3 text-sm"><div className="font-medium">{r.symbol_name || "File chunk"}</div><div className="text-slate-500">{r.file_path} · score {Number(r.score||0).toFixed(3)}</div></div>)}</div></Panel>
            </div>

            <Panel title="Architecture"><pre className="max-h-80 overflow-auto rounded-lg bg-slate-950 p-4 text-xs text-slate-100">{JSON.stringify(architecture,null,2)}</pre></Panel>

            <div className="grid gap-4 lg:grid-cols-2">
                <Panel title="Business rule → code">
                    <div className="flex gap-2"><input value={businessRuleText} onChange={e=>setBusinessRuleText(e.target.value)} placeholder="Refund cannot exceed original payment" className="flex-1 rounded-lg border px-3 py-2"/><button onClick={runBusinessRule} disabled={loading||!businessRuleText.trim()} className="rounded-lg bg-slate-900 px-4 py-2 text-white">Map</button></div>
                    {businessRuleResult && <pre className="mt-4 max-h-72 overflow-auto rounded-lg bg-slate-50 p-3 text-xs">{JSON.stringify(businessRuleResult,null,2)}</pre>}
                </Panel>
                <Panel title="Git history"><div className="space-y-2">{history.length===0?<Empty/>:history.slice(0,20).map((h,i)=><div key={i} className="border-b py-2 text-sm last:border-0"><div className="font-medium">{h.message}</div><div className="text-xs text-slate-500">{h.sha?.slice(0,10)} · {h.author_name || "Unknown"} · {h.committed_at ? new Date(h.committed_at).toLocaleString() : ""}</div></div>)}</div></Panel>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
                <Panel title="Symbols / dependencies"><div className="max-h-96 overflow-auto">{symbols.length===0?<Empty/>:symbols.slice(0,200).map(s=><div key={s.id} className="flex items-center justify-between gap-3 border-b py-2 text-sm last:border-0"><div><div className="font-medium">{s.qualified_name}</div><div className="text-xs text-slate-500">{s.symbol_type} · lines {s.start_line}-{s.end_line}</div></div><button onClick={()=>inspectSymbol(s.id)} className="inline-flex items-center gap-1 rounded border px-2 py-1 text-xs">{analysisLoading===s.id?<Loader2 size={13} className="animate-spin"/>:<Network size={13}/>}Inspect</button></div>)}</div></Panel>
                <Panel title="Dependency / impact result">{dependencies ? <div className="space-y-3 text-sm"><div><div className="font-semibold">{dependencies.symbol}</div><div className="text-slate-500">Callers: {dependencies.callers?.length||0} · Callees: {dependencies.callees?.length||0}</div></div><pre className="max-h-80 overflow-auto rounded-lg bg-slate-50 p-3 text-xs">{JSON.stringify({dependencies,impact},null,2)}</pre></div> : <Empty/>}</Panel>
            </div>

            <Panel title="Indexed files"><button onClick={()=>loadProject(Number(projectId))} className="mb-3 inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm">Refresh</button>{files.slice(0,100).map(f=><div key={f.id} className="border-b py-2 text-sm last:border-0"><span className="font-mono">{f.file_path}</span><span className="ml-3 text-slate-500">{f.language||"unknown"}</span></div>)}</Panel>
        </>}
    </div>;
}

function Metric({title,value}:{title:string;value:number}){return <div className="rounded-xl border bg-white p-4"><div className="text-sm text-slate-500">{title}</div><div className="mt-2 text-2xl font-bold">{value}</div></div>}
function Panel({title,children}:{title:string;children:ReactNode}){return <div className="rounded-xl border bg-white p-5 shadow-sm"><h3 className="font-semibold">{title}</h3><div className="mt-3">{children}</div></div>}
function Empty(){return <div className="py-6 text-center text-sm text-slate-500">No data yet.</div>}
