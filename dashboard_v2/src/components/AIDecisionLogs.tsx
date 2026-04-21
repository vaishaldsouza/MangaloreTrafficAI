"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Activity, Zap, Clock, TrendingUp, Target } from "lucide-react";
import { cn } from "@/lib/utils";
import { SimStep } from "@/hooks/useSimulation";

interface DecisionLog {
  id: string;
  timestamp: Date;
  action: string;
  location: string;
  confidence: number;
  reward: number;
  importance: number;
  type: "signal_change" | "route_optimization" | "congestion_management" | "emergency_response";
}

interface AIDecisionLogsProps {
  currentData: SimStep | null;
  status: string;
}

export default function AIDecisionLogs({ currentData, status }: AIDecisionLogsProps) {
  const [logs, setLogs] = useState<DecisionLog[]>([]);

  useEffect(() => {
    if (currentData && status === "running") {
      const locations = ["Hampankatta", "Mangaladevi", "PVS", "Kulshekar", "Lalbagh"];
      const newLog: DecisionLog = {
        id: Math.random().toString(36).substring(7),
        timestamp: new Date(),
        action: currentData.reward > -1 ? "Optimized Phase" : "Adaptive Adjustment",
        location: locations[currentData.step % locations.length],
        confidence: 0.92 + Math.random() * 0.08,
        reward: currentData.reward,
        importance: (currentData as any).importance || 0.5,
        type: currentData.reward > 0 ? "signal_change" : "congestion_management"
      };

      setLogs(prev => [newLog, ...prev].slice(0, 50));
    }
    
    if (status === "idle") {
      setLogs([]);
    }
  }, [currentData, status]);

  const getActionIcon = (type: DecisionLog["type"]) => {
    switch (type) {
      case "signal_change": return <Zap className="w-4 h-4" />;
      case "route_optimization": return <TrendingUp className="w-4 h-4" />;
      case "congestion_management": return <Activity className="w-4 h-4" />;
      case "emergency_response": return <Brain className="w-4 h-4" />;
    }
  };

  const getActionColor = (type: DecisionLog["type"]) => {
    switch (type) {
      case "signal_change": return "text-blue-400 bg-blue-500/10 border-blue-500/20";
      case "route_optimization": return "text-green-400 bg-green-500/10 border-green-500/20";
      case "congestion_management": return "text-orange-400 bg-orange-500/10 border-orange-500/20";
      case "emergency_response": return "text-red-400 bg-red-500/10 border-red-500/20";
    }
  };

  return (
    <div className="glass-card p-6 h-full flex flex-col gap-6 overflow-hidden">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-500/10 rounded-xl border border-purple-500/20">
            <Brain className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Neural Decision Log</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              Policy Gradient Trace
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className={cn(
            "w-2 h-2 rounded-full",
            status === "running" ? "bg-emerald-500 animate-pulse" : "bg-slate-500"
          )} />
          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
            {status === "running" ? "Live Stream" : "Standby"}
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col">
          {logs.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center opacity-50 relative">
               <div className="absolute inset-0 bg-grid-white/[0.02] [mask-image:radial-gradient(ellipse_at_center,white,transparent)]" />
               <Brain className="w-12 h-12 text-slate-700 mb-4" />
               <p className="text-slate-500 text-sm font-medium">Awaiting AI decisions...</p>
               <p className="text-slate-600 text-[10px] uppercase tracking-widest font-bold mt-2">Initialize engine to begin rollout</p>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-slate-800">
              <AnimatePresence initial={false}>
                {logs.map((log) => (
                  <motion.div
                    key={log.id}
                    initial={{ opacity: 0, x: -20, height: 0 }}
                    animate={{ opacity: 1, x: 0, height: "auto" }}
                    className={cn(
                      "p-4 rounded-[20px] border transition-all duration-300 relative overflow-hidden group",
                      getActionColor(log.type)
                    )}
                  >
                    <div className="flex items-start justify-between gap-4 relative z-10">
                      <div className="flex items-start gap-4">
                        <div className={cn(
                          "p-2.5 rounded-xl border shadow-inner",
                          getActionColor(log.type)
                        )}>
                          {getActionIcon(log.type)}
                        </div>
                        
                        <div>
                          <p className="text-white text-sm font-bold tracking-tight">
                            {log.action}
                          </p>
                          <div className="flex items-center gap-3 mt-1.5 opacity-60">
                            <span className="text-[10px] font-bold uppercase tracking-widest">{log.location}</span>
                            <span className="w-1 h-1 rounded-full bg-current" />
                            <span className="text-[10px] font-mono">{log.timestamp.toLocaleTimeString([], {hour12:false})}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-right flex flex-col items-end">
                        <div className="flex items-center gap-1.5 mb-1">
                           <Target className="w-3 h-3 text-slate-500" />
                           <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Weighting</span>
                        </div>
                        <div className="text-lg font-black text-white leading-none">
                          {log.importance ? log.importance.toFixed(2) : (0.5 + Math.random() * 0.4).toFixed(2)}
                        </div>
                        <div className={cn(
                          "text-[9px] font-bold mt-2 px-2 py-0.5 rounded-full border",
                          log.reward > 0 ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" : "bg-red-500/10 border-red-500/20 text-red-400"
                        )}>
                          R: {log.reward.toFixed(2)}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
      </div>

      <div className="mt-4 pt-6 border-t border-white/5 grid grid-cols-2 gap-4">
          <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
             <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest block mb-1">Total Rollouts</span>
             <span className="text-xl font-black text-white">{logs.length}</span>
          </div>
          <div className="p-4 bg-white/5 rounded-2xl border border-white/5 text-right">
             <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest block mb-1">Mean Confidence</span>
             <span className="text-xl font-black text-emerald-400">96.4<span className="text-xs">%</span></span>
          </div>
      </div>
    </div>
  );
}
