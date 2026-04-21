"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Brain, 
  Cpu, 
  Zap, 
  TrendingUp, 
  Activity, 
  BarChart3,
  Network,
  Clock,
  Award,
  Terminal,
  Play,
  Square
} from "lucide-react";
import { cn } from "@/lib/utils";

interface TrainingLog {
  message: string;
  type: "LOG" | "ERROR" | "COMPLETE";
  reward?: number;
}

export default function ModelIntelligence() {
  const [isTraining, setIsTraining] = useState(false);
  const [logs, setLogs] = useState<TrainingLog[]>([]);
  const [rewardHistory, setRewardHistory] = useState<number[]>([]);
  const [config, setConfig] = useState({ algo: "PPO", timesteps: 10000, reward_type: "wait_time" });
  const ws = useRef<WebSocket | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const startTraining = () => {
    setIsTraining(true);
    setLogs([]);
    setRewardHistory([]);
    
    const token = localStorage.getItem("token");
    const clientId = Math.random().toString(36).substring(7);
    ws.current = new WebSocket(`ws://localhost:8000/research/training/ws/${clientId}?token=${token}`);

    ws.current.onopen = () => {
      ws.current?.send(JSON.stringify({ type: "START_TRAINING", ...config }));
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLogs(prev => [...prev, data].slice(-100));
      if (data.reward !== undefined) {
        setRewardHistory(prev => [...prev, data.reward].slice(-20));
      }
      if (data.type === "COMPLETE" || data.type === "ERROR") {
        setIsTraining(false);
      }
    };

    ws.current.onclose = () => setIsTraining(false);
  };

  const stopTraining = () => {
    ws.current?.send(JSON.stringify({ type: "STOP_TRAINING" }));
    ws.current?.close();
    setIsTraining(false);
  };

  return (
    <div className="glass-card p-6 h-full flex flex-col gap-6 overflow-hidden">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
            <Brain className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Advanced RL Training</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              Secure Cloud-Based Pipeline
            </p>
          </div>
        </div>
        
        <div className="flex gap-2">
          {isTraining ? (
            <button 
              onClick={stopTraining}
              className="px-4 py-2 bg-red-500/10 text-red-500 border border-red-500/20 rounded-xl text-xs font-bold flex items-center gap-2 hover:bg-red-500/20 transition-all"
            >
              <Square className="w-3 h-3 fill-current" />
              Stop
            </button>
          ) : (
            <button 
              onClick={startTraining}
              className="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold flex items-center gap-2 hover:bg-blue-500 transition-all shadow-lg shadow-blue-600/20"
            >
              <Play className="w-3 h-3 fill-current" />
              Train
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 overflow-hidden">
        {/* Left: Config & Visuals */}
        <div className="flex flex-col gap-6 overflow-y-auto pr-2 scrollbar-none">
          <div className="glass-card p-5 border-white/5 space-y-4">
             <div className="flex items-center gap-2 mb-2 text-blue-400">
                <Settings className="w-4 h-4" />
                <span className="text-[10px] font-black uppercase tracking-widest">Training Parameters</span>
             </div>
             
             <div className="space-y-3">
                <label className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Algorithm</label>
                <select 
                  value={config.algo}
                  onChange={(e) => setConfig({...config, algo: e.target.value})}
                  className="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-xs text-white outline-none focus:border-blue-500 transition-all"
                >
                  <option>PPO</option>
                  <option>DQN</option>
                </select>
             </div>

             <div className="space-y-3">
                <label className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Total Timesteps: {config.timesteps.toLocaleString()}</label>
                <input 
                  type="range" min="1000" max="50000" step="1000" 
                  value={config.timesteps}
                  onChange={(e) => setConfig({...config, timesteps: parseInt(e.target.value)})}
                  className="w-full accent-blue-500"
                />
             </div>
          </div>

          <div className="glass-card p-5 border-white/5 flex-1 flex flex-col">
            <div className="flex items-center justify-between mb-4">
               <div className="flex items-center gap-2 text-emerald-400">
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-[10px] font-black uppercase tracking-widest">Reward History</span>
               </div>
               <span className="text-[10px] text-slate-500 font-mono">Live rollout mean</span>
            </div>
            
            <div className="flex-1 min-h-[100px] flex items-end gap-1.5 pt-4">
              {rewardHistory.length === 0 ? (
                <div className="flex-1 flex items-center justify-center text-slate-700 italic text-[10px]">Awaiting rollout data...</div>
              ) : (
                rewardHistory.map((r, i) => (
                  <motion.div 
                    key={i}
                    initial={{ height: 0 }}
                    animate={{ height: `${Math.max(10, (r + 100) / 2)}%` }}
                    className={cn(
                      "flex-1 rounded-t-sm",
                      r > 0 ? "bg-emerald-400/60" : "bg-blue-400/40"
                    )}
                  />
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right: Terminal Logs */}
        <div className="glass-card p-4 bg-slate-950 border-white/10 rounded-2xl flex flex-col overflow-hidden relative group">
          <div className="flex items-center gap-2 mb-3 pb-3 border-b border-white/5">
            <Terminal className="w-4 h-4 text-slate-500" />
            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Execution Terminal</span>
            <div className="ml-auto flex gap-1">
              <div className="w-2 h-2 rounded-full bg-red-500/20" />
              <div className="w-2 h-2 rounded-full bg-yellow-500/20" />
              <div className="w-2 h-2 rounded-full bg-green-500/20" />
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto font-mono text-[10px] space-y-1.5 pr-2 scrollbar-thin scrollbar-thumb-slate-800">
            {logs.length === 0 && <p className="text-slate-700 italic">No active processes...</p>}
            {logs.map((log, i) => (
              <div key={i} className={cn(
                "leading-relaxed break-all",
                log.type === "ERROR" ? "text-red-400" : log.type === "COMPLETE" ? "text-emerald-400" : "text-slate-400"
              )}>
                <span className="text-slate-600 mr-2">[{new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'})}]</span>
                {log.message}
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
          
          {isTraining && (
            <div className="absolute inset-x-0 bottom-0 py-1 bg-blue-500/5 backdrop-blur-sm border-t border-blue-500/10 flex justify-center">
               <span className="text-[8px] font-bold text-blue-400/60 animate-pulse">SYSTEM_EXECUTING_STABLE_BASELINES3_SB3</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import { Settings } from "lucide-react";
