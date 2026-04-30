"use client";

import React, { useState, useEffect } from "react";
import DashboardShell from "@/components/DashboardShell";
import { useAuth } from "@/hooks/useAuth";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from "recharts";
import { 
  Leaf, 
  BookOpen, 
  FlaskConical, 
  Binary, 
  ChevronRight,
  Info,
  Zap,
  Target,
  RefreshCw
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function ResearchPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [baselineQ, setBaselineQ] = useState(15.0);
  const [methodQ, setMethodQ] = useState(9.3);
  const [literatureData, setLiteratureData] = useState<any[]>([]);
  const [ablationData, setAblationData] = useState<any[]>([]);
  const [isAblating, setIsAblating] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);

  useEffect(() => {
    fetchLiterature();
    runAblation(); // Run once on load
  }, []);

  const fetchLiterature = async () => {
    try {
      const res = await fetch("http://localhost:8000/research/literature", {
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
      });
      if (res.status === 401) return;
      const data = await res.json();
      if (Array.isArray(data)) {
        setLiteratureData(data.map((d: any) => ({
          name: d.Method,
          reduction: d["Reduction %"],
          source: d.Source
        })));
      }
    } catch (e) {
      // Silently handle connection errors - backend may not be running
      console.warn("Backend unavailable - literature data unavailable");
    }
  };

  const runAblation = async () => {
    setIsAblating(true);
    try {
      const res = await fetch("http://localhost:8000/research/ablation", {
        method: "POST",
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
      });
      if (res.status === 401) {
        setIsAblating(false);
        return;
      }
      const data = await res.json();
      if (Array.isArray(data)) {
        setAblationData(data.map((d: any) => ({
          feature: d.Configuration,
          impact: parseFloat(d["Accuracy %"]) / 100
        })));
      }
    } catch (e) {
      // Silently handle connection errors - backend may not be running
      console.warn("Backend unavailable - ablation data unavailable");
    }
    setIsAblating(false);
  };

  const runOptimization = async () => {
     setIsOptimizing(true);
     try {
       await fetch("http://localhost:8000/research/optimize", {
         method: "POST",
         headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
       });
       alert("Optimization (Optuna) started in background. Check server logs for progress.");
     } catch(e) {
       console.warn("Backend unavailable - optimization not started");
       alert("Cannot start optimization - backend server unavailable.");
     }
     setIsOptimizing(false);
  };

  // Carbon math
  const reduction = ((baselineQ - methodQ) / (baselineQ || 1)) * 100;
  const trees = Math.max(0, Math.floor(reduction * 1.5));

  if (authLoading) return null;
  if (!isAuthenticated) return null;

  return (
    <DashboardShell>
      <div className="flex flex-col gap-10 pb-10">
        {/* Header Section */}
        <section className="flex justify-between items-end">
          <div>
            <h2 className="text-3xl font-bold text-white tracking-tight">Research & Academic Hub</h2>
            <p className="text-slate-400 mt-1">Academic benchmarking, carbon impact assessment, and model interpretability.</p>
          </div>
          <button 
            onClick={runOptimization}
            disabled={isOptimizing}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-xl font-bold border border-blue-500/20 transition-all text-xs"
          >
            <Target className={cn("w-4 h-4", isOptimizing && "animate-spin")} />
            {isOptimizing ? "Optimizing..." : "Trigger Optuna Tuning"}
          </button>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Section 1: Carbon Calculator */}
          <div className="glass-card p-8 flex flex-col gap-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2.5 bg-emerald-500/10 rounded-xl text-emerald-400">
                <Leaf className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">CO₂ Impact Calculator</h3>
            </div>
            
            <p className="text-sm text-slate-400 leading-relaxed">
              Calculate the environmental benefits of your AI controller compared to standard fixed-cycle timing.
            </p>

            <div className="grid grid-cols-2 gap-6 mt-2">
              <div className="space-y-2">
                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Baseline Avg Queue (Veh)</label>
                <input 
                  type="number" 
                  value={baselineQ} 
                  onChange={(e) => setBaselineQ(parseFloat(e.target.value))}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:border-emerald-500/50 outline-none transition-all"
                />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500">AI Method Avg Queue (Veh)</label>
                <input 
                  type="number" 
                  value={methodQ} 
                  onChange={(e) => setMethodQ(parseFloat(e.target.value))}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:border-emerald-500/50 outline-none transition-all"
                />
              </div>
            </div>

            <div className="bg-emerald-500/5 border border-emerald-500/10 rounded-2xl p-6 mt-2 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-emerald-500/80 uppercase tracking-widest mb-1">Queue Reduction</p>
                <span className="text-3xl font-black text-emerald-400">{reduction.toFixed(1)}%</span>
              </div>
              <div className="text-right">
                <p className="text-xs font-bold text-emerald-500/80 uppercase tracking-widest mb-1">Equivalent Trees Saved</p>
                <span className="text-3xl font-black text-white">🌳 {trees} / yr</span>
              </div>
            </div>
          </div>

          {/* Section 2: Literature Benchmarks */}
          <div className="glass-card p-8 flex flex-col gap-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2.5 bg-blue-500/10 rounded-xl text-blue-400">
                <BookOpen className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">Literature Benchmarks</h3>
            </div>

            <div className="h-[250px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={literatureData} layout="vertical" margin={{ left: 40, right: 30 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" horizontal={false} />
                  <XAxis type="number" domain={[0, 40]} hide />
                  <YAxis 
                    dataKey="name" 
                    type="category" 
                    axisLine={false} 
                    tickLine={false}
                    tick={{ fill: "#94a3b8", fontSize: 10, fontWeight: 600 }}
                    width={100}
                  />
                  <Tooltip 
                    cursor={{ fill: "rgba(255,255,255,0.03)" }}
                    contentStyle={{ backgroundColor: "#0f172a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "12px", fontSize: "11px" }}
                  />
                  <Bar dataKey="reduction" radius={[0, 4, 4, 0]} barSize={16}>
                    {literatureData.map((entry, index) => (
                      <Cell key={index} fill={entry.name.includes("This Project") || entry.name.includes("DQN") ? "#60a5fa" : "#334155"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            <p className="text-[10px] text-slate-500 font-medium italic mt-2">
              Source: Academic benchmarks comparing percentage reduction in wait time or queue length.
            </p>
          </div>

          {/* Section 3: Ablation Study */}
          <div className="glass-card p-8 flex flex-col gap-6">
            <div className="flex items-center justify-between">
               <div className="flex items-center gap-3">
                <div className="p-2.5 bg-purple-500/10 rounded-xl text-purple-400">
                  <FlaskConical className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-white tracking-tight">Feature Ablation Study</h3>
              </div>
              <button onClick={runAblation} disabled={isAblating} className="text-slate-500 hover:text-white transition-colors">
                 <RefreshCw className={cn("w-4 h-4", isAblating && "animate-spin")} />
              </button>
            </div>

            <div className="space-y-5 mt-2">
              {ablationData.length === 0 ? <p className="text-slate-600 italic text-sm">Running study...</p> : 
               ablationData.map((item) => (
                <div key={item.feature} className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-300">{item.feature}</span>
                    <span className="text-slate-500 font-mono">{(item.impact * 100).toFixed(1)}% Acc</span>
                  </div>
                  <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.4)] transition-all duration-1000" 
                      style={{ width: `${item.impact * 100}%` }} 
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 4: Academic Resources */}
          <div className="glass-card p-8 flex flex-col gap-6 relative group bg-gradient-to-br from-white/[0.02] to-transparent">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2.5 bg-slate-500/10 rounded-xl text-slate-400">
                <Binary className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">Export Academic Report</h3>
            </div>

            <p className="text-sm text-slate-400 leading-relaxed flex-1">
              Generate a comprehensive PDF/HTML report including all charts, tables, and CO₂ analysis formatted for project documentation.
            </p>

            <button className="w-full py-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl flex items-center justify-center gap-3 transition-all text-white font-bold group-hover:border-blue-500/30">
              <span className="text-sm">Download Full Report (.html)</span>
              <ChevronRight className="w-4 h-4 text-blue-500" />
            </button>
            
            <div className="flex items-start gap-2 p-3 bg-blue-500/5 rounded-xl border border-blue-500/10 mt-auto">
              <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
              <p className="text-[10px] text-blue-400/80 leading-normal">
                Reports are generated based on the current active run state and historical database trends.
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardShell>
  );
}
