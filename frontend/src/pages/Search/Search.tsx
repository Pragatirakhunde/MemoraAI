import { useState } from "react";
import { Loader2, Search as SearchIcon } from "lucide-react";
import { semanticSearch, type SearchResult } from "../../services/api/search";

export default function Search() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const runSearch = async () => {
        if (!query.trim()) return;
        setLoading(true); setError("");
        try { setResults(await semanticSearch(query.trim(), 10)); }
        catch (e: any) { setError(e?.response?.data?.detail || "Search failed."); }
        finally { setLoading(false); }
    };

    return <div className="space-y-6">
        <div><h1 className="text-3xl font-bold">Semantic Search</h1><p className="mt-1 text-sm text-slate-500">Search organizational knowledge using the authorized vector index.</p></div>
        {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        <div className="rounded-xl border bg-white p-5 shadow-sm"><div className="flex gap-2"><input value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>e.key==="Enter"&&runSearch()} placeholder="Search policies, decisions, projects..." className="flex-1 rounded-lg border px-3 py-2"/><button onClick={runSearch} disabled={loading||!query.trim()} className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-white disabled:opacity-50">{loading?<Loader2 size={17} className="animate-spin"/>:<SearchIcon size={17}/>}Search</button></div></div>
        <div className="space-y-3">{results.length===0?<div className="rounded-xl border border-dashed bg-white p-10 text-center text-sm text-slate-500">No results yet.</div>:results.map((r,i)=><article key={`${r.chunk_id}-${i}`} className="rounded-xl border bg-white p-5 shadow-sm"><div className="flex items-center justify-between gap-4"><div><h2 className="font-semibold">{r.title}</h2><p className="text-xs text-slate-500">{r.reference.file_path} · score {r.score.toFixed(3)}</p></div></div><p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">{r.content}</p></article>)}</div>
    </div>;
}
