"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  History, 
  BarChart3, 
  Settings, 
  LogOut, 
  TrafficCone,
  Zap,
  Database
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

const menuItems = [
  { name: "Live Dashboard", icon: LayoutDashboard, href: "/" },
  { name: "Simulation History", icon: History, href: "/history" },
  { name: "Research Analytics", icon: BarChart3, href: "/research" },
  { name: "Dataset Management", icon: Database, href: "/datasets" },
  { name: "AI Settings", icon: Settings, href: "/settings" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 h-screen glass border-r border-white/5 flex flex-col p-4 z-50">
      <div className="flex items-center gap-3 px-2 mb-10 mt-2">
        <div className="p-2 bg-blue-500/20 rounded-xl">
          <TrafficCone className="w-6 h-6 text-blue-400" />
        </div>
        <div>
          <h1 className="font-bold text-lg tracking-tight text-white">Mangalore</h1>
          <p className="text-[10px] uppercase tracking-[0.2em] text-blue-400/80 font-semibold -mt-1">Traffic AI</p>
        </div>
      </div>

      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link key={item.name} href={item.href}>
              <div
                className={cn(
                  "relative flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group overflow-hidden",
                  isActive 
                    ? "text-blue-400" 
                    : "text-slate-400 hover:text-white hover:bg-white/5"
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="active-pill"
                    className="absolute inset-0 bg-blue-500/10 border-l-2 border-blue-500"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <Icon className={cn("w-5 h-5 z-10", isActive && "text-blue-400")} />
                <span className="font-medium text-sm z-10">{item.name}</span>
                
                {!isActive && (
                  <div className="absolute right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Zap className="w-3 h-3 text-blue-400" />
                  </div>
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto pt-6 border-t border-white/5">
        <button className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/5 transition-all">
          <LogOut className="w-5 h-5" />
          <span className="font-medium text-sm">Sign Out</span>
        </button>
      </div>
    </div>
  );
}
