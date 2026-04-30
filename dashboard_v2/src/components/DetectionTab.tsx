"use client";
import { useState } from "react";

export default function DetectionTab() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res  = await fetch("http://localhost:8000/api/detect", { method: "POST", body: form });
      setResult(await res.json());
    } catch (error) {
      console.error("Detection failed:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="glass-card p-8 rounded-3xl border border-white/[0.08] space-y-6">
      <p className="text-xs font-black uppercase tracking-widest text-slate-500">Vehicle Detection</p>

      <input type="file" accept="image/*" onChange={handleUpload}
        className="text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl
                   file:border-0 file:bg-blue-500/20 file:text-blue-400 cursor-pointer" />

      {loading && <p className="text-slate-500 animate-pulse text-sm">Detecting vehicles...</p>}

      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <img src={`data:image/jpeg;base64,${result.annotated_image}`}
               className="rounded-2xl w-full" alt="detected" />
          <div className="space-y-3">
            <div className="glass-card p-5 rounded-2xl text-center">
              <p className="text-4xl font-black text-blue-400">{result.total}</p>
              <p className="text-xs text-slate-500 mt-1">Total Vehicles</p>
            </div>
            {Object.entries(result.counts).map(([type, count]) => (
              <div key={type} className="flex justify-between px-4 py-3 glass-card rounded-xl">
                <span className="text-sm capitalize text-slate-400">{type}</span>
                <span className="font-bold text-white">{count as number}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
