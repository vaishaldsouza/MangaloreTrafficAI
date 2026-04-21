"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Wind, 
  Leaf, 
  TrendingDown, 
  Activity, 
  BarChart3,
  Globe,
  AlertTriangle,
  Trees
} from "lucide-react";
import { cn } from "@/lib/utils";
import { SimStep } from "@/hooks/useSimulation";

interface EnvironmentalTrackingProps {
  currentData: SimStep | null;
  status: string;
}

export default function EnvironmentalTracking({ currentData, status }: EnvironmentalTrackingProps) {
  const [history, setHistory] = useState<number[]>([]);
  
  // Real-time environmental math (derived from queue length and reward)
  const co2 = currentData ? 150 + (currentData.total_queue * 4.5) : 0;
  const reduction = currentData ? Math.max(0, currentData.reward * 1.5) : 0;
  const trees = currentData ? Math.floor(reduction / 10) : 0;
  const fuel = currentData ? (reduction * 2.1).toFixed(1) : "0.0";

  useEffect(() => {
    if (currentData && status === "running") {
      setHistory(prev => [...prev, co2].slice(-30));
    }
  }, [currentData, status]);

  return (
    <div className="glass-card p-6 h-full flex flex-col gap-6 overflow-hidden">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-green-500/10 rounded-xl border border-green-500/20">
            <Leaf className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Ecological Footprint</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              Live Emission Diagnostics
            </p>
          </div>
        </div>
        
        <div className={cn(
          "px-3 py-1 rounded-full border text-[10px] font-black uppercase tracking-widest",
          co2 < 200 ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20 shadow-[0_0_10px_rgba(52,211,153,0.1)]" : "text-orange-400 bg-orange-500/10 border-orange-500/20"
        )}>
          {status === "running" ? (co2 < 200 ? "Excellent Flow" : "Moderate Congestion") : "Engine Idle"}
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col gap-6">
        {/* Real-time KPIs */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/[0.03] rounded-[24px] p-5 border border-white/5 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
               <Wind className="w-12 h-12 text-white" />
            </div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Live CO2 Index</span>
            </div>
            <div className="text-3xl font-black text-white">{co2.toFixed(1)}<span className="text-xs text-slate-500 ml-1">g/km</span></div>
          </div>
          
          <div className="bg-white/[0.03] rounded-[24px] p-5 border border-white/5 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
               <TrendingDown className="w-12 h-12 text-emerald-400" />
            </div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Policy Efficiency</span>
            </div>
            <div className="text-3xl font-black text-emerald-400">+{reduction.toFixed(1)}<span className="text-xs ml-1">%</span></div>
          </div>
        </div>

        {/* Global Impact Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/[0.03] rounded-[24px] p-5 border border-white/5 flex flex-col justify-between">
            <div>
              <Globe className="w-5 h-5 text-blue-400/60 mb-2" />
              <span className="text-[9px] text-slate-500 font-black uppercase tracking-wider block">Estimated Fuel Saved</span>
            </div>
            <div className="text-2xl font-black text-white mt-4">{fuel}<span className="text-[10px] text-slate-500 ml-1">Liters</span></div>
          </div>
          
          <div className="bg-white/[0.03] rounded-[24px] p-5 border border-white/5 flex flex-col justify-between">
            <div>
               <Trees className="w-5 h-5 text-emerald-400/60 mb-2" />
               <span className="text-[9px] text-slate-500 font-black uppercase tracking-wider block">Trees Offset Credit</span>
            </div>
            <div className="text-2xl font-black text-emerald-400 mt-4">{trees}<span className="text-[10px] text-emerald-400/50 ml-1">Units</span></div>
          </div>
        </div>

        {/* Chart */}
        <div className="flex-1 flex flex-col bg-slate-900/40 rounded-[28px] border border-white/5 p-6 relative">
          <div className="flex items-center justify-between mb-4">
             <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-slate-500" />
                <span className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Real-time Emission Profile</span>
             </div>
             {status === "running" && <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping" />}
          </div>
          
          <div className="flex-1 flex items-end justify-between gap-1 mt-2">
            {history.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-[10px] text-slate-700 italic">Streaming sensor telemetry...</div>
            ) : (
              history.map((val, i) => (
                <motion.div
                  key={i}
                  initial={{ height: 0 }}
                  animate={{ height: `${(val / 400) * 100}%` }}
                  className={cn(
                    "flex-1 rounded-t-sm min-h-[4px]",
                    val < 200 ? "bg-emerald-400/80 shadow-[0_0_8px_rgba(52,211,153,0.2)]" : "bg-orange-400/60"
                  )}
                />
              ))
            )}
          </div>
          
          <div className="flex items-center justify-between mt-4">
            <span className="text-[8px] text-slate-500 font-bold uppercase tracking-tight">Window: Continuous Rollout</span>
            <span className="text-[8px] text-slate-500 font-bold uppercase tracking-tight">Baseline: Fixed-Cycle (214.5g)</span>
          </div>
        </div>
      </div>

      <div className="mt-2 pt-4 border-t border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-3 h-3 text-slate-500" />
          <span className="text-[9px] text-slate-500 uppercase tracking-widest font-bold">Mangalore Urban AI Network</span>
        </div>
        <div className="flex items-center gap-1">
           <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
           <span className="text-[9px] text-slate-400 font-bold">Cloud Sync Active</span>
        </div>
      </div>
    </div>
  );
}
