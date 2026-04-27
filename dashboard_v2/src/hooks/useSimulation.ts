"use client";
import { useState, useEffect, useRef, useCallback } from "react";

export type SimStep = {
  step: number;
  reward: number;
  total_queue: number;
  co2_mg: number;
  congestion: string;
  phase_name: string;
  vehicles: Array<{ id: string; lat: number; lon: number; speed: number }>;
};

function getLOS(avgDelay: number): string {
  if (avgDelay <= 10) return "A";
  if (avgDelay <= 20) return "B";
  if (avgDelay <= 35) return "C";
  if (avgDelay <= 55) return "D";
  if (avgDelay <= 80) return "E";
  return "F";
}

export function useSimulation() {
  const [latest, setLatest] = useState<SimStep | null>(null);
  const [history, setHistory] = useState<SimStep[]>([]);
  const [los, setLos] = useState<string>("—");
  const [status, setStatus] = useState<"idle" | "running" | "complete" | "error">("idle");
  const ws = useRef<WebSocket | null>(null);

  const startSimulation = useCallback((config: any) => {
    setHistory([]);
    setLatest(null);
    setLos("—");
    const clientId = Math.random().toString(36).substring(7);
    const token = localStorage.getItem("token");
    ws.current = new WebSocket(`ws://localhost:8000/simulation/ws/${clientId}?token=${token}`);

    ws.current.onopen = () => {
      setStatus("running");
      ws.current?.send(JSON.stringify({ type: "START", config }));
    };

    ws.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "STEP") {
        setLatest(msg);
        setHistory(prev => {
          const next = [...prev, msg];
          // Recalculate LoS from running average
          const avg = next.reduce((s, r) => s + r.total_queue, 0) / next.length * 5;
          setLos(getLOS(avg));
          return next;
        });
      } else if (msg.type === "COMPLETE") {
        setStatus("complete");
      } else if (msg.type === "ERROR") {
        setStatus("error");
      }
    };

    ws.current.onclose = () => setStatus(s => s === "running" ? "idle" : s);
    ws.current.onerror = () => setStatus("error");
  }, []);

  const stopSimulation = useCallback(() => {
    ws.current?.send(JSON.stringify({ type: "STOP" }));
    ws.current?.close();
    setStatus("idle");
  }, []);

  useEffect(() => () => { ws.current?.close(); }, []);

  return { latest, history, los, status, startSimulation, stopSimulation };
}
