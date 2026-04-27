"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { TrafficCone, Lock, User, ArrowRight, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg("");

    try {
      await login(formData.username, formData.password);
    } catch (err: any) {
      setErrorMsg("Invalid username or password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6 bg-slate-950 relative overflow-hidden">
      {/* Background Decals */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-blue-600/5 blur-[120px] rounded-full" />
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-purple-600/5 blur-[120px] rounded-full" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md glass-card p-8 md:p-12 relative z-10"
      >
        <div className="text-center mb-10">
          <div className="inline-flex p-3 bg-blue-500/10 rounded-2xl mb-6">
            <TrafficCone className="w-8 h-8 text-blue-400" />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Traffic Control</h1>
          <p className="text-slate-400 mt-2 text-sm">Sign in to manage Mangalore's smart traffic grid.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-slate-500 ml-1">Username</label>
            <div className="relative group">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
              <input
                type="text" required
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3.5 pl-12 pr-4 text-white outline-none focus:border-blue-500 focus:bg-white/[0.08] transition-all"
                placeholder="Enter your username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-bold uppercase tracking-widest text-slate-500 ml-1">Password</label>
              <Link href="/forgot-password" size="sm" className="text-[10px] text-blue-400 hover:underline">
                Forgot password?
              </Link>
            </div>
            <div className="relative group">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
              <input
                type="password" required
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3.5 pl-12 pr-4 text-white outline-none focus:border-blue-500 focus:bg-white/[0.08] transition-all"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </div>
          </div>

          {errorMsg && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-500 text-xs font-medium">
              {errorMsg}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-xl shadow-blue-600/20"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <><span>Sign In</span><ArrowRight className="w-4 h-4" /></>}
          </button>
        </form>

        <div className="mt-8 pt-8 border-t border-white/5 text-center">
          <p className="text-sm text-slate-500">
            Don't have access? <Link href="/register" className="text-blue-400 hover:underline">Create Account</Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
