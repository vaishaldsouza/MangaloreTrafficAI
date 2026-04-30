"use client";

import React, { useEffect, useState } from "react";
import DashboardShell from "@/components/DashboardShell";
import { useAuth } from "@/hooks/useAuth";
import { motion } from "framer-motion";
import { 
  Search, 
  Filter, 
  Download, 
  Trash2, 
  ExternalLink,
  ChevronRight,
  Clock,
  Calendar,
  Layers,
  Activity
} from "lucide-react";
import { cn } from "@/lib/utils";

type RunSummary = {
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
};

export default function HistoryPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    if (isAuthenticated) {
      fetchRuns();
    }
  }, [isAuthenticated]);

  const fetchRuns = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/analytics/history", {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.status === 401) {
        console.error("Unauthorized access to history");
        setRuns([]);
        setLoading(false);
        return;
      }

      if (!res.ok) {
        setRuns([]);
        setLoading(false);
        return;
      }
      
      const data = await res.json();
      
      // Ensure data is an array
      if (Array.isArray(data)) {
        setRuns(data);
      } else {
        console.warn("API returned non-array data:", data);
        setRuns([]);
      }
    } catch (error) {
      // Silently handle connection errors - backend may not be running
      console.warn("Backend unavailable - history data unavailable");
      setRuns([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredRuns = Array.isArray(runs) ? runs.filter(run => 
    run.method.toLowerCase().includes(searchTerm.toLowerCase()) ||
    run.notes?.toLowerCase().includes(searchTerm.toLowerCase())
  ) : [];

  if (authLoading) return null;
  if (!isAuthenticated) return null;

  return (
    <DashboardShell>
      <div className="flex flex-col gap-8">
        {/* Header Section */}
        <section className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold text-white tracking-tight">Simulation Archive</h2>
            <p className="text-slate-400 mt-1">Review and analyze performance metrics from past simulation runs.</p>
          </div>
          
          <div className="flex gap-3">
            <div className="relative group">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
              <input 
                type="text" 
                placeholder="Search by method or notes..."
                className="bg-white/5 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all w-full md:w-64"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button className="p-2.5 bg-white/5 border border-white/10 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-all">
              <Filter className="w-5 h-5" />
            </button>
          </div>
        </section>

        {/* Runs Table */}
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/5 bg-white/[0.02]">
                  <th className="p-5 text-xs font-bold uppercase tracking-widest text-slate-500">ID</th>
                  <th className="p-5 text-xs font-bold uppercase tracking-widest text-slate-500">Run Info</th>
                  <th className="p-5 text-xs font-bold uppercase tracking-widest text-slate-500">Metrics</th>
                  <th className="p-5 text-xs font-bold uppercase tracking-widest text-slate-500">Congestion</th>
                  <th className="p-5 text-xs font-bold uppercase tracking-widest text-slate-500 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {loading ? (
                  Array(5).fill(0).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan={5} className="p-8 text-center text-slate-600">Loading historical data...</td>
                    </tr>
                  ))
                ) : filteredRuns.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-20 text-center">
                      <Layers className="w-12 h-12 text-slate-700 mx-auto mb-4" />
                      <p className="text-slate-500 font-medium text-lg">No simulation runs found</p>
                    </td>
                  </tr>
                ) : filteredRuns.map((run) => (
                  <tr key={run.id} className="group hover:bg-white/[0.02] transition-colors">
                    <td className="p-5 align-top">
                      <span className="text-xs font-mono font-bold text-slate-500 bg-white/5 px-2 py-1 rounded">#{run.id}</span>
                    </td>
                    <td className="p-5 align-top">
                      <div className="flex flex-col gap-1.5">
                        <span className="text-white font-bold text-sm tracking-tight">{run.method}</span>
                        <div className="flex items-center gap-3 text-[10px] text-slate-500 font-semibold mt-1">
                          <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {run.timestamp.split(' ')[0]}</span>
                          <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {run.timestamp.split(' ')[1]}</span>
                        </div>
                      </div>
                    </td>
                    <td className="p-5 align-top">
                      <div className="grid grid-cols-2 gap-x-8 gap-y-2">
                        <div className="flex flex-col">
                          <span className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Avg Reward</span>
                          <span className="text-blue-400 font-bold text-sm">{run.avg_reward.toFixed(4)}</span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Avg Queue</span>
                          <span className="text-white font-bold text-sm">{run.avg_queue.toFixed(1)} <span className="text-[10px] font-normal text-slate-500">v</span></span>
                        </div>
                      </div>
                    </td>
                    <td className="p-5 align-top">
                      <div className="flex items-center gap-4 h-full">
                        <div className="flex-1 max-w-[100px] h-1.5 bg-white/5 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-emerald-500" 
                            style={{ width: `${run.free_cong_pct}%` }} 
                          />
                        </div>
                        <span className="text-[10px] font-black text-emerald-500">{run.free_cong_pct.toFixed(0)}% Flow</span>
                      </div>
                    </td>
                    <td className="p-5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button className="p-2 text-slate-500 hover:text-white hover:bg-white/10 rounded-lg transition-all" title="View details">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all" title="Delete run">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Summary Footer */}
        <div className="flex items-center justify-between text-slate-500 text-xs font-medium px-2">
          <p>Showing {filteredRuns.length} of {runs.length} recorded episodes</p>
          <div className="flex gap-4">
             <span className="flex items-center gap-1.5"><Activity className="w-4 h-4" /> Real-time database synced</span>
          </div>
        </div>
      </div>
    </DashboardShell>
  );
}
