"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Brain, 
  Zap, 
  Target,
  Activity,
  BarChart3,
  Settings,
  CheckCircle,
  AlertTriangle,
  TrendingUp
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Technique {
  id: string;
  name: string;
  type: "rl" | "traditional" | "hybrid";
  description: string;
  howItWorks: string;
  advantages: string[];
  limitations: string[];
  parameters: Record<string, any>;
  color: string;
  icon: React.ReactNode;
}

interface SimulationResult {
  technique: string;
  avgTime: number;
  successRate: number;
  fuelEfficiency: number;
  congestionReduction: number;
  userSatisfaction: number;
  co2Reduction: number;
  iterations: number;
}

export default function TechniqueSimulator() {
  const [selectedTechniques, setSelectedTechniques] = useState<string[]>(["PPO", "DQN", "A*"]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationProgress, setSimulationProgress] = useState(0);
  const [results, setResults] = useState<SimulationResult[]>([]);
  const [iterations, setIterations] = useState(1000);
  const [dataset, setDataset] = useState<string>("mangalore_traffic_2024");
  const [expandedTechnique, setExpandedTechnique] = useState<string | null>(null);

  const techniques: Technique[] = [
    {
      id: "PPO",
      name: "PPO (Proximal Policy Optimization)",
      type: "rl",
      description: "Advanced reinforcement learning with policy gradient optimization",
      howItWorks: "PPO uses a trust region method to update policies, preventing large policy updates that could degrade performance. It collects trajectories and performs multiple epochs of minibatch updates on collected data.",
      advantages: ["Stable learning", "Sample efficient", "Easy to implement", "Handles continuous/discrete actions"],
      limitations: ["Requires careful tuning", "Can be computationally expensive", "May converge slowly"],
      parameters: { learningRate: 0.0003, gamma: 0.99, epsilon: 0.1 },
      color: "text-blue-400",
      icon: <Brain className="w-5 h-5" />
    },
    {
      id: "DQN",
      name: "DQN (Deep Q-Network)",
      type: "rl",
      description: "Deep Q-learning with experience replay and target networks",
      howItWorks: "DQN uses a neural network to approximate Q-values, learning optimal actions through trial-and-error. Experience replay breaks correlations and target networks stabilize training.",
      advantages: ["Handles high-dimensional spaces", "Experience replay", "Target network stability"],
      limitations: ["Can overestimate Q-values", "Sample inefficient", "Requires large replay buffer"],
      parameters: { learningRate: 0.001, gamma: 0.95, epsilon: 0.2 },
      color: "text-green-400",
      icon: <Zap className="w-5 h-5" />
    },
    {
      id: "A*",
      name: "A* Algorithm",
      type: "traditional",
      description: "Classic pathfinding algorithm with heuristic search",
      howItWorks: "A* combines Dijkstra's algorithm with heuristic guidance. It maintains a priority queue of nodes to explore, using f(n) = g(n) + h(n) where g is actual cost and h is estimated cost to goal.",
      advantages: ["Optimal if heuristic is admissible", "Faster than Dijkstra", "Complete search"],
      limitations: ["Memory intensive", "Performance depends on heuristic quality", "Not adaptive"],
      parameters: { heuristic: "euclidean", weight: 1.0 },
      color: "text-purple-400",
      icon: <Target className="w-5 h-5" />
    },
    {
      id: "Dijkstra",
      name: "Dijkstra's Algorithm",
      type: "traditional",
      description: "Shortest path algorithm with guaranteed optimality",
      howItWorks: "Dijkstra explores all possible paths in order of increasing distance from start. It guarantees finding the shortest path but can be slow as it explores many unnecessary paths.",
      advantages: ["Guaranteed optimal", "Simple to implement", "Works with negative weights"],
      limitations: ["Very slow for large graphs", "Explores unnecessary paths", "No heuristic guidance"],
      parameters: { optimization: "distance" },
      color: "text-orange-400",
      icon: <Activity className="w-5 h-5" />
    },
    {
      id: "Hybrid",
      name: "Hybrid RL-Traditional",
      type: "hybrid",
      description: "Combines RL with traditional algorithms for best performance",
      howItWorks: "Hybrid approach uses RL for learning traffic patterns while traditional algorithms provide baseline solutions. It combines the adaptability of RL with the reliability of traditional methods.",
      advantages: ["Best of both worlds", "Adaptive and reliable", "Handles edge cases well", "Faster convergence"],
      limitations: ["Complex to implement", "Multiple hyperparameters", "Potential conflicts between methods"],
      parameters: { rlWeight: 0.7, traditionalWeight: 0.3 },
      color: "text-cyan-400",
      icon: <BarChart3 className="w-5 h-5" />
    }
  ];

  const runSimulation = async () => {
    if (selectedTechniques.length === 0) return;
    
    setIsSimulating(true);
    setSimulationProgress(0);
    setResults([]);

    // Simulate simulation progress
    const progressInterval = setInterval(() => {
      setSimulationProgress(prev => {
        if (prev >= 95) {
          clearInterval(progressInterval);
          return 95;
        }
        return prev + Math.random() * 10;
      });
    }, 500);

    // Generate results for each selected technique
    setTimeout(() => {
      clearInterval(progressInterval);
      
      const newResults: SimulationResult[] = selectedTechniques.map(techId => {
        const technique = techniques.find(t => t.id === techId)!;
        
        // Simulate different performance based on technique type
        let basePerformance = 0.5;
        if (technique.type === "rl") basePerformance = 0.85;
        else if (technique.type === "hybrid") basePerformance = 0.92;
        else basePerformance = 0.65;

        const variance = Math.random() * 0.2 - 0.1;
        const performance = Math.max(0.3, Math.min(1.0, basePerformance + variance));

        return {
          technique: technique.name,
          avgTime: 15 - performance * 8 + Math.random() * 3,
          successRate: 70 + performance * 25 + Math.random() * 5,
          fuelEfficiency: 60 + performance * 30 + Math.random() * 10,
          congestionReduction: 50 + performance * 40 + Math.random() * 10,
          userSatisfaction: 65 + performance * 30 + Math.random() * 5,
          co2Reduction: 40 + performance * 35 + Math.random() * 15,
          iterations: iterations
        };
      });

      setResults(newResults);
      setSimulationProgress(100);
      
      setTimeout(() => {
        setIsSimulating(false);
      }, 1000);
    }, 3000);
  };

  const resetSimulation = () => {
    setIsSimulating(false);
    setSimulationProgress(0);
    setResults([]);
  };

  const toggleTechnique = (techId: string) => {
    setSelectedTechniques(prev => 
      prev.includes(techId) 
        ? prev.filter(id => id !== techId)
        : [...prev, techId]
    );
  };

  const getBestTechnique = () => {
    if (results.length === 0) return null;
    
    return results.reduce((best, current) => {
      const bestScore = (best.successRate + best.fuelEfficiency + best.congestionReduction + 
                       best.userSatisfaction + best.co2Reduction) / 5;
      const currentScore = (current.successRate + current.fuelEfficiency + current.congestionReduction + 
                          current.userSatisfaction + current.co2Reduction) / 5;
      return currentScore > bestScore ? current : best;
    });
  };

  const bestTechnique = getBestTechnique();

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-500/10 rounded-xl border border-purple-500/20">
            <Brain className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Technique Simulator</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              Compare Routing Algorithms
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={resetSimulation}
            disabled={isSimulating}
            className="p-2 bg-white/5 hover:bg-white/10 disabled:bg-white/5 disabled:opacity-50 rounded-lg transition-all"
          >
            <RotateCcw className="w-4 h-4 text-slate-400" />
          </button>
          <button
            onClick={runSimulation}
            disabled={isSimulating || selectedTechniques.length === 0}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all",
              isSimulating || selectedTechniques.length === 0
                ? "bg-white/5 text-white/50 cursor-not-allowed"
                : "bg-purple-600 hover:bg-purple-500 text-white"
            )}
          >
            {isSimulating ? (
              <>
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                <span>Simulating...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Run Simulation</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Simulation Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Dataset</label>
          <select 
            value={dataset}
            onChange={(e) => setDataset(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-purple-500 transition-all"
          >
            <option value="mangalore_traffic_2024">Mangalore Traffic 2024</option>
            <option value="peak_hours">Peak Hours Dataset</option>
            <option value="weekend_traffic">Weekend Traffic</option>
            <option value="emergency_scenarios">Emergency Scenarios</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Iterations: {iterations.toLocaleString()}
          </label>
          <input 
            type="range"
            min="100"
            max="10000"
            step="100"
            value={iterations}
            onChange={(e) => setIterations(parseInt(e.target.value))}
            className="w-full"
          />
        </div>
      </div>

      {/* Technique Selection */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Settings className="w-4 h-4 text-slate-400" />
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
            Select Techniques ({selectedTechniques.length})
          </span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {techniques.map((technique) => (
            <div key={technique.id} className="space-y-2">
              <button
                onClick={() => toggleTechnique(technique.id)}
                className={cn(
                  "w-full p-4 rounded-xl border transition-all text-left",
                  selectedTechniques.includes(technique.id)
                    ? "bg-purple-500/10 border-purple-500/30"
                    : "bg-white/5 border-white/10 hover:bg-white/10"
                )}
              >
                <div className="flex items-start gap-3">
                  <div className={cn(
                    "p-2 rounded-lg border",
                    selectedTechniques.includes(technique.id)
                      ? "bg-purple-500/20 border-purple-500/30"
                      : "bg-white/10 border-white/20"
                  )}>
                    <div className={selectedTechniques.includes(technique.id) ? technique.color : "text-slate-400"}>
                      {technique.icon}
                    </div>
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h4 className={cn(
                      "font-bold text-sm mb-1",
                      selectedTechniques.includes(technique.id) ? "text-white" : "text-slate-400"
                    )}>
                      {technique.name}
                    </h4>
                    <p className="text-[10px] text-slate-500 line-clamp-2">
                      {technique.description}
                    </p>
                    <div className="mt-2">
                      <span className={cn(
                        "px-2 py-0.5 rounded-full text-[8px] font-bold",
                        technique.type === "rl" ? "bg-blue-500/10 text-blue-400" :
                        technique.type === "hybrid" ? "bg-cyan-500/10 text-cyan-400" :
                        "bg-orange-500/10 text-orange-400"
                      )}>
                        {technique.type}
                      </span>
                    </div>
                  </div>
                </div>
              </button>
              
              {/* Expandable technique info */}
              <button
                onClick={() => setExpandedTechnique(expandedTechnique === technique.id ? null : technique.id)}
                className="w-full p-3 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 text-left transition-all"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-slate-400 font-medium">How it works</span>
                  <span className="text-[8px] text-slate-500">
                    {expandedTechnique === technique.id ? "Hide" : "Show"}
                  </span>
                </div>
              </button>
              
              {expandedTechnique === technique.id && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="p-4 bg-white/5 rounded-lg border border-white/10 space-y-3"
                >
                  <div>
                    <h5 className="text-[11px] text-white font-bold mb-2">How It Works:</h5>
                    <p className="text-[10px] text-slate-300 leading-relaxed">
                      {technique.howItWorks}
                    </p>
                  </div>
                  
                  <div>
                    <h5 className="text-[11px] text-emerald-400 font-bold mb-2">Advantages:</h5>
                    <ul className="space-y-1">
                      {technique.advantages.map((advantage, index) => (
                        <li key={index} className="text-[10px] text-slate-300 flex items-start gap-2">
                          <span className="text-emerald-400 mt-0.5">+</span>
                          <span>{advantage}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h5 className="text-[11px] text-orange-400 font-bold mb-2">Limitations:</h5>
                    <ul className="space-y-1">
                      {technique.limitations.map((limitation, index) => (
                        <li key={index} className="text-[10px] text-slate-300 flex items-start gap-2">
                          <span className="text-orange-400 mt-0.5">-</span>
                          <span>{limitation}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Simulation Progress */}
      <AnimatePresence>
        {isSimulating && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-6"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] text-slate-400">Running simulation...</span>
              <span className="text-[10px] text-purple-400">{simulationProgress.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${simulationProgress}%` }}
                className="h-full bg-gradient-to-r from-purple-400 to-pink-400"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <AnimatePresence mode="wait">
          {results.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1 flex items-center justify-center"
            >
              <div className="text-center">
                <div className="w-16 h-16 bg-slate-800/50 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/5">
                  <Brain className="w-8 h-8 text-slate-600" />
                </div>
                <h3 className="text-xl font-bold text-white">No Simulation Results</h3>
                <p className="text-slate-400 text-sm mt-2">Select techniques and run simulation to compare performance</p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex-1 overflow-y-auto space-y-4"
            >
              {/* Best Technique Highlight */}
              {bestTechnique && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="p-4 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-xl border border-purple-500/30"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                    <h4 className="text-white font-bold">Best Performing Technique</h4>
                  </div>
                  <div className="text-2xl font-bold text-white mb-2">{bestTechnique.technique}</div>
                  <div className="grid grid-cols-3 gap-4 text-[10px]">
                    <div>
                      <span className="text-slate-400">Success Rate:</span>
                      <span className="text-emerald-400 font-bold ml-1">{bestTechnique.successRate.toFixed(1)}%</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Avg Time:</span>
                      <span className="text-blue-400 font-bold ml-1">{bestTechnique.avgTime.toFixed(1)}s</span>
                    </div>
                    <div>
                      <span className="text-slate-400">CO2 Reduction:</span>
                      <span className="text-green-400 font-bold ml-1">{bestTechnique.co2Reduction.toFixed(1)}%</span>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Detailed Results */}
              {results.map((result, index) => (
                <motion.div
                  key={result.technique}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={cn(
                    "p-4 rounded-xl border",
                    bestTechnique?.technique === result.technique
                      ? "bg-emerald-500/10 border-emerald-500/30"
                      : "bg-white/5 border-white/10"
                  )}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-white font-bold">{result.technique}</h4>
                    {bestTechnique?.technique === result.technique && (
                      <div className="flex items-center gap-1 px-2 py-1 bg-emerald-500/20 rounded-full">
                        <CheckCircle className="w-3 h-3 text-emerald-400" />
                        <span className="text-[10px] text-emerald-400 font-bold">BEST</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-lg font-bold text-white">{result.avgTime.toFixed(1)}s</div>
                      <div className="text-[9px] text-slate-500">Avg Time</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-white">{result.successRate.toFixed(1)}%</div>
                      <div className="text-[9px] text-slate-500">Success Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-white">{result.fuelEfficiency.toFixed(1)}%</div>
                      <div className="text-[9px] text-slate-500">Fuel Efficiency</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-white">{result.congestionReduction.toFixed(1)}%</div>
                      <div className="text-[9px] text-slate-500">Congestion Reduction</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-white">{result.userSatisfaction.toFixed(1)}%</div>
                      <div className="text-[9px] text-slate-500">User Satisfaction</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-white">{result.co2Reduction.toFixed(1)}%</div>
                      <div className="text-[9px] text-slate-500">CO2 Reduction</div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
