"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  BarChart3, 
  TrendingUp, 
  Brain, 
  Zap, 
  Target,
  Activity,
  PieChart,
  LineChart,
  CheckCircle,
  XCircle,
  AlertTriangle
} from "lucide-react";
import { cn } from "@/lib/utils";

interface AlgorithmPerformance {
  name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  avgResponseTime: number;
  successRate: number;
  color: string;
}

interface ConfusionMatrix {
  truePositive: number;
  falsePositive: number;
  trueNegative: number;
  falseNegative: number;
}

interface TrafficFlowData {
  time: string;
  volume: number;
  speed: number;
  congestion: number;
  algorithm: string;
}

interface ComparisonMetrics {
  algorithm: string;
  routeOptimal: number;
  timeSaved: number;
  fuelSaved: number;
  userSatisfaction: number;
  errorRate: number;
}

export default function TechniqueComparison() {
  const [selectedAlgorithms, setSelectedAlgorithms] = useState<string[]>(["PPO", "DQN", "A*"]);
  const [activeView, setActiveView] = useState<"performance" | "confusion" | "traffic" | "comparison">("performance");
  const [timeRange, setTimeRange] = useState<"1h" | "24h" | "7d" | "30d">("24h");

  // Simulated algorithm performance data
  const [algorithmPerformance, setAlgorithmPerformance] = useState<AlgorithmPerformance[]>([
    {
      name: "PPO",
      accuracy: 94.2,
      precision: 91.8,
      recall: 89.5,
      f1Score: 90.6,
      avgResponseTime: 12.5,
      successRate: 96.1,
      color: "text-blue-400"
    },
    {
      name: "DQN",
      accuracy: 89.7,
      precision: 87.3,
      recall: 85.2,
      f1Score: 86.2,
      avgResponseTime: 15.8,
      successRate: 92.3,
      color: "text-green-400"
    },
    {
      name: "A*",
      accuracy: 82.4,
      precision: 79.1,
      recall: 81.3,
      f1Score: 80.2,
      avgResponseTime: 8.2,
      successRate: 88.7,
      color: "text-purple-400"
    },
    {
      name: "Dijkstra",
      accuracy: 78.9,
      precision: 76.4,
      recall: 74.8,
      f1Score: 75.6,
      avgResponseTime: 6.5,
      successRate: 85.2,
      color: "text-orange-400"
    }
  ]);

  // Confusion matrix data for each algorithm
  const confusionMatrices: Record<string, ConfusionMatrix> = {
    "PPO": { truePositive: 850, falsePositive: 75, trueNegative: 920, falseNegative: 55 },
    "DQN": { truePositive: 780, falsePositive: 95, trueNegative: 885, falseNegative: 140 },
    "A*": { truePositive: 720, falsePositive: 120, trueNegative: 860, falseNegative: 200 },
    "Dijkstra": { truePositive: 680, falsePositive: 145, trueNegative: 840, falseNegative: 235 }
  };

  // Traffic flow data
  const [trafficFlowData, setTrafficFlowData] = useState<TrafficFlowData[]>([]);

  // Comparison metrics
  const [comparisonMetrics, setComparisonMetrics] = useState<ComparisonMetrics[]>([
    { algorithm: "PPO", routeOptimal: 94.2, timeSaved: 23.5, fuelSaved: 18.7, userSatisfaction: 91.3, errorRate: 3.9 },
    { algorithm: "DQN", routeOptimal: 89.7, timeSaved: 18.2, fuelSaved: 15.3, userSatisfaction: 87.6, errorRate: 7.7 },
    { algorithm: "A*", routeOptimal: 82.4, timeSaved: 12.8, fuelSaved: 11.2, userSatisfaction: 82.1, errorRate: 11.3 },
    { algorithm: "Dijkstra", routeOptimal: 78.9, timeSaved: 8.5, fuelSaved: 7.8, userSatisfaction: 78.4, errorRate: 14.8 }
  ]);

  useEffect(() => {
    // Generate simulated traffic flow data
    const generateTrafficData = () => {
      const data: TrafficFlowData[] = [];
      const now = new Date();
      
      for (let i = 0; i < 24; i++) {
        const time = new Date(now.getTime() - (23 - i) * 3600000);
        selectedAlgorithms.forEach(algo => {
          data.push({
            time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            volume: 50 + Math.random() * 150,
            speed: 20 + Math.random() * 40,
            congestion: Math.random() * 100,
            algorithm: algo
          });
        });
      }
      
      setTrafficFlowData(data);
    };

    generateTrafficData();
  }, [selectedAlgorithms]);

  const renderConfusionMatrix = (matrix: ConfusionMatrix, algorithm: string) => {
    const total = matrix.truePositive + matrix.falsePositive + matrix.trueNegative + matrix.falseNegative;
    
    return (
      <div className="bg-white/5 rounded-xl p-4 border border-white/10">
        <h4 className="text-white font-bold mb-3">{algorithm} Confusion Matrix</h4>
        
        <div className="grid grid-cols-3 gap-2 mb-4">
          <div></div>
          <div className="text-center text-[10px] text-slate-400 font-bold">Predicted: Yes</div>
          <div className="text-center text-[10px] text-slate-400 font-bold">Predicted: No</div>
          
          <div className="text-[10px] text-slate-400 font-bold">Actual: Yes</div>
          <div className="bg-emerald-500/20 border border-emerald-500/30 rounded p-2 text-center">
            <div className="text-emerald-400 font-bold">{matrix.truePositive}</div>
            <div className="text-[8px] text-slate-400">TP</div>
          </div>
          <div className="bg-red-500/20 border border-red-500/30 rounded p-2 text-center">
            <div className="text-red-400 font-bold">{matrix.falseNegative}</div>
            <div className="text-[8px] text-slate-400">FN</div>
          </div>
          
          <div className="text-[10px] text-slate-400 font-bold">Actual: No</div>
          <div className="bg-orange-500/20 border border-orange-500/30 rounded p-2 text-center">
            <div className="text-orange-400 font-bold">{matrix.falsePositive}</div>
            <div className="text-[8px] text-slate-400">FP</div>
          </div>
          <div className="bg-blue-500/20 border border-blue-500/30 rounded p-2 text-center">
            <div className="text-blue-400 font-bold">{matrix.trueNegative}</div>
            <div className="text-[8px] text-slate-400">TN</div>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-2 text-[10px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Accuracy:</span>
            <span className="text-white font-bold">
              {((matrix.truePositive + matrix.trueNegative) / total * 100).toFixed(1)}%
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Precision:</span>
            <span className="text-white font-bold">
              {(matrix.truePositive / (matrix.truePositive + matrix.falsePositive) * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    );
  };

  const renderTrafficFlowChart = () => {
    const maxVolume = Math.max(...trafficFlowData.map(d => d.volume));
    
    return (
      <div className="bg-white/5 rounded-xl p-4 border border-white/10">
        <h4 className="text-white font-bold mb-3">Traffic Flow Analysis</h4>
        
        <div className="space-y-3">
          {selectedAlgorithms.map(algo => {
            const algoData = trafficFlowData.filter(d => d.algorithm === algo);
            const algoPerf = algorithmPerformance.find(p => p.name === algo);
            
            return (
              <div key={algo} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className={cn("text-sm font-bold", algoPerf?.color)}>{algo}</span>
                  <span className="text-[10px] text-slate-400">
                    Avg Speed: {(algoData.reduce((sum, d) => sum + d.speed, 0) / algoData.length || 0).toFixed(1)} km/h
                  </span>
                </div>
                
                <div className="h-20 flex items-end gap-1">
                  {algoData.slice(0, 20).map((data, index) => (
                    <motion.div
                      key={index}
                      initial={{ height: 0 }}
                      animate={{ height: `${(data.volume / maxVolume) * 100}%` }}
                      transition={{ delay: index * 0.02 }}
                      className={cn(
                        "flex-1 rounded-t-sm min-h-[2px]",
                        data.congestion > 70 ? "bg-red-400" :
                        data.congestion > 40 ? "bg-orange-400" :
                        "bg-emerald-400"
                      )}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
        
        <div className="mt-4 flex items-center gap-4 text-[10px] text-slate-400">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-emerald-400 rounded" />
            <span>Low</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-orange-400 rounded" />
            <span>Medium</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-400 rounded" />
            <span>High</span>
          </div>
        </div>
      </div>
    );
  };

  const renderPerformanceComparison = () => {
    return (
      <div className="space-y-4">
        {algorithmPerformance
          .filter(perf => selectedAlgorithms.includes(perf.name))
          .map((perf, index) => (
          <motion.div
            key={perf.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white/5 rounded-xl p-4 border border-white/10"
          >
            <div className="flex items-center justify-between mb-3">
              <h4 className={cn("font-bold", perf.color)}>{perf.name}</h4>
              <div className="flex items-center gap-2">
                {perf.successRate > 90 ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                ) : perf.successRate > 80 ? (
                  <AlertTriangle className="w-4 h-4 text-orange-400" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-400" />
                )}
                <span className="text-[10px] text-slate-400">{perf.successRate}% success</span>
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-[10px] text-slate-500 mb-1">Accuracy</div>
                <div className="text-lg font-bold text-white">{perf.accuracy}%</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500 mb-1">F1 Score</div>
                <div className="text-lg font-bold text-white">{perf.f1Score}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500 mb-1">Response Time</div>
                <div className="text-lg font-bold text-white">{perf.avgResponseTime}ms</div>
              </div>
            </div>
            
            <div className="mt-3 space-y-2">
              <div className="flex justify-between text-[10px]">
                <span className="text-slate-400">Precision</span>
                <span className="text-white">{perf.precision}%</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-400 to-purple-400"
                  style={{ width: `${perf.precision}%` }}
                />
              </div>
              
              <div className="flex justify-between text-[10px]">
                <span className="text-slate-400">Recall</span>
                <span className="text-white">{perf.recall}%</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-400 to-cyan-400"
                  style={{ width: `${perf.recall}%` }}
                />
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    );
  };

  const renderComparisonMetrics = () => {
    return (
      <div className="space-y-4">
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <h4 className="text-white font-bold mb-3">Route Optimization Comparison</h4>
          
          <div className="space-y-3">
            {comparisonMetrics
              .filter(metric => selectedAlgorithms.includes(metric.algorithm))
              .map((metric, index) => (
              <div key={metric.algorithm} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-bold text-white">{metric.algorithm}</span>
                  <span className="text-[10px] text-emerald-400">
                    {metric.routeOptimal}% optimal routes
                  </span>
                </div>
                
                <div className="grid grid-cols-4 gap-2 text-[10px]">
                  <div className="text-center">
                    <div className="text-white font-bold">{metric.timeSaved}min</div>
                    <div className="text-slate-400">Time Saved</div>
                  </div>
                  <div className="text-center">
                    <div className="text-white font-bold">{metric.fuelSaved}%</div>
                    <div className="text-slate-400">Fuel Saved</div>
                  </div>
                  <div className="text-center">
                    <div className="text-white font-bold">{metric.userSatisfaction}%</div>
                    <div className="text-slate-400">Satisfaction</div>
                  </div>
                  <div className="text-center">
                    <div className="text-white font-bold">{metric.errorRate}%</div>
                    <div className="text-slate-400">Error Rate</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <h4 className="text-white font-bold mb-3">Performance Summary</h4>
          
          <div className="space-y-3">
            <div className="flex justify-between text-[10px]">
              <span className="text-slate-400">Best Algorithm (Overall)</span>
              <span className="text-emerald-400 font-bold">PPO</span>
            </div>
            <div className="flex justify-between text-[10px]">
              <span className="text-slate-400">Fastest Response</span>
              <span className="text-blue-400 font-bold">Dijkstra (6.5ms)</span>
            </div>
            <div className="flex justify-between text-[10px]">
              <span className="text-slate-400">Most Accurate</span>
              <span className="text-purple-400 font-bold">PPO (94.2%)</span>
            </div>
            <div className="flex justify-between text-[10px]">
              <span className="text-slate-400">Best Time Savings</span>
              <span className="text-green-400 font-bold">PPO (23.5min)</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-500/10 rounded-xl border border-purple-500/20">
            <BarChart3 className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Technique Comparison</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              Algorithm Performance Analysis
            </p>
          </div>
        </div>
        
        <div className="flex gap-2">
          {["performance", "confusion", "traffic", "comparison"].map((view) => (
            <button
              key={view}
              onClick={() => setActiveView(view as any)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all",
                activeView === view
                  ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                  : "bg-white/5 text-slate-400 border border-transparent"
              )}
            >
              {view}
            </button>
          ))}
        </div>
      </div>

      {/* Algorithm Selection */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Brain className="w-4 h-4 text-slate-400" />
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
            Select Algorithms
          </span>
        </div>
        
        <div className="flex gap-2 flex-wrap">
          {["PPO", "DQN", "A*", "Dijkstra"].map((algo) => (
            <button
              key={algo}
              onClick={() => {
                setSelectedAlgorithms(prev => 
                  prev.includes(algo) 
                    ? prev.filter(a => a !== algo)
                    : [...prev, algo]
                );
              }}
              className={cn(
                "px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                selectedAlgorithms.includes(algo)
                  ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                  : "bg-white/5 text-slate-400 border border-white/10"
              )}
            >
              {algo}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">
          {activeView === "performance" && (
            <motion.div
              key="performance"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {renderPerformanceComparison()}
            </motion.div>
          )}

          {activeView === "confusion" && (
            <motion.div
              key="confusion"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              {selectedAlgorithms.map(algo => 
                renderConfusionMatrix(confusionMatrices[algo], algo)
              )}
            </motion.div>
          )}

          {activeView === "traffic" && (
            <motion.div
              key="traffic"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {renderTrafficFlowChart()}
            </motion.div>
          )}

          {activeView === "comparison" && (
            <motion.div
              key="comparison"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {renderComparisonMetrics()}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
