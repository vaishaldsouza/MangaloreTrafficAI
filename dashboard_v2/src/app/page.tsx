"use client";

import React, { useState } from "react";
import DashboardShell from "@/components/DashboardShell";
import MapView from "@/components/MapView";
import AIDecisionLogs from "@/components/AIDecisionLogs";
import ModelIntelligence from "@/components/ModelIntelligence";
import EnvironmentalTracking from "@/components/EnvironmentalTracking";
import AutomaticBenchmarking from "@/components/AutomaticBenchmarking";
import RouteFinder from "@/components/RouteFinder";
import { useSimulation, SimStep } from "@/hooks/useSimulation";
import LiveMetricsChart from "@/components/LiveMetricsChart";
import { useAuth } from "@/hooks/useAuth";
import { motion, AnimatePresence } from "framer-motion";
import GraphPanel from "@/components/GraphPanel";
import DetectionTab from "@/components/DetectionTab";
import TechniqueComparison from "@/components/TechniqueComparison";
import DatasetImport from "@/components/DatasetImport";
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
  TrafficCone,
  Loader2,
  Camera,
  Upload,
  Database
} from "lucide-react";
import { cn } from "@/lib/utils";

const getLos = (queue: number) => {
  if (queue < 5) return "A";
  if (queue < 10) return "B";
  if (queue < 20) return "C";
  if (queue < 35) return "D";
  if (queue < 50) return "E";
  return "F";
};

export default function Home() {
  const { data, history, status, startSimulation, stopSimulation } = useSimulation();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState("overview");
  
  const [simConfig, setSimConfig] = useState({
    method: "PPO RL Model",
    scenario: "Normal",
    steps: 200,
    backend: "Python Simulator",
    reward_type: "wait_time",
    use_cv: false,
    n_junctions: 1,
  });

  const [datasetLoaded, setDatasetLoaded] = useState(false);
  const [backendDown, setBackendDown] = useState(false);

  React.useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch("http://localhost:8000/health");
        setBackendDown(!res.ok);
      } catch {
        setBackendDown(true);
      }
    };
    checkBackend();
    const interval = setInterval(checkBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  const [detResult, setDetResult] = useState<any>(null);
  const [detLoading, setDetLoading] = useState(false);

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setDetLoading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("http://localhost:8000/api/detect", { method: "POST", body: form });
      const data = await res.json();
      setDetResult(data);
    } catch (error) {
      console.error("Detection failed:", error);
    } finally {
      setDetLoading(false);
    }
  }

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
    { id: "route-finder", label: "Route Finder", icon: Navigation },
    { id: "technique-compare", label: "Technique Comparison", icon: TrendingUp },
    { id: "detection", label: "Detection", icon: Camera }
  ];

  if (authLoading) return (
    <div className="flex h-screen items-center justify-center bg-[#0d1117]">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (!isAuthenticated) return null; // router handles redirect

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
                status === "running" ? "bg-emerald-500 status-live" : "bg-slate-500"
              )} />
              <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500">
                {status === "running" ? "System Live" : "System Standby"}
              </p>
            </div>
            <h2 className="text-3xl font-bold text-white tracking-tight">Traffic Control Center</h2>
          </div>
          
          <div className="flex items-center gap-4">
            {datasetLoaded && (
              <div className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 rounded-xl text-cyan-400 text-xs font-bold shadow-lg shadow-cyan-500/5">
                <Database className="w-4 h-4" />
                Dataset Ready
              </div>
            )}
            {backendDown && (
              <div className="flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs font-bold animate-pulse">
                <AlertCircle className="w-4 h-4" />
                Backend Offline
              </div>
            )}
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
          <MetricCard
            title="Level of Service"
            value={data ? getLos(data.total_queue) : "—"}
            unit="HCM Grade"
            change={status === "running" ? "Live Data" : "--"}
            icon={AlertCircle}
            color={data && getLos(data.total_queue) <= "B" ? "green" : (data && getLos(data.total_queue) >= "E" ? "orange" : "purple")}
          />
        </div>

        {/* Live Visualizations & LoS */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3 glass-card p-6 rounded-3xl border border-white/[0.08]">
             <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm font-bold text-white uppercase tracking-wider">Live Queue Metric</h4>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Level of Service</span>
                  <span className={`text-2xl font-black ${
                    data && (getLos(data.total_queue) === "A" || getLos(data.total_queue) === "B") ? "text-emerald-400" :
                    data && (getLos(data.total_queue) === "C" || getLos(data.total_queue) === "D") ? "text-yellow-400" : "text-red-400"
                  }`}>{data ? getLos(data.total_queue) : "—"}</span>
                </div>
             </div>
             <div className="h-[300px] w-full">
               <LiveMetricsChart history={history} />
             </div>
          </div>

          <div className="glass-card p-6 rounded-3xl border border-white/[0.08] flex flex-col justify-center gap-4">
             {data ? (
                <>
                  <div className="bg-slate-800/50 rounded-2xl p-4 border border-white/5">
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Current Reward</p>
                    <p className="text-2xl font-black text-white">{data.reward.toFixed(2)}</p>
                  </div>
                  <div className="bg-slate-800/50 rounded-2xl p-4 border border-white/5">
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">CO₂ Emissions</p>
                    <p className="text-2xl font-black text-white">{data.co2_mg.toFixed(0)} <span className="text-xs text-slate-500 font-normal">mg</span></p>
                  </div>
                  <div className="bg-slate-800/50 rounded-2xl p-4 border border-white/5">
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Active Phase</p>
                    <p className="text-sm font-bold text-blue-400">{data.phase_name}</p>
                  </div>
                </>
             ) : (
                <div className="text-center py-10">
                   <Activity className="w-8 h-8 text-slate-700 mx-auto mb-3" />
                   <p className="text-xs text-slate-500">Awaiting stream...</p>
                </div>
             )}
          </div>
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
              className="grid grid-cols-1 lg:grid-cols-3 gap-8"
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

              <div className="flex flex-col gap-6 h-full overflow-y-auto pr-2 scrollbar-none">
                <div className="glass-card p-8 flex flex-col rounded-3xl border border-white/[0.08]">
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
                      <div className="pt-2">
                        <label className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-3 block">Simulation Backend</label>
                        <div className="grid grid-cols-2 gap-2">
                          {["Python Simulator", "SUMO"].map(b => (
                            <button 
                              key={b}
                              onClick={() => setSimConfig({...simConfig, backend: b})}
                              className={cn(
                                "py-2 rounded-xl text-[10px] font-bold border transition-all",
                                simConfig.backend === b ? "bg-blue-600/10 border-blue-600 text-blue-400" : "bg-white/5 border-white/10 text-slate-500 hover:border-white/20"
                              )}
                            >
                              {b}
                            </button>
                          ))}
                        </div>
                      </div>

                      <ParamGroup label="CV Pipeline">
                        <label className="flex items-center gap-3 cursor-pointer p-4 bg-white/5 rounded-2xl border border-white/10 hover:bg-white/10 transition-colors">
                          <input type="checkbox" checked={simConfig.use_cv}
                            onChange={e => setSimConfig({...simConfig, use_cv: e.target.checked})}
                            className="accent-blue-500 w-4 h-4"
                          />
                          <span className="text-sm text-slate-400">Use Computer Vision</span>
                        </label>
                      </ParamGroup>

                      <ParamGroup label={`Junctions: ${simConfig.n_junctions}`}>
                        <input type="range" min={1} max={3} value={simConfig.n_junctions}
                          onChange={e => setSimConfig({...simConfig, n_junctions: +e.target.value})}
                          className="w-full accent-blue-500"
                        />
                      </ParamGroup>
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
              <div className="lg:col-span-3 min-h-[400px]">
                <GraphPanel history={history} />
              </div>
              
              <div className="lg:col-span-3">
                 <DatasetImport onDatasetImport={() => setDatasetLoaded(true)} />
              </div>
            </motion.div>
          )}

          {activeTab === "ai-decisions" && (
            <motion.div
              key="ai-decisions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="min-h-[650px]"
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
              className="min-h-[650px]"
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
              className="min-h-[650px]"
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
              className="min-h-[650px]"
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
              className="min-h-[650px]"
            >
              <RouteFinder />
            </motion.div>
          )}

          {activeTab === "technique-compare" && (
            <motion.div
              key="technique-compare"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="min-h-[650px]"
            >
              <TechniqueComparison />
            </motion.div>
          )}

          {activeTab === "detection" && (
            <motion.div
              key="detection"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="min-h-[650px] flex flex-col gap-6"
            >
              <div className="glass-card p-8 rounded-3xl border border-white/[0.08]">
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h3 className="text-xl font-bold text-white flex items-center gap-3">
                      <div className="p-2 bg-slate-800 rounded-xl">
                        <Camera className="w-5 h-5 text-blue-400" />
                      </div>
                      AI Vehicle Detection
                    </h3>
                    <p className="text-slate-500 text-xs mt-1">Upload an image to perform real-time vehicle classification and counting.</p>
                  </div>
                  
                  <div className="relative">
                    <input 
                      type="file" 
                      id="image-upload"
                      accept="image/*" 
                      onChange={handleImageUpload}
                      className="hidden" 
                    />
                    <label 
                      htmlFor="image-upload"
                      className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-bold transition-all shadow-xl shadow-blue-600/30 cursor-pointer active:scale-95"
                    >
                      <Upload className="w-4 h-4" />
                      <span>Upload Capture</span>
                    </label>
                  </div>
                </div>

                {detLoading && (
                  <div className="flex flex-col items-center justify-center py-20 bg-slate-900/50 rounded-3xl border border-dashed border-white/10">
                    <Loader2 className="w-10 h-10 text-blue-500 animate-spin mb-4" />
                    <p className="text-slate-400 font-medium animate-pulse">Running YOLOv8 Inference...</p>
                  </div>
                )}

                {!detLoading && !detResult && (
                  <div className="flex flex-col items-center justify-center py-20 bg-slate-900/50 rounded-3xl border border-dashed border-white/10">
                    <Camera className="w-12 h-12 text-slate-700 mb-4" />
                    <p className="text-slate-500 text-sm">Select a traffic camera frame or road image to begin</p>
                  </div>
                )}

                {detResult && !detLoading && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 relative">
                      <div className="absolute top-4 left-4 z-10 px-3 py-1.5 bg-slate-900/80 backdrop-blur-md rounded-lg border border-white/10">
                        <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Annotated Result</p>
                      </div>
                      <img 
                        src={`data:image/jpeg;base64,${detResult.annotated_image}`}
                        className="rounded-3xl w-full border border-white/10 shadow-2xl" 
                        alt="detected" 
                      />
                    </div>

                    <div className="space-y-4">
                      <div className="glass-card p-6 rounded-3xl border border-blue-500/20 bg-blue-500/5">
                        <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">Total Count</p>
                        <div className="flex items-baseline gap-2">
                          <p className="text-5xl font-black text-blue-400">{detResult.total}</p>
                          <p className="text-xs text-slate-500 font-bold uppercase">Objects</p>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        {Object.entries(detResult.counts).map(([type, count]) => (
                          <div key={type} className="flex justify-between items-center p-4 bg-white/5 border border-white/5 rounded-2xl group hover:border-white/10 transition-colors">
                            <div className="flex items-center gap-3">
                              <div className="w-2 h-2 rounded-full bg-blue-500/50 group-hover:bg-blue-400 transition-colors" />
                              <span className="text-sm font-bold capitalize text-slate-400 group-hover:text-slate-200 transition-colors">{type}</span>
                            </div>
                            <span className="text-lg font-black text-white">{count as number}</span>
                          </div>
                        ))}
                      </div>
                      
                      <div className="p-4 bg-emerald-500/5 rounded-2xl border border-emerald-500/10">
                        <p className="text-[10px] text-slate-400 leading-relaxed">
                          <span className="text-emerald-400 font-bold block mb-1">Model: YOLOv8 Nano</span>
                          Pre-trained on COCO dataset. Optimized for real-time edge inference on traffic surveillance streams.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
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
