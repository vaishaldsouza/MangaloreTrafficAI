"use client";

import React, { useState } from "react";
import DashboardShell from "@/components/DashboardShell";
import { useAuth } from "@/hooks/useAuth";
import { motion } from "framer-motion";
import { 
  Brain, 
  Settings, 
  Save, 
  RotateCcw,
  Zap,
  Activity,
  Wind,
  FileText,
  Database,
  Bell,
  Shield,
  Cpu,
  Globe,
  Network,
  AlertTriangle,
  CheckCircle,
  X
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ModelConfig {
  algorithm: "PPO" | "DQN" | "A3C" | "SAC";
  modelPath: string;
  learningRate: number;
  batchSize: number;
  episodes: number;
  gamma: number;
  epsilon: number;
  targetUpdateInterval: number;
  bufferSize: number;
}

interface SimulationConfig {
  timeStep: number;
  maxSteps: number;
  vehicleSpawnRate: number;
  trafficDensity: "low" | "medium" | "high" | "dynamic";
  weatherConditions: "clear" | "rain" | "fog" | "storm";
  emergencyFrequency: number;
  signalUpdateInterval: number;
}

interface EnvironmentalConfig {
  co2Monitoring: boolean;
  noxMonitoring: boolean;
  pm25Monitoring: boolean;
  fuelConsumptionTracking: boolean;
  emissionTargets: {
    co2: number;
    nox: number;
    pm25: number;
  };
  reportingInterval: "hourly" | "daily" | "weekly";
  researchHubSync: boolean;
}

interface BenchmarkingConfig {
  autoGenerateWeekly: boolean;
  autoGenerateMonthly: boolean;
  comparisonAlgorithms: string[];
  metrics: string[];
  exportFormat: "pdf" | "csv" | "json";
  emailReports: boolean;
}

interface NotificationConfig {
  highCongestionAlerts: boolean;
  modelFailureAlerts: boolean;
  emissionThresholdAlerts: boolean;
  systemHealthAlerts: boolean;
  emailNotifications: boolean;
  smsNotifications: boolean;
  webhookUrl: string;
}

export default function SettingsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [activeSection, setActiveSection] = useState("model");
  const [hasChanges, setHasChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");

  // Model Configuration
  const [modelConfig, setModelConfig] = useState<ModelConfig>({
    algorithm: "PPO",
    modelPath: "/models/ppo_mangalore_sumo.zip",
    learningRate: 0.0003,
    batchSize: 64,
    episodes: 1000,
    gamma: 0.99,
    epsilon: 0.1,
    targetUpdateInterval: 10,
    bufferSize: 100000
  });

  // Simulation Configuration
  const [simulationConfig, setSimulationConfig] = useState<SimulationConfig>({
    timeStep: 1.0,
    maxSteps: 500,
    vehicleSpawnRate: 0.1,
    trafficDensity: "dynamic",
    weatherConditions: "clear",
    emergencyFrequency: 0.05,
    signalUpdateInterval: 5
  });

  // Environmental Configuration
  const [environmentalConfig, setEnvironmentalConfig] = useState<EnvironmentalConfig>({
    co2Monitoring: true,
    noxMonitoring: true,
    pm25Monitoring: false,
    fuelConsumptionTracking: true,
    emissionTargets: {
      co2: 200,
      nox: 40,
      pm25: 25
    },
    reportingInterval: "daily",
    researchHubSync: true
  });

  // Benchmarking Configuration
  const [benchmarkingConfig, setBenchmarkingConfig] = useState<BenchmarkingConfig>({
    autoGenerateWeekly: true,
    autoGenerateMonthly: true,
    comparisonAlgorithms: ["DQN RL Model", "Actuated signals", "Fixed-cycle baseline"],
    metrics: ["avg_queue", "avg_waiting_time", "throughput", "co2_reduction"],
    exportFormat: "pdf",
    emailReports: true
  });

  // Notification Configuration
  const [notificationConfig, setNotificationConfig] = useState<NotificationConfig>({
    highCongestionAlerts: true,
    modelFailureAlerts: true,
    emissionThresholdAlerts: true,
    systemHealthAlerts: false,
    emailNotifications: true,
    smsNotifications: false,
    webhookUrl: ""
  });

  const sections = [
    { id: "model", label: "AI Model", icon: Brain },
    { id: "simulation", label: "Simulation", icon: Activity },
    { id: "environmental", label: "Environmental", icon: Wind },
    { id: "benchmarking", label: "Benchmarking", icon: FileText },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "data", label: "Data Sources", icon: Database }
  ];

  const handleSave = async () => {
    setSaveStatus("saving");
    setHasChanges(false);
    
    // Simulate API call
    setTimeout(() => {
      setSaveStatus("saved");
      setTimeout(() => setSaveStatus("idle"), 2000);
    }, 1500);
  };

  const handleReset = () => {
    setModelConfig({
      algorithm: "PPO",
      modelPath: "/models/ppo_mangalore_sumo.zip",
      learningRate: 0.0003,
      batchSize: 64,
      episodes: 1000,
      gamma: 0.99,
      epsilon: 0.1,
      targetUpdateInterval: 10,
      bufferSize: 100000
    });
    setHasChanges(false);
  };

  if (authLoading) return null;
  if (!isAuthenticated) return null;

  return (
    <DashboardShell>
      <div className="flex flex-col gap-8">
        {/* Header */}
        <section className="flex items-end justify-between">
          <div>
            <h2 className="text-3xl font-bold text-white tracking-tight">AI Settings</h2>
            <p className="text-slate-400 mt-1">Configure machine learning models, simulation parameters, and system preferences.</p>
          </div>
          
          <div className="flex gap-3">
            <button 
              onClick={handleReset}
              className="flex items-center gap-2 px-5 py-2.5 bg-white/5 hover:bg-white/10 text-white rounded-xl font-semibold transition-all border border-white/10"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset</span>
            </button>
            <button 
              onClick={handleSave}
              disabled={!hasChanges || saveStatus === "saving"}
              className={cn(
                "flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold transition-all border",
                saveStatus === "saving" ? "bg-blue-500/20 text-blue-400 border-blue-500/30 cursor-not-allowed" :
                saveStatus === "saved" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" :
                hasChanges ? "bg-blue-600 hover:bg-blue-500 text-white border-blue-600/20 shadow-lg shadow-blue-600/20" :
                "bg-white/5 text-white/50 border-white/10 cursor-not-allowed"
              )}
            >
              {saveStatus === "saving" ? (
                <>
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  <span>Saving...</span>
                </>
              ) : saveStatus === "saved" ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>Saved</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Save Changes</span>
                </>
              )}
            </button>
          </div>
        </section>

        {/* Navigation */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {sections.map((section) => {
            const Icon = section.icon;
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-xl font-medium text-sm transition-all whitespace-nowrap",
                  activeSection === section.id
                    ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                    : "bg-white/5 text-slate-400 hover:bg-white/10 border border-transparent"
                )}
              >
                <Icon className="w-4 h-4" />
                {section.label}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <motion.div
          key={activeSection}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-8"
        >
          {/* AI Model Configuration */}
          {activeSection === "model" && (
            <div className="space-y-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-purple-500/10 rounded-xl border border-purple-500/20">
                  <Brain className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">AI Model Configuration</h3>
                  <p className="text-slate-400 text-sm">Configure reinforcement learning algorithms and parameters</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Algorithm</label>
                    <select 
                      value={modelConfig.algorithm}
                      onChange={(e) => {
                        setModelConfig(prev => ({ ...prev, algorithm: e.target.value as any }));
                        setHasChanges(true);
                      }}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                    >
                      <option value="PPO">Proximal Policy Optimization (PPO)</option>
                      <option value="DQN">Deep Q-Network (DQN)</option>
                      <option value="A3C">Asynchronous Actor-Critic (A3C)</option>
                      <option value="SAC">Soft Actor-Critic (SAC)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Model Path</label>
                    <input 
                      type="text"
                      value={modelConfig.modelPath}
                      onChange={(e) => {
                        setModelConfig(prev => ({ ...prev, modelPath: e.target.value }));
                        setHasChanges(true);
                      }}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Learning Rate: {modelConfig.learningRate}
                    </label>
                    <input 
                      type="range"
                      min="0.0001"
                      max="0.01"
                      step="0.0001"
                      value={modelConfig.learningRate}
                      onChange={(e) => {
                        setModelConfig(prev => ({ ...prev, learningRate: parseFloat(e.target.value) }));
                        setHasChanges(true);
                      }}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Batch Size</label>
                    <input 
                      type="number"
                      value={modelConfig.batchSize}
                      onChange={(e) => {
                        setModelConfig(prev => ({ ...prev, batchSize: parseInt(e.target.value) }));
                        setHasChanges(true);
                      }}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                    />
                  </div>
                </div>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Training Episodes</label>
                    <input 
                      type="number"
                      value={modelConfig.episodes}
                      onChange={(e) => {
                        setModelConfig(prev => ({ ...prev, episodes: parseInt(e.target.value) }));
                        setHasChanges(true);
                      }}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Discount Factor (Gamma): {modelConfig.gamma}
                    </label>
                    <input 
                      type="range"
                      min="0.9"
                      max="0.999"
                      step="0.001"
                      value={modelConfig.gamma}
                      onChange={(e) => {
                        setModelConfig(prev => ({ ...prev, gamma: parseFloat(e.target.value) }));
                        setHasChanges(true);
                      }}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Exploration Rate (Epsilon): {modelConfig.epsilon}
                    </label>
                    <input 
                      type="range"
                      min="0"
                      max="0.5"
                      step="0.01"
                      value={modelConfig.epsilon}
                      onChange={(e) => {
                        setModelConfig(prev => ({ ...prev, epsilon: parseFloat(e.target.value) }));
                        setHasChanges(true);
                      }}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Buffer Size</label>
                    <input 
                      type="number"
                      value={modelConfig.bufferSize}
                      onChange={(e) => {
                        setModelConfig(prev => ({ ...prev, bufferSize: parseInt(e.target.value) }));
                        setHasChanges(true);
                      }}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Simulation Configuration */}
          {activeSection === "simulation" && (
            <div className="space-y-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-blue-500/10 rounded-xl border border-blue-500/20">
                  <Activity className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Simulation Parameters</h3>
                  <p className="text-slate-400 text-sm">Configure traffic simulation and environment settings</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Time Step (seconds): {simulationConfig.timeStep}
                    </label>
                    <input 
                      type="range"
                      min="0.1"
                      max="5"
                      step="0.1"
                      value={simulationConfig.timeStep}
                      onChange={(e) => {
                        setSimulationConfig(prev => ({ ...prev, timeStep: parseFloat(e.target.value) }));
                        setHasChanges(true);
                      }}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Max Steps</label>
                    <input 
                      type="number"
                      value={simulationConfig.maxSteps}
                      onChange={(e) => {
                        setSimulationConfig(prev => ({ ...prev, maxSteps: parseInt(e.target.value) }));
                        setHasChanges(true);
                      }}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Vehicle Spawn Rate: {simulationConfig.vehicleSpawnRate}
                    </label>
                    <input 
                      type="range"
                      min="0.01"
                      max="0.5"
                      step="0.01"
                      value={simulationConfig.vehicleSpawnRate}
                      onChange={(e) => {
                        setSimulationConfig(prev => ({ ...prev, vehicleSpawnRate: parseFloat(e.target.value) }));
                        setHasChanges(true);
                      }}
                      className="w-full"
                    />
                  </div>
                </div>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Traffic Density</label>
                    <select 
                      value={simulationConfig.trafficDensity}
                      onChange={(e) => {
                        setSimulationConfig(prev => ({ ...prev, trafficDensity: e.target.value as any }));
                        setHasChanges(true);
                      }}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                    >
                      <option value="low">Low Traffic</option>
                      <option value="medium">Medium Traffic</option>
                      <option value="high">High Traffic</option>
                      <option value="dynamic">Dynamic (Real-time)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Weather Conditions</label>
                    <select 
                      value={simulationConfig.weatherConditions}
                      onChange={(e) => {
                        setSimulationConfig(prev => ({ ...prev, weatherConditions: e.target.value as any }));
                        setHasChanges(true);
                      }}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                    >
                      <option value="clear">Clear</option>
                      <option value="rain">Rain</option>
                      <option value="fog">Fog</option>
                      <option value="storm">Storm</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Emergency Frequency: {(simulationConfig.emergencyFrequency * 100).toFixed(1)}%
                    </label>
                    <input 
                      type="range"
                      min="0"
                      max="0.2"
                      step="0.01"
                      value={simulationConfig.emergencyFrequency}
                      onChange={(e) => {
                        setSimulationConfig(prev => ({ ...prev, emergencyFrequency: parseFloat(e.target.value) }));
                        setHasChanges(true);
                      }}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Environmental Configuration */}
          {activeSection === "environmental" && (
            <div className="space-y-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-green-500/10 rounded-xl border border-green-500/20">
                  <Wind className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Environmental Monitoring</h3>
                  <p className="text-slate-400 text-sm">Configure emission tracking and environmental metrics</p>
                </div>
              </div>

              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-3">
                      <Wind className="w-5 h-5 text-slate-400" />
                      <span className="text-white font-medium">CO2 Monitoring</span>
                    </div>
                    <button
                      onClick={() => {
                        setEnvironmentalConfig(prev => ({ ...prev, co2Monitoring: !prev.co2Monitoring }));
                        setHasChanges(true);
                      }}
                      className={cn(
                        "w-12 h-6 rounded-full transition-colors",
                        environmentalConfig.co2Monitoring ? "bg-emerald-500" : "bg-slate-600"
                      )}
                    >
                      <div className={cn(
                        "w-5 h-5 bg-white rounded-full transition-transform",
                        environmentalConfig.co2Monitoring ? "translate-x-6" : "translate-x-0.5"
                      )} />
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-3">
                      <Globe className="w-5 h-5 text-slate-400" />
                      <span className="text-white font-medium">NOx Monitoring</span>
                    </div>
                    <button
                      onClick={() => {
                        setEnvironmentalConfig(prev => ({ ...prev, noxMonitoring: !prev.noxMonitoring }));
                        setHasChanges(true);
                      }}
                      className={cn(
                        "w-12 h-6 rounded-full transition-colors",
                        environmentalConfig.noxMonitoring ? "bg-emerald-500" : "bg-slate-600"
                      )}
                    >
                      <div className={cn(
                        "w-5 h-5 bg-white rounded-full transition-transform",
                        environmentalConfig.noxMonitoring ? "translate-x-6" : "translate-x-0.5"
                      )} />
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-3">
                      <Activity className="w-5 h-5 text-slate-400" />
                      <span className="text-white font-medium">PM2.5 Monitoring</span>
                    </div>
                    <button
                      onClick={() => {
                        setEnvironmentalConfig(prev => ({ ...prev, pm25Monitoring: !prev.pm25Monitoring }));
                        setHasChanges(true);
                      }}
                      className={cn(
                        "w-12 h-6 rounded-full transition-colors",
                        environmentalConfig.pm25Monitoring ? "bg-emerald-500" : "bg-slate-600"
                      )}
                    >
                      <div className={cn(
                        "w-5 h-5 bg-white rounded-full transition-transform",
                        environmentalConfig.pm25Monitoring ? "translate-x-6" : "translate-x-0.5"
                      )} />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-white">Emission Targets (ppm)</h4>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">CO2 Target</label>
                      <input 
                        type="number"
                        value={environmentalConfig.emissionTargets.co2}
                        onChange={(e) => {
                          setEnvironmentalConfig(prev => ({ 
                            ...prev, 
                            emissionTargets: { ...prev.emissionTargets, co2: parseInt(e.target.value) }
                          }));
                          setHasChanges(true);
                        }}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">NOx Target</label>
                      <input 
                        type="number"
                        value={environmentalConfig.emissionTargets.nox}
                        onChange={(e) => {
                          setEnvironmentalConfig(prev => ({ 
                            ...prev, 
                            emissionTargets: { ...prev.emissionTargets, nox: parseInt(e.target.value) }
                          }));
                          setHasChanges(true);
                        }}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">PM2.5 Target</label>
                      <input 
                        type="number"
                        value={environmentalConfig.emissionTargets.pm25}
                        onChange={(e) => {
                          setEnvironmentalConfig(prev => ({ 
                            ...prev, 
                            emissionTargets: { ...prev.emissionTargets, pm25: parseInt(e.target.value) }
                          }));
                          setHasChanges(true);
                        }}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                      />
                    </div>
                  </div>

                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-white">Reporting Settings</h4>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Reporting Interval</label>
                      <select 
                        value={environmentalConfig.reportingInterval}
                        onChange={(e) => {
                          setEnvironmentalConfig(prev => ({ ...prev, reportingInterval: e.target.value as any }));
                          setHasChanges(true);
                        }}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                      >
                        <option value="hourly">Hourly</option>
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                      </select>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center gap-3">
                        <Database className="w-5 h-5 text-slate-400" />
                        <span className="text-white font-medium">Research Hub Sync</span>
                      </div>
                      <button
                        onClick={() => {
                          setEnvironmentalConfig(prev => ({ ...prev, researchHubSync: !prev.researchHubSync }));
                          setHasChanges(true);
                        }}
                        className={cn(
                          "w-12 h-6 rounded-full transition-colors",
                          environmentalConfig.researchHubSync ? "bg-emerald-500" : "bg-slate-600"
                        )}
                      >
                        <div className={cn(
                          "w-5 h-5 bg-white rounded-full transition-transform",
                          environmentalConfig.researchHubSync ? "translate-x-6" : "translate-x-0.5"
                        )} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Benchmarking Configuration */}
          {activeSection === "benchmarking" && (
            <div className="space-y-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-violet-500/10 rounded-xl border border-violet-500/20">
                  <FileText className="w-5 h-5 text-violet-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Benchmarking & Reports</h3>
                  <p className="text-slate-400 text-sm">Configure automatic report generation and academic benchmarking</p>
                </div>
              </div>

              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-slate-400" />
                      <span className="text-white font-medium">Auto-generate Weekly Reports</span>
                    </div>
                    <button
                      onClick={() => {
                        setBenchmarkingConfig(prev => ({ ...prev, autoGenerateWeekly: !prev.autoGenerateWeekly }));
                        setHasChanges(true);
                      }}
                      className={cn(
                        "w-12 h-6 rounded-full transition-colors",
                        benchmarkingConfig.autoGenerateWeekly ? "bg-emerald-500" : "bg-slate-600"
                      )}
                    >
                      <div className={cn(
                        "w-5 h-5 bg-white rounded-full transition-transform",
                        benchmarkingConfig.autoGenerateWeekly ? "translate-x-6" : "translate-x-0.5"
                      )} />
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-slate-400" />
                      <span className="text-white font-medium">Auto-generate Monthly Reports</span>
                    </div>
                    <button
                      onClick={() => {
                        setBenchmarkingConfig(prev => ({ ...prev, autoGenerateMonthly: !prev.autoGenerateMonthly }));
                        setHasChanges(true);
                      }}
                      className={cn(
                        "w-12 h-6 rounded-full transition-colors",
                        benchmarkingConfig.autoGenerateMonthly ? "bg-emerald-500" : "bg-slate-600"
                      )}
                    >
                      <div className={cn(
                        "w-5 h-5 bg-white rounded-full transition-transform",
                        benchmarkingConfig.autoGenerateMonthly ? "translate-x-6" : "translate-x-0.5"
                      )} />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-white">Comparison Algorithms</h4>
                    <div className="space-y-3">
                      {["DQN RL Model", "Actuated signals", "Fixed-cycle baseline"].map((algo) => (
                        <div key={algo} className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10">
                          <span className="text-white text-sm">{algo}</span>
                          <button
                            onClick={() => {
                              const newAlgos = benchmarkingConfig.comparisonAlgorithms.includes(algo)
                                ? benchmarkingConfig.comparisonAlgorithms.filter(a => a !== algo)
                                : [...benchmarkingConfig.comparisonAlgorithms, algo];
                              setBenchmarkingConfig(prev => ({ ...prev, comparisonAlgorithms: newAlgos }));
                              setHasChanges(true);
                            }}
                            className={cn(
                              "w-10 h-5 rounded-full transition-colors",
                              benchmarkingConfig.comparisonAlgorithms.includes(algo) ? "bg-emerald-500" : "bg-slate-600"
                            )}
                          >
                            <div className={cn(
                              "w-4 h-4 bg-white rounded-full transition-transform",
                              benchmarkingConfig.comparisonAlgorithms.includes(algo) ? "translate-x-5" : "translate-x-0.5"
                            )} />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-white">Export Settings</h4>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Export Format</label>
                      <select 
                        value={benchmarkingConfig.exportFormat}
                        onChange={(e) => {
                          setBenchmarkingConfig(prev => ({ ...prev, exportFormat: e.target.value as any }));
                          setHasChanges(true);
                        }}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                      >
                        <option value="pdf">PDF</option>
                        <option value="csv">CSV</option>
                        <option value="json">JSON</option>
                      </select>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center gap-3">
                        <Bell className="w-5 h-5 text-slate-400" />
                        <span className="text-white font-medium">Email Reports</span>
                      </div>
                      <button
                        onClick={() => {
                          setBenchmarkingConfig(prev => ({ ...prev, emailReports: !prev.emailReports }));
                          setHasChanges(true);
                        }}
                        className={cn(
                          "w-12 h-6 rounded-full transition-colors",
                          benchmarkingConfig.emailReports ? "bg-emerald-500" : "bg-slate-600"
                        )}
                      >
                        <div className={cn(
                          "w-5 h-5 bg-white rounded-full transition-transform",
                          benchmarkingConfig.emailReports ? "translate-x-6" : "translate-x-0.5"
                        )} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Notification Configuration */}
          {activeSection === "notifications" && (
            <div className="space-y-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-orange-500/10 rounded-xl border border-orange-500/20">
                  <Bell className="w-5 h-5 text-orange-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Notifications & Alerts</h3>
                  <p className="text-slate-400 text-sm">Configure system alerts and notification preferences</p>
                </div>
              </div>

              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {[
                    { key: "highCongestionAlerts", label: "High Congestion Alerts", icon: AlertTriangle },
                    { key: "modelFailureAlerts", label: "Model Failure Alerts", icon: Brain },
                    { key: "emissionThresholdAlerts", label: "Emission Threshold Alerts", icon: Wind },
                    { key: "systemHealthAlerts", label: "System Health Alerts", icon: Shield }
                  ].map(({ key, label, icon: Icon }) => (
                    <div key={key} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center gap-3">
                        <Icon className="w-5 h-5 text-slate-400" />
                        <span className="text-white font-medium">{label}</span>
                      </div>
                      <button
                        onClick={() => {
                          setNotificationConfig(prev => ({ ...prev, [key]: !prev[key as keyof NotificationConfig] }));
                          setHasChanges(true);
                        }}
                        className={cn(
                          "w-12 h-6 rounded-full transition-colors",
                          notificationConfig[key as keyof NotificationConfig] ? "bg-emerald-500" : "bg-slate-600"
                        )}
                      >
                        <div className={cn(
                          "w-5 h-5 bg-white rounded-full transition-transform",
                          notificationConfig[key as keyof NotificationConfig] ? "translate-x-6" : "translate-x-0.5"
                        )} />
                      </button>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-white">Notification Channels</h4>
                    
                    <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center gap-3">
                        <Bell className="w-5 h-5 text-slate-400" />
                        <span className="text-white font-medium">Email Notifications</span>
                      </div>
                      <button
                        onClick={() => {
                          setNotificationConfig(prev => ({ ...prev, emailNotifications: !prev.emailNotifications }));
                          setHasChanges(true);
                        }}
                        className={cn(
                          "w-12 h-6 rounded-full transition-colors",
                          notificationConfig.emailNotifications ? "bg-emerald-500" : "bg-slate-600"
                        )}
                      >
                        <div className={cn(
                          "w-5 h-5 bg-white rounded-full transition-transform",
                          notificationConfig.emailNotifications ? "translate-x-6" : "translate-x-0.5"
                        )} />
                      </button>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center gap-3">
                        <Bell className="w-5 h-5 text-slate-400" />
                        <span className="text-white font-medium">SMS Notifications</span>
                      </div>
                      <button
                        onClick={() => {
                          setNotificationConfig(prev => ({ ...prev, smsNotifications: !prev.smsNotifications }));
                          setHasChanges(true);
                        }}
                        className={cn(
                          "w-12 h-6 rounded-full transition-colors",
                          notificationConfig.smsNotifications ? "bg-emerald-500" : "bg-slate-600"
                        )}
                      >
                        <div className={cn(
                          "w-5 h-5 bg-white rounded-full transition-transform",
                          notificationConfig.smsNotifications ? "translate-x-6" : "translate-x-0.5"
                        )} />
                      </button>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-white">Webhook Configuration</h4>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Webhook URL</label>
                      <input 
                        type="url"
                        value={notificationConfig.webhookUrl}
                        onChange={(e) => {
                          setNotificationConfig(prev => ({ ...prev, webhookUrl: e.target.value }));
                          setHasChanges(true);
                        }}
                        placeholder="https://your-webhook-url.com"
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-blue-500 transition-all"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Data Sources Configuration */}
          {activeSection === "data" && (
            <div className="space-y-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-cyan-500/10 rounded-xl border border-cyan-500/20">
                  <Database className="w-5 h-5 text-cyan-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Data Sources & Integration</h3>
                  <p className="text-slate-400 text-sm">Configure real-time data sources and external integrations</p>
                </div>
              </div>

              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-white">Traffic Data Sources</h4>
                    
                    <div className="space-y-4">
                      <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <Network className="w-5 h-5 text-slate-400" />
                            <span className="text-white font-medium">SUMO Simulation</span>
                          </div>
                          <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase rounded-full">Active</span>
                        </div>
                        <div className="text-[11px] text-slate-400 space-y-1">
                          <p>Connection: localhost:8000</p>
                          <p>Update Rate: Real-time</p>
                          <p>Status: Connected</p>
                        </div>
                      </div>

                      <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <Globe className="w-5 h-5 text-slate-400" />
                            <span className="text-white font-medium">OpenStreetMap</span>
                          </div>
                          <span className="px-2 py-1 bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase rounded-full">Static</span>
                        </div>
                        <div className="text-[11px] text-slate-400 space-y-1">
                          <p>Region: Mangalore, India</p>
                          <p>Last Update: 2024-01-15</p>
                          <p>Status: Cached</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-white">Environmental Sensors</h4>
                    
                    <div className="space-y-4">
                      <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <Wind className="w-5 h-5 text-slate-400" />
                            <span className="text-white font-medium">Air Quality Monitor</span>
                          </div>
                          <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase rounded-full">Active</span>
                        </div>
                        <div className="text-[11px] text-slate-400 space-y-1">
                          <p>Location: Hampankatta Junction</p>
                          <p>Sensors: CO2, NOx, PM2.5</p>
                          <p>Update Rate: 5 minutes</p>
                        </div>
                      </div>

                      <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <Activity className="w-5 h-5 text-slate-400" />
                            <span className="text-white font-medium">Traffic Flow Sensors</span>
                          </div>
                          <span className="px-2 py-1 bg-orange-500/10 text-orange-400 text-[10px] font-bold uppercase rounded-full">Limited</span>
                        </div>
                        <div className="text-[11px] text-slate-400 space-y-1">
                          <p>Coverage: 4/12 intersections</p>
                          <p>Data Type: Vehicle counts, speed</p>
                          <p>Status: Partial deployment</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-orange-500/10 rounded-xl border border-orange-500/20">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-orange-400 shrink-0 mt-0.5" />
                    <div className="text-[11px] text-orange-400/80">
                      <p className="font-bold mb-1">Data Integration Notice</p>
                      <p>Some data sources are in testing phase. Full integration expected by Q2 2024. Contact system administrator for priority access.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </DashboardShell>
  );
}
