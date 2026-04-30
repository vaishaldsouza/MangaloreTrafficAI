"use client";
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid
} from "recharts";
import { SimStep } from "@/hooks/useSimulation";

const TIP_STYLE = {
  contentStyle: { background: "#1e293b", border: "none", borderRadius: 12, fontSize: 11 },
  labelStyle: { color: "#94a3b8" }
};

export default function GraphPanel({ history }: { history: SimStep[] }) {
  if (history.length < 2) return (
    <div className="flex items-center justify-center h-64 text-slate-600 text-sm">
      Run simulation to see graphs
    </div>
  );

  // Downsample for performance
  const sample = history.filter((_, i) => i % Math.max(1, Math.floor(history.length / 80)) === 0);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">

      {/* Queue over time */}
      <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
        <p className="text-xs font-black uppercase tracking-widest text-slate-500 mb-4">Queue Length Over Time</p>
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={sample}>
            <defs>
              <linearGradient id="qGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" />
            <XAxis dataKey="step" tick={{ fill: "#64748b", fontSize: 9 }} />
            <YAxis tick={{ fill: "#64748b", fontSize: 9 }} />
            <Tooltip {...TIP_STYLE} />
            <Area type="monotone" dataKey="total_queue" stroke="#3b82f6"
              fill="url(#qGrad)" strokeWidth={2} dot={false} name="Queue" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Reward over time */}
      <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
        <p className="text-xs font-black uppercase tracking-widest text-slate-500 mb-4">Reward Signal Over Time</p>
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={sample}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" />
            <XAxis dataKey="step" tick={{ fill: "#64748b", fontSize: 9 }} />
            <YAxis tick={{ fill: "#64748b", fontSize: 9 }} />
            <Tooltip {...TIP_STYLE} />
            <Line type="monotone" dataKey="reward" stroke="#10b981"
              strokeWidth={2} dot={false} name="Reward" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* CO2 over time */}
      <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
        <p className="text-xs font-black uppercase tracking-widest text-slate-500 mb-4">CO₂ Emissions (mg/step)</p>
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={sample}>
            <defs>
              <linearGradient id="co2Grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#f97316" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" />
            <XAxis dataKey="step" tick={{ fill: "#64748b", fontSize: 9 }} />
            <YAxis tick={{ fill: "#64748b", fontSize: 9 }} />
            <Tooltip {...TIP_STYLE} />
            <Area type="monotone" dataKey="co2_mg" stroke="#f97316"
              fill="url(#co2Grad)" strokeWidth={2} dot={false} name="CO₂ mg" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Congestion state distribution */}
      <div className="glass-card p-6 rounded-3xl border border-white/[0.08]">
        <p className="text-xs font-black uppercase tracking-widest text-slate-500 mb-4">Congestion State Distribution</p>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={(() => {
            const counts: Record<string, number> = {};
            history.forEach(h => { counts[h.congestion] = (counts[h.congestion]||0) + 1; });
            return Object.entries(counts).map(([state, count]) => ({ state, count }));
          })()}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" />
            <XAxis dataKey="state" tick={{ fill: "#64748b", fontSize: 9 }} />
            <YAxis tick={{ fill: "#64748b", fontSize: 9 }} />
            <Tooltip {...TIP_STYLE} />
            <Bar dataKey="count" fill="#8b5cf6" radius={[6,6,0,0]} name="Steps" />
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
}
