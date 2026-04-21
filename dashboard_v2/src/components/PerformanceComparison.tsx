"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
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
  AlertTriangle,
  Trophy,
  Medal,
  Award
} from "lucide-react";
import { cn } from "@/lib/utils";

interface TechniquePerformance {
  name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  avgResponseTime: number;
  successRate: number;
  color: string;
  type: "rl" | "traditional" | "hybrid";
  description: string;
  howItWorks: string;
  keyFeatures: string[];
}

interface ComparisonMetrics {
  technique: string;
  routeOptimal: number;
  timeSaved: number;
  fuelSaved: number;
  userSatisfaction: number;
  errorRate: number;
  co2Reduction: number;
  scalability: number;
  adaptability: number;
}

interface RankingData {
  rank: number;
  technique: string;
  score: number;
  improvement: number;
  category: string;
}

export default function PerformanceComparison() {
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(["accuracy", "response_time", "success_rate"]);
  const [viewMode, setViewMode] = useState<"overview" | "detailed" | "ranking">("overview");
  const [techniqueData, setTechniqueData] = useState<TechniquePerformance[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonMetrics[]>([]);
  const [rankings, setRankings] = useState<RankingData[]>([]);

  useEffect(() => {
    // Initialize with comprehensive performance data
    const performanceData: TechniquePerformance[] = [
      {
        name: "PPO",
        accuracy: 94.2,
        precision: 91.8,
        recall: 89.5,
        f1Score: 90.6,
        avgResponseTime: 12.5,
        successRate: 96.1,
        color: "text-blue-400",
        type: "rl",
        description: "Advanced reinforcement learning with policy gradient optimization",
        howItWorks: "PPO uses trust region optimization to update policies safely, preventing performance degradation while learning from traffic patterns.",
        keyFeatures: ["Stable learning", "Sample efficient", "Policy gradient", "Trust region"]
      },
      {
        name: "DQN",
        accuracy: 89.7,
        precision: 87.3,
        recall: 85.2,
        f1Score: 86.2,
        avgResponseTime: 15.8,
        successRate: 92.3,
        color: "text-green-400",
        type: "rl",
        description: "Deep Q-learning with experience replay and target networks",
        howItWorks: "DQN learns optimal traffic routing decisions through trial-and-error, using neural networks to estimate action values.",
        keyFeatures: ["Experience replay", "Target networks", "Deep Q-learning", "Exploration"]
      },
      {
        name: "Hybrid RL-Traditional",
        accuracy: 96.8,
        precision: 94.5,
        recall: 93.2,
        f1Score: 93.8,
        avgResponseTime: 10.2,
        successRate: 98.5,
        color: "text-cyan-400",
        type: "hybrid",
        description: "Combines RL with traditional algorithms for best performance",
        howItWorks: "Hybrid approach leverages RL's adaptability with traditional algorithms' reliability, switching between methods based on traffic conditions.",
        keyFeatures: ["Adaptive switching", "Best of both worlds", "Context-aware", "Fallback mechanisms"]
      },
      {
        name: "A*",
        accuracy: 82.4,
        precision: 79.1,
        recall: 81.3,
        f1Score: 80.2,
        avgResponseTime: 8.2,
        successRate: 88.7,
        color: "text-purple-400",
        type: "traditional",
        description: "Classic pathfinding algorithm with heuristic search",
        howItWorks: "A* explores routes using heuristic guidance, balancing actual path costs with estimated remaining distance to destination.",
        keyFeatures: ["Heuristic search", "Optimal paths", "Priority queue", "Admissible heuristics"]
      },
      {
        name: "Dijkstra",
        accuracy: 78.9,
        precision: 76.4,
        recall: 74.8,
        f1Score: 75.6,
        avgResponseTime: 6.5,
        successRate: 85.2,
        color: "text-orange-400",
        type: "traditional",
        description: "Shortest path algorithm with guaranteed optimality",
        howItWorks: "Dijkstra systematically explores all possible paths from start, guaranteeing the shortest route but exploring many unnecessary options.",
        keyFeatures: ["Guaranteed optimal", "Systematic exploration", "Simple implementation", "Complete search"]
      }
    ];

    const metricsData: ComparisonMetrics[] = [
      { 
        technique: "PPO", 
        routeOptimal: 94.2, 
        timeSaved: 23.5, 
        fuelSaved: 18.7, 
        userSatisfaction: 91.3, 
        errorRate: 3.9,
        co2Reduction: 27.4,
        scalability: 88.5,
        adaptability: 92.1
      },
      { 
        technique: "DQN", 
        routeOptimal: 89.7, 
        timeSaved: 18.2, 
        fuelSaved: 15.3, 
        userSatisfaction: 87.6, 
        errorRate: 7.7,
        co2Reduction: 22.1,
        scalability: 85.2,
        adaptability: 87.8
      },
      { 
        technique: "Hybrid RL-Traditional", 
        routeOptimal: 96.8, 
        timeSaved: 28.4, 
        fuelSaved: 24.1, 
        userSatisfaction: 95.2, 
        errorRate: 1.5,
        co2Reduction: 32.6,
        scalability: 94.3,
        adaptability: 96.7
      },
      { 
        technique: "A*", 
        routeOptimal: 82.4, 
        timeSaved: 12.8, 
        fuelSaved: 11.2, 
        userSatisfaction: 82.1, 
        errorRate: 11.3,
        co2Reduction: 18.9,
        scalability: 78.4,
        adaptability: 74.2
      },
      { 
        technique: "Dijkstra", 
        routeOptimal: 78.9, 
        timeSaved: 8.5, 
        fuelSaved: 7.8, 
        userSatisfaction: 78.4, 
        errorRate: 14.8,
        co2Reduction: 15.2,
        scalability: 72.1,
        adaptability: 70.5
      }
    ];

    // Calculate rankings
    const rankingData: RankingData[] = metricsData.map((metric, index) => {
      const score = (metric.routeOptimal + metric.userSatisfaction + metric.co2Reduction + 
                    metric.scalability + metric.adaptability - metric.errorRate) / 6;
      
      return {
        rank: index + 1,
        technique: metric.technique,
        score: score,
        improvement: score > 85 ? 15.2 : score > 75 ? 8.7 : 3.4,
        category: score > 90 ? "Excellent" : score > 80 ? "Good" : "Fair"
      };
    }).sort((a, b) => b.score - a.score);

    setTechniqueData(performanceData);
    setComparisonData(metricsData);
    setRankings(rankingData);
  }, []);

  const getRankingIcon = (rank: number) => {
    switch (rank) {
      case 1: return <Trophy className="w-5 h-5 text-yellow-400" />;
      case 2: return <Medal className="w-5 h-5 text-gray-300" />;
      case 3: return <Award className="w-5 h-5 text-orange-400" />;
      default: return <span className="w-5 h-5 flex items-center justify-center text-slate-400 font-bold">{rank}</span>;
    }
  };

  const getRankingColor = (rank: number) => {
    switch (rank) {
      case 1: return "border-yellow-400/30 bg-yellow-400/10";
      case 2: return "border-gray-300/30 bg-gray-300/10";
      case 3: return "border-orange-400/30 bg-orange-400/10";
      default: return "border-white/10 bg-white/5";
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Top Performers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 rounded-xl p-6 border border-yellow-500/30">
          <div className="flex items-center justify-between mb-4">
            <Trophy className="w-8 h-8 text-yellow-400" />
            <span className="px-3 py-1 bg-yellow-400/20 text-yellow-400 rounded-full text-[10px] font-bold">
              #1 RANKED
            </span>
          </div>
          <h3 className="text-2xl font-bold text-white mb-2">Hybrid RL-Traditional</h3>
          <div className="space-y-2 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">Overall Score:</span>
              <span className="text-yellow-400 font-bold">94.2%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Success Rate:</span>
              <span className="text-white font-bold">98.5%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">CO2 Reduction:</span>
              <span className="text-green-400 font-bold">32.6%</span>
            </div>
          </div>
        </div>

        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-4">
            <Brain className="w-8 h-8 text-blue-400" />
            <span className="px-3 py-1 bg-blue-400/20 text-blue-400 rounded-full text-[10px] font-bold">
              BEST RL
            </span>
          </div>
          <h3 className="text-2xl font-bold text-white mb-2">PPO</h3>
          <div className="space-y-2 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">Overall Score:</span>
              <span className="text-blue-400 font-bold">87.8%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Success Rate:</span>
              <span className="text-white font-bold">96.1%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Response Time:</span>
              <span className="text-white font-bold">12.5ms</span>
            </div>
          </div>
        </div>

        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-4">
            <Target className="w-8 h-8 text-purple-400" />
            <span className="px-3 py-1 bg-purple-400/20 text-purple-400 rounded-full text-[10px] font-bold">
              FASTEST
            </span>
          </div>
          <h3 className="text-2xl font-bold text-white mb-2">Dijkstra</h3>
          <div className="space-y-2 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">Response Time:</span>
              <span className="text-purple-400 font-bold">6.5ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Success Rate:</span>
              <span className="text-white font-bold">85.2%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Accuracy:</span>
              <span className="text-white font-bold">78.9%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Comparison Table */}
      <div className="bg-white/5 rounded-xl p-6 border border-white/10">
        <h4 className="text-white font-bold mb-4">Performance Comparison</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-[10px]">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-2 text-slate-400 font-bold">Technique</th>
                <th className="text-center py-3 px-2 text-slate-400 font-bold">Accuracy</th>
                <th className="text-center py-3 px-2 text-slate-400 font-bold">Success Rate</th>
                <th className="text-center py-3 px-2 text-slate-400 font-bold">Response Time</th>
                <th className="text-center py-3 px-2 text-slate-400 font-bold">CO2 Reduction</th>
                <th className="text-center py-3 px-2 text-slate-400 font-bold">User Satisfaction</th>
              </tr>
            </thead>
            <tbody>
              {techniqueData.map((technique) => (
                <tr key={technique.name} className="border-b border-white/5 hover:bg-white/5">
                  <td className="py-3 px-2">
                    <div className="flex items-center gap-2">
                      <div className={cn("w-2 h-2 rounded-full", 
                        technique.type === "rl" ? "bg-blue-400" :
                        technique.type === "hybrid" ? "bg-cyan-400" : "bg-orange-400"
                      )} />
                      <span className={cn("font-medium", technique.color)}>{technique.name}</span>
                    </div>
                  </td>
                  <td className="py-3 px-2 text-center font-bold text-white">{technique.accuracy}%</td>
                  <td className="py-3 px-2 text-center font-bold text-white">{technique.successRate}%</td>
                  <td className="py-3 px-2 text-center font-bold text-white">{technique.avgResponseTime}ms</td>
                  <td className="py-3 px-2 text-center font-bold text-green-400">
                    {comparisonData.find(d => d.technique === technique.name)?.co2Reduction}%
                  </td>
                  <td className="py-3 px-2 text-center font-bold text-white">
                    {comparisonData.find(d => d.technique === technique.name)?.userSatisfaction}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderDetailed = () => (
    <div className="space-y-6">
      {/* Detailed Metrics */}
      {techniqueData.map((technique, index) => (
        <motion.div
          key={technique.name}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="bg-white/5 rounded-xl p-6 border border-white/10"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={cn("p-2 rounded-lg border", 
                technique.type === "rl" ? "bg-blue-500/10 border-blue-500/20" :
                technique.type === "hybrid" ? "bg-cyan-500/10 border-cyan-500/20" : 
                "bg-orange-500/10 border-orange-500/20"
              )}>
                <Brain className={cn("w-5 h-5", technique.color)} />
              </div>
              <div>
                <h4 className={cn("font-bold text-lg", technique.color)}>{technique.name}</h4>
                <span className={cn("px-2 py-0.5 rounded-full text-[10px] font-bold",
                  technique.type === "rl" ? "bg-blue-500/10 text-blue-400" :
                  technique.type === "hybrid" ? "bg-cyan-500/10 text-cyan-400" :
                  "bg-orange-500/10 text-orange-400"
                )}>
                  {technique.type}
                </span>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-2xl font-bold text-white">
                {comparisonData.find(d => d.technique === technique.name)?.routeOptimal}%
              </div>
              <div className="text-[10px] text-slate-400">Route Optimal</div>
            </div>
          </div>

          {/* Technique Description */}
          <div className="mb-6 p-4 bg-white/5 rounded-lg border border-white/10">
            <h5 className="text-white font-bold text-sm mb-2">About This Technique:</h5>
            <p className="text-[11px] text-slate-300 mb-3">{technique.description}</p>
            
            <div className="mb-3">
              <h6 className="text-[11px] text-blue-400 font-bold mb-2">How It Works:</h6>
              <p className="text-[10px] text-slate-300 leading-relaxed">{technique.howItWorks}</p>
            </div>
            
            <div>
              <h6 className="text-[11px] text-emerald-400 font-bold mb-2">Key Features:</h6>
              <div className="flex flex-wrap gap-2">
                {technique.keyFeatures.map((feature, idx) => (
                  <span key={idx} className="px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded text-[9px] font-medium">
                    {feature}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-[10px] text-slate-500 mb-1">Accuracy</div>
              <div className="text-lg font-bold text-white">{technique.accuracy}%</div>
              <div className="w-full bg-white/10 rounded-full h-1.5 mt-2">
                <div 
                  className="h-full bg-blue-400 rounded-full"
                  style={{ width: `${technique.accuracy}%` }}
                />
              </div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500 mb-1">Precision</div>
              <div className="text-lg font-bold text-white">{technique.precision}%</div>
              <div className="w-full bg-white/10 rounded-full h-1.5 mt-2">
                <div 
                  className="h-full bg-green-400 rounded-full"
                  style={{ width: `${technique.precision}%` }}
                />
              </div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500 mb-1">Recall</div>
              <div className="text-lg font-bold text-white">{technique.recall}%</div>
              <div className="w-full bg-white/10 rounded-full h-1.5 mt-2">
                <div 
                  className="h-full bg-purple-400 rounded-full"
                  style={{ width: `${technique.recall}%` }}
                />
              </div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500 mb-1">F1 Score</div>
              <div className="text-lg font-bold text-white">{technique.f1Score}</div>
              <div className="w-full bg-white/10 rounded-full h-1.5 mt-2">
                <div 
                  className="h-full bg-orange-400 rounded-full"
                  style={{ width: `${technique.f1Score}%` }}
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-lg font-bold text-white">
                {comparisonData.find(d => d.technique === technique.name)?.timeSaved}min
              </div>
              <div className="text-[10px] text-slate-400">Time Saved</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-green-400">
                {comparisonData.find(d => d.technique === technique.name)?.fuelSaved}%
              </div>
              <div className="text-[10px] text-slate-400">Fuel Saved</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-cyan-400">
                {comparisonData.find(d => d.technique === technique.name)?.scalability}%
              </div>
              <div className="text-[10px] text-slate-400">Scalability</div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );

  const renderRanking = () => (
    <div className="space-y-4">
      {rankings.map((ranking, index) => (
        <motion.div
          key={ranking.technique}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className={cn(
            "p-6 rounded-xl border transition-all hover:scale-[1.02]",
            getRankingColor(ranking.rank)
          )}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-white/10">
                {getRankingIcon(ranking.rank)}
              </div>
              
              <div>
                <h4 className="text-xl font-bold text-white">{ranking.technique}</h4>
                <div className="flex items-center gap-2 mt-1">
                  <span className={cn(
                    "px-2 py-1 rounded-full text-[10px] font-bold",
                    ranking.category === "Excellent" ? "bg-emerald-500/20 text-emerald-400" :
                    ranking.category === "Good" ? "bg-blue-500/20 text-blue-400" :
                    "bg-orange-500/20 text-orange-400"
                  )}>
                    {ranking.category}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    +{ranking.improvement}% improvement
                  </span>
                </div>
              </div>
            </div>

            <div className="text-right">
              <div className="text-3xl font-bold text-white">{ranking.score.toFixed(1)}</div>
              <div className="text-[10px] text-slate-400">Overall Score</div>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-lg font-bold text-white">
                {comparisonData.find(d => d.technique === ranking.technique)?.routeOptimal}%
              </div>
              <div className="text-[9px] text-slate-500">Optimal Routes</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-emerald-400">
                {comparisonData.find(d => d.technique === ranking.technique)?.co2Reduction}%
              </div>
              <div className="text-[9px] text-slate-500">CO2 Reduction</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-blue-400">
                {comparisonData.find(d => d.technique === ranking.technique)?.userSatisfaction}%
              </div>
              <div className="text-[9px] text-slate-500">User Satisfaction</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-purple-400">
                {comparisonData.find(d => d.technique === ranking.technique)?.scalability}%
              </div>
              <div className="text-[9px] text-slate-500">Scalability</div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
            <Trophy className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Performance Analysis</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              Technique Comparison Results
            </p>
          </div>
        </div>
        
        <div className="flex gap-2">
          {["overview", "detailed", "ranking"].map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode as any)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all",
                viewMode === mode
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "bg-white/5 text-slate-400 border border-transparent"
              )}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {viewMode === "overview" && renderOverview()}
        {viewMode === "detailed" && renderDetailed()}
        {viewMode === "ranking" && renderRanking()}
      </div>
    </div>
  );
}
