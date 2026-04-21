"use client";

import React, { useState, useEffect } from "react";
import DashboardShell from "@/components/DashboardShell";
import { useAuth } from "@/hooks/useAuth";
import { motion, AnimatePresence } from "framer-motion";
import DatasetManager from "@/components/DatasetManager";
import TechniqueSimulator from "@/components/TechniqueSimulator";
import PerformanceComparison from "@/components/PerformanceComparison";

export default function DatasetsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<"datasets" | "simulation" | "comparison">("datasets");

  if (authLoading) return null;
  if (!isAuthenticated) return null;

  const tabs = [
    { id: "datasets", label: "Dataset Manager", icon: "database" },
    { id: "simulation", label: "Technique Simulator", icon: "play" },
    { id: "comparison", label: "Performance Analysis", icon: "chart" }
  ];

  return (
    <DashboardShell>
      <div className="flex flex-col gap-8">
        {/* Header */}
        <section className="flex items-end justify-between">
          <div>
            <h2 className="text-3xl font-bold text-white tracking-tight">Dataset Management</h2>
            <p className="text-slate-400 mt-1">Upload datasets and compare routing techniques to demonstrate algorithm superiority</p>
          </div>
        </section>

        {/* Tab Navigation */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium text-sm transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                  : "bg-white/5 text-slate-400 hover:bg-white/10 border border-transparent"
              }`}
            >
              <span className="text-lg">{tab.icon === "database" ? "Database" : tab.icon === "play" ? "Play" : "Chart"}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === "datasets" && (
            <motion.div
              key="datasets"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-[600px]"
            >
              <DatasetManager />
            </motion.div>
          )}

          {activeTab === "simulation" && (
            <motion.div
              key="simulation"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-[600px]"
            >
              <TechniqueSimulator />
            </motion.div>
          )}

          {activeTab === "comparison" && (
            <motion.div
              key="comparison"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-[600px]"
            >
              <PerformanceComparison />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </DashboardShell>
  );
}
