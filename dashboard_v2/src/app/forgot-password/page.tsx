"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { TrafficCone, User, Lock, Key, ArrowRight, Loader2, CheckCircle2, ChevronLeft } from "lucide-react";
import Link from "next/link";

export default function ForgotPasswordPage() {
  const [step, setStep] = useState<1 | 2>(1);
  const [formData, setFormData] = useState({ username: "", token: "", newPassword: "" });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  const handleRequestToken = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: formData.username })
      });
      const data = await res.json();
      setMessage(data.message);
      // In this demo environment, we show the token for ease of use
      if (data.debug_token) {
        console.log("DEMO TOKEN:", data.debug_token);
        setFormData({ ...formData, token: data.debug_token });
      }
      setStep(2);
    } catch (err) {
      setMessage("Failed to request reset. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: formData.token,
          new_password: formData.newPassword
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      
      setIsSuccess(true);
    } catch (err: any) {
      setMessage(err.message || "Reset failed. Invalid token?");
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-950 p-6">
        <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="text-center">
          <CheckCircle2 className="w-16 h-16 text-emerald-400 mx-auto mb-6" />
          <h1 className="text-3xl font-bold text-white mb-2">Password Reset!</h1>
          <p className="text-slate-400 mb-8">You can now login with your new credentials.</p>
          <Link href="/login" className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-xl font-bold transition-all shadow-lg shadow-blue-600/20">
            Back to Login
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6 bg-slate-950 relative overflow-hidden">
      <div className="absolute bottom-1/4 left-1/4 w-[500px] h-[500px] bg-purple-600/5 blur-[120px] rounded-full" />
      
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md glass-card p-8 md:p-12 relative z-10">
        <div className="mb-8">
          <Link href="/login" className="flex items-center gap-2 text-slate-500 hover:text-white transition-colors text-sm mb-6 w-fit">
            <ChevronLeft className="w-4 h-4" /> Back to Login
          </Link>
          <div className="inline-flex p-3 bg-blue-500/10 rounded-2xl mb-4">
            <Key className="w-6 h-6 text-blue-400" />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Recovery</h1>
          <p className="text-slate-400 mt-2 text-sm">
            {step === 1 ? "Enter your username to receive a reset token." : "Enter the token and your new password."}
          </p>
        </div>

        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.form key="step1" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} onSubmit={handleRequestToken} className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-slate-500 ml-1">Username</label>
                <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                  <input
                    type="text" required
                    className="w-full bg-white/5 border border-white/10 rounded-xl py-3.5 pl-12 pr-4 text-white outline-none focus:border-blue-500 transition-all text-sm"
                    placeholder="Enter account username"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  />
                </div>
              </div>
              <button disabled={isLoading} className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all">
                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <span>Request Recovery Token</span>}
              </button>
            </motion.form>
          ) : (
            <motion.form key="step2" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} onSubmit={handleResetPassword} className="space-y-5">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-slate-500 ml-1">Recovery Token</label>
                <input
                  type="text" required
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3.5 px-4 text-white outline-none focus:border-blue-500 transition-all text-sm font-mono tracking-widest"
                  placeholder="Paste token here"
                  value={formData.token}
                  onChange={(e) => setFormData({ ...formData, token: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-slate-500 ml-1">New Password</label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                  <input
                    type="password" required
                    className="w-full bg-white/5 border border-white/10 rounded-xl py-3.5 pl-12 pr-4 text-white outline-none focus:border-blue-500 transition-all text-sm"
                    placeholder="Min 6 characters"
                    value={formData.newPassword}
                    onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
                  />
                </div>
              </div>
              {message && <p className="text-[10px] text-orange-400 bg-orange-400/5 p-2 rounded-lg border border-orange-400/10">{message}</p>}
              <button disabled={isLoading} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-600/20">
                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <span>Reset Password</span>}
              </button>
            </motion.form>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
