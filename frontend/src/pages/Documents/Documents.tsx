import { useEffect, useState } from "react";
import { ChevronRight, FileText, Loader2, RefreshCw } from "lucide-react";
import { getDocument, getDocuments, getDocumentChunks, type DocumentDetails, type DocumentItem } from "../../services/api/documents";

export default function Documents() {
    const [documents, setDocuments] = useState<DocumentItem[]>([]);
    const [selected, setSelected] = useState<DocumentDetails | null>(null);
    const [chunks, setChunks] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const load = async () => {
        setLoading(true); setError("");
        try { setDocuments(await getDocuments()); }
        catch (e: any) { setError(e?.response?.data?.detail || "Unable to load documents."); }
        finally { setLoading(false); }
    };
    useEffect(()=>{ load(); },[]);

    const open = async (id:number) => {
        setError("");
        try { const [doc, c] = await Promise.all([getDocument(id), getDocumentChunks(id)]); setSelected(doc); setChunks(c); }
        catch (e:any) { setError(e?.response?.data?.detail || "Unable to open document."); }
    };

    if (loading) return <div className="flex items-center justify-center p-10 text-slate-500"><Loader2 size={18} className="mr-2 animate-spin"/>Loading documents...</div>;
    return <div className="space-y-6">
        <div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold">Documents</h1><p className="mt-1 text-sm text-slate-500">Browse documents available to your current authorization scope.</p></div><button onClick={load} className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm"><RefreshCw size={15}/>Refresh</button></div>
        {error&&<div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        <div className="grid gap-4 lg:grid-cols-5"><div className="space-y-2 lg:col-span-2">{documents.length===0?<div className="rounded-xl border border-dashed bg-white p-8 text-center text-sm text-slate-500">No accessible documents.</div>:documents.map(d=><button key={d.id} onClick={()=>open(d.id)} className={`flex w-full items-center gap-3 rounded-xl border bg-white p-4 text-left shadow-sm hover:bg-slate-50 ${selected?.id===d.id?"border-slate-900":""}`}><FileText size={20} className="text-slate-500"/><div className="min-w-0 flex-1"><div className="truncate font-medium">{d.title}</div><div className="truncate text-xs text-slate-500">{d.file_path}</div><div className="mt-1 text-xs text-slate-400">{d.processing_status}</div></div><ChevronRight size={16}/></button>)}</div><div className="rounded-xl border bg-white p-5 shadow-sm lg:col-span-3">{!selected?<div className="flex min-h-80 items-center justify-center text-sm text-slate-500">Select a document.</div>:<><h2 className="text-xl font-semibold">{selected.title}</h2><p className="mt-1 text-xs text-slate-500">{selected.file_path}</p><div className="mt-4 whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-sm leading-6">{selected.content}</div><h3 className="mt-6 font-semibold">Chunks</h3><div className="mt-3 space-y-2">{chunks.map(c=><div key={c.id} className="rounded-lg border p-3"><div className="text-xs text-slate-500">Chunk {c.chunk_index}</div><div className="mt-1 whitespace-pre-wrap text-sm">{c.content}</div></div>)}</div></>}</div></div>
    </div>;
}
