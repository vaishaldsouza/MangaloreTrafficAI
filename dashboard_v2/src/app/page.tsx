"use client";

import React, { useState } from "react";
import DashboardShell from "@/components/DashboardShell";
import MapView from "@/components/MapView";
import AIDecisionLogs from "@/components/AIDecisionLogs";
import ModelIntelligence from "@/components/ModelIntelligence";
import EnvironmentalTracking from "@/components/EnvironmentalTracking";
import AutomaticBenchmarking from "@/components/AutomaticBenchmarking";
import RouteFinder from "@/components/RouteFinder";
import { useSimulation } from "@/hooks/useSimulation";
import { useAuth } from "@/hooks/useAuth";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Play, 
  Square,
  TrendingUp, 
  Car, 
  Layers,
  Activity,
  AlertCircle,
  Brain,
  FileText,
  Leaf,
  Navigation,
  Settings,
  TrafficCone
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function Home() {
  const { data, status, startSimulation, stopSimulation } = useSimulation();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState("overview");
  
  const [simConfig, setSimConfig] = useState({
    method: "PPO RL Model",
    scenario: "Normal",
    steps: 200,
    backend: "Python Simulator",
    reward_type: "wait_time"
  });

  const controllers = [
    "Fixed-cycle baseline",
    "Actuated signals",
    "Greedy adaptive",
    "Random Forest",
    "LSTM predictor",
    "Ensemble controller",
    "PPO RL Model",
    "DQN RL Model"
  ];

  const scenarios = [
    { id: "Normal", label: "🌤️ Normal Day" },
    { id: "Monsoon", label: "🌧️ Heavy Monsoon" },
    { id: "Rush Hour", label: "🌅 Morning Rush Hour" },
    { id: "Accident", label: "🚨 Accident Response" }
  ];

  const backends = ["Python Simulator", "SUMO"];
  const rewards = ["wait_time", "queue_length", "co2_emission", "balanced"];

  const tabs = [
    { id: "overview", label: "Overview", icon: Activity },
    { id: "ai-decisions", label: "AI Decisions", icon: Brain },
    { id: "model-intelligence", label: "Model Intelligence", icon: TrendingUp },
    { id: "environmental", label: "Environmental", icon: Leaf },
    { id: "benchmarking", label: "Benchmarking", icon: FileText },
    { id: "route-finder", label: "Route Finder", icon: Navigation }
  ];

  if (authLoading) return null;
  if (!isAuthenticated) return null;

  // Mangalore Center (Hampankatta area)
  const mapCenter: [number, number] = [12.8700, 74.8400];

  return (
    <DashboardShell>
      <div className="flex flex-col gap-8">
        {/* Header Section */}
        <section className="flex items-end justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className={cn(
                "w-2 h-2 rounded-full",
                status === "running" ? "bg-emerald-500 animate-pulse" : "bg-slate-500"
              )} />
              <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500">
                {status === "running" ? "System Live" : "System Standby"}
              </p>
            </div>
            <h2 className="text-3xl font-bold text-white tracking-tight">Traffic Control Center</h2>
          </div>
          
          <div className="flex gap-3">
            {status === "running" ? (
              <button 
                onClick={stopSimulation}
                className="flex items-center gap-2 px-6 py-3 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-2xl font-bold transition-all border border-red-500/20 shadow-lg shadow-red-500/5 group"
              >
                <div className="w-2 h-2 bg-red-500 rounded-full animate-ping" />
                <span>Terminate Run</span>
              </button>
            ) : (
              <button 
                onClick={() => startSimulation(simConfig)}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-bold transition-all shadow-xl shadow-blue-600/30 group active:scale-95"
              >
                <Play className="w-5 h-5 fill-current transition-transform group-hover:scale-110" />
                <span>Initialize AI Engine</span>
              </button>
            )}
          </div>
        </section>

        {/* Top Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard 
            title="Current Queue" 
            value={data?.total_queue.toFixed(1) || "0.0"} 
            unit="vehicles" 
            change={status === "running" ? "Live Data" : "--"} 
            icon={Car} 
            color="blue"
          />
          <MetricCard 
            title="Reward Signal" 
            value={data?.reward.toFixed(3) || "0.000"} 
            unit="pts" 
            change={status === "running" ? "Live Feedback" : "--"} 
            icon={TrendingUp} 
            color="green"
          />
          <MetricCard 
            title="Simulation Step" 
            value={data?.step.toString() || "0"} 
            unit={`/ ${simConfig.steps}`} 
            change={status === "running" ? "Processing" : "--"} 
            icon={Activity} 
            color="purple"
          />
          <MetricCard 
            title="Traffic State" 
            value={data?.congestion.toUpperCase() || "IDLE"} 
            unit="" 
            change={status === "running" ? "Continuous Monitoring" : "--"} 
            icon={Layers} 
            color="orange"
          />
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center gap-3 px-6 py-3 rounded-2xl font-bold text-xs transition-all whitespace-nowrap",
                  activeTab === tab.id
                    ? "bg-blue-500/15 text-blue-400 border border-blue-500/30 shadow-lg shadow-blue-500/5"
                    : "bg-white/5 text-slate-500 hover:bg-white/10 border border-transparent hover:text-slate-300"
                )}
              >
                <Icon className={cn("w-4 h-4", activeTab === tab.id ? "text-blue-400" : "text-slate-500")} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === "overview" && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[650px]"
            >
              <div className="lg:col-span-2 glass-card overflow-hidden relative group rounded-3xl border border-white/[0.08]">
                <AnimatePresence>
                  {status === "idle" && (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="absolute inset-0 flex items-center justify-center bg-slate-950/40 backdrop-blur-md z-20"
                    >
                      <div className="text-center p-10 bg-slate-900/80 rounded-[32px] border border-white/10 shadow-2xl max-w-sm">
                        <div className="w-20 h-20 bg-blue-500/10 rounded-[28px] flex items-center justify-center mx-auto mb-6 border border-blue-500/20">
                          <TrafficCone className="w-10 h-10 text-blue-400" />
                        </div>
                        <h3 className="text-2xl font-black text-white tracking-tight">System Offline</h3>
                        <p className="text-slate-400 text-sm mt-3 leading-relaxed">
                          Initialize the AI engine using the control panel on the right to start real-time traffic monitoring.
                        </p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
                
                <MapView 
                  center={mapCenter} 
                  zoom={16} 
                  vehicles={data?.vehicles || []} 
                />
              </div>

              <div className="flex flex-col gap-6 h-full">
                <div className="glass-card p-8 flex-1 flex flex-col rounded-3xl border border-white/[0.08]">
                  <h3 className="text-xl font-bold text-white mb-8 flex items-center gap-3">
                    <div className="p-2 bg-slate-800 rounded-xl">
                      <Settings className="w-5 h-5 text-blue-400" />
                    </div>
                    Engine Configuration
                  </h3>
                  
                  <div className="space-y-6 flex-1 overflow-y-auto pr-2 scrollbar-none">
                    <ParamGroup label="Control Algorithm">
                      <select 
                        value={simConfig.method}
                        onChange={(e) => setSimConfig({...simConfig, method: e.target.value})}
                        className="w-full bg-slate-800/50 border border-white/10 rounded-2xl px-5 py-4 text-sm text-white outline-none focus:border-blue-500 transition-all cursor-pointer hover:bg-slate-800"
                      >
                        {controllers.map(c => <option key={c} value={c}>{c}</option>)}
                      </select>
                    </ParamGroup>

                    <ParamGroup label="Simulation Backend">
                      <div className="grid grid-cols-2 gap-3">
                        {backends.map(b => (
                          <button
                            key={b}
                            onClick={() => setSimConfig({...simConfig, backend: b})}
                            className={cn(
                              "px-4 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all",
                              simConfig.backend === b 
                                ? "bg-blue-500/10 border-blue-500/30 text-blue-400" 
                                : "bg-white/5 border-transparent text-slate-500 hover:bg-white/10"
                            )}
                          >
                            {b}
                          </button>
                        ))}
                      </div>
                    </ParamGroup>

                    <ParamGroup label="Reward Function">
                      <select 
                        value={simConfig.reward_type}
                        onChange={(e) => setSimConfig({...simConfig, reward_type: e.target.value})}
                        className="w-full bg-slate-800/50 border border-white/10 rounded-2xl px-5 py-4 text-sm text-white outline-none focus:border-blue-500 transition-all cursor-pointer hover:bg-slate-800"
                      >
                        {rewards.map(r => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
                      </select>
                    </ParamGroup>

                    <ParamGroup label="Scenario Context">
                      <select 
                        value={simConfig.scenario}
                        onChange={(e) => setSimConfig({...simConfig, scenario: e.target.value})}
                        className="w-full bg-slate-800/50 border border-white/10 rounded-2xl px-5 py-4 text-sm text-white outline-none focus:border-blue-500 transition-all cursor-pointer hover:bg-slate-800"
                      >
                        {scenarios.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
                      </select>
                    </ParamGroup>

                    <ParamGroup label={`Target Horizon: ${simConfig.steps} steps`}>
                      <input 
                        type="range" 
                        min="50" 
                        max="1000" 
                        step="50"
                        value={simConfig.steps}
                        onChange={(e) => setSimConfig({...simConfig, steps: parseInt(e.target.value)})}
                        className="w-full accent-blue-500"
                      />
                    </ParamGroup>
                  </div>
                  
                  <div className="mt-8 pt-6 border-t border-white/5">
                    <div className="p-4 bg-orange-500/5 rounded-2xl border border-orange-500/10 flex gap-4">
                      <AlertCircle className="w-6 h-6 text-orange-400/60 shrink-0" />
                      <p className="text-[11px] text-slate-400 leading-relaxed">
                        <span className="text-orange-400 font-bold block mb-1">Compute Note:</span>
                        High-fidelity SUMO simulations require higher CPU overhead. Real-time updates may be throttled based on system performance.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === "ai-decisions" && (
            <motion.div
              key="ai-decisions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-[650px]"
            >
              <AIDecisionLogs currentData={data} status={status} />
            </motion.div>
          )}

          {activeTab === "model-intelligence" && (
            <motion.div
              key="model-intelligence"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-[650px]"
            >
              <ModelIntelligence />
            </motion.div>
          )}

          {activeTab === "environmental" && (
            <motion.div
              key="environmental"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-[650px]"
            >
              <EnvironmentalTracking currentData={data} status={status} />
            </motion.div>
          )}

          {activeTab === "benchmarking" && (
            <motion.div
              key="benchmarking"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-[650px]"
            >
              <AutomaticBenchmarking />
            </motion.div>
          )}

          {activeTab === "route-finder" && (
            <motion.div
              key="route-finder"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-[650px]"
            >
              <RouteFinder />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </DashboardShell>
  );
}

function ParamGroup({ label, children }: { label: string, children: React.ReactNode }) {
  return (
    <div className="space-y-4">
      <label className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 ml-1">
        {label}
      </label>
      {children}
    </div>
  );
}

function MetricCard({ title, value, unit, change, icon: Icon, color }: any) {
  const colors: any = {
    blue: "text-blue-400 bg-blue-500/10",
    green: "text-emerald-400 bg-emerald-500/10",
    purple: "text-purple-400 bg-purple-500/10",
    orange: "text-orange-400 bg-orange-500/10",
  };

  return (
    <div className="glass-card p-6 group transition-all duration-500 border border-white/[0.05] hover:border-white/10 rounded-3xl relative overflow-hidden">
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-white/5 to-transparent blur-2xl -mr-8 -mt-8 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      <div className="flex items-start justify-between">
        <div className={cn("p-3 rounded-2xl transition-all duration-500 group-hover:scale-110 group-hover:rotate-3 shadow-lg", colors[color])}>
          <Icon className="w-5 h-5 shadow-inner" />
        </div>
        <span className={cn(
          "text-[9px] font-black px-3 py-1.5 rounded-full uppercase tracking-widest border border-transparent transition-all duration-500",
          change === "Live Data" || change === "Processing" || change === "Live Feedback" || change === "Continuous Monitoring"
            ? "text-emerald-400 bg-emerald-400/10 border-emerald-400/20 shadow-[0_0_10px_rgba(52,211,153,0.15)]" 
            : "text-slate-500 bg-white/5"
        )}>
          {change}
        </span>
      </div>
      <div className="mt-6">
        <h4 className="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-1.5">{title}</h4>
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-black text-white tracking-tighter drop-shadow-md">{value}</span>
          {unit && <span className="text-slate-600 text-[10px] font-black uppercase tracking-widest">{unit}</span>}
        </div>
      </div>
    </div>
  );
}
