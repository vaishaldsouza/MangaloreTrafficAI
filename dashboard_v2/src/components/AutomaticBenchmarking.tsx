"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  FileText, 
  BarChart3, 
  Download, 
  Clock,
  Award,
  Database,
  Calendar,
  Layers,
  ChevronRight,
  ExternalLink
} from "lucide-react";
import { cn } from "@/lib/utils";

interface RunSummary {
  id: number;
  timestamp: string;
  method: string;
  steps: number;
  avg_reward: number;
  avg_queue: number;
  peak_queue: number;
  high_cong_pct: number;
  free_cong_pct: number;
  notes: string;
}

export default function AutomaticBenchmarking() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingFor, setGeneratingFor] = useState<number | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://localhost:8000/analytics/history", {
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
      });
      const data = await res.json();
      setRuns(data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const generateReport = async (runId: number) => {
    setGeneratingFor(runId);
    try {
      const res = await fetch(`http://localhost:8000/analytics/report/${runId}`, {
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
      });
      const data = await res.json();
      if (data.html) {
         const blob = new Blob([data.html], { type: "text/html" });
         const url = URL.createObjectURL(blob);
         const a = document.createElement("a");
         a.href = url;
         a.download = `mangalore_traffic_report_${runId}.html`;
         a.click();
      }
    } catch (e) { alert("Failed to generate report."); }
    setGeneratingFor(null);
  };

  return (
    <div className="glass-card p-6 h-full flex flex-col gap-6 overflow-hidden">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-violet-500/10 rounded-xl border border-violet-500/20">
            <BarChart3 className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Comparative Analytics</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              Historical Performance Hub
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col gap-6">
        {/* Table */}
        <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-800">
           <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/5 text-[10px] font-black uppercase tracking-widest text-slate-500">
                  <th className="py-3 px-2">Run Method</th>
                  <th className="py-3 px-2 text-right">Avg Queue</th>
                  <th className="py-3 px-2 text-right">Avg Reward</th>
                  <th className="py-3 px-2 text-right">Flow %</th>
                  <th className="py-3 px-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {loading ? (
                   <tr><td colSpan={5} className="py-10 text-center text-slate-600 italic text-sm">Syncing with database...</td></tr>
                ) : runs.map((run) => (
                  <tr key={run.id} className="group hover:bg-white/[0.02]">
                    <td className="py-4 px-2">
                      <div className="flex flex-col">
                        <span className="text-white font-bold text-sm tracking-tight">{run.method}</span>
                        <span className="text-[9px] text-slate-500">#{run.id} • {run.timestamp}</span>
                      </div>
                    </td>
                    <td className="py-4 px-2 text-right font-mono text-xs text-blue-400 font-bold">
                       {run.avg_queue.toFixed(2)}
                    </td>
                    <td className="py-4 px-2 text-right font-mono text-xs text-white">
                       {run.avg_reward.toFixed(3)}
                    </td>
                    <td className="py-4 px-2 text-right">
                       <span className={cn(
                         "px-2 py-0.5 rounded-full text-[9px] font-bold",
                         run.free_cong_pct > 80 ? "bg-emerald-400/10 text-emerald-400" : "bg-orange-400/10 text-orange-400"
                       )}>
                         {run.free_cong_pct.toFixed(0)}%
                       </span>
                    </td>
                    <td className="py-4 px-2 text-right">
                       <button 
                         onClick={() => generateReport(run.id)}
                         disabled={generatingFor === run.id}
                         className="p-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-lg border border-blue-500/20 transition-all disabled:opacity-50"
                       >
                         {generatingFor === run.id ? <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" /> : <Download className="w-3 h-3" />}
                       </button>
                    </td>
                  </tr>
                ))}
              </tbody>
           </table>
        </div>

        {/* Research Info Card */}
        <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-2xl p-5 border border-indigo-500/20">
           <div className="flex items-center gap-3 mb-3">
              <Award className="w-5 h-5 text-yellow-400" />
              <h4 className="text-white font-bold text-sm">Automated Academic Reporting</h4>
           </div>
           <p className="text-[10px] text-slate-400 leading-relaxed mb-4">
             Each simulation run is automatically indexed and benchmarked. Click the download icon to generate a formatted HTML report containing SHAP analysis, carbon savings, and time-series charts for publication.
           </p>
           <button className="w-full py-3 bg-white/5 hover:bg-white/10 text-white rounded-xl text-[10px] font-bold uppercase tracking-widest border border-white/10 transition-all flex items-center justify-center gap-2">
             <span>Open Comparative Matrix</span>
             <ChevronRight className="w-3 h-3" />
           </button>
        </div>
      </div>
    </div>
  );
}
