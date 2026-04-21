"use client";

import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, Clock } from "lucide-react";

interface LogEntry {
  id: string;
  time: string;
  message: string;
  type: "action" | "info" | "warning";
}

interface ActionLogProps {
  logs: LogEntry[];
}

export default function ActionLog({ logs }: ActionLogProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="glass-card flex-1 flex flex-col overflow-hidden min-h-[300px]">
      <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          AI Decision Stream
        </h3>
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1">
          <Clock className="w-3 h-3" />
          Real-time
        </span>
      </div>

      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 custom-scrollbar space-y-3"
      >
        <AnimatePresence initial={false}>
          {logs.length === 0 ? (
            <div className="h-full flex items-center justify-center text-slate-600 text-xs italic">
              Waiting for simulation data...
            </div>
          ) : (
            logs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex gap-3 text-[11px] group"
              >
                <span className="text-slate-600 font-mono mt-0.5 shrink-0 select-none">
                  {log.time}
                </span>
                <div className="flex-1">
                  <span className="text-slate-300 leading-relaxed group-hover:text-white transition-colors">
                    {log.message}
                  </span>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
      
      <div className="p-3 bg-white/[0.01] border-t border-white/5 text-center">
        <p className="text-[9px] text-slate-500 font-medium uppercase tracking-tighter">
          Synchronized with Mangalore RL Inference Engine
        </p>
      </div>
    </div>
  );
}
