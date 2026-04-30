"use client";
import { useState, useEffect, useRef, useCallback } from "react";

export type SimStep = {
  step: number;
  reward: number;
  total_queue: number;
  co2_mg: number;
  congestion: string;
  phase_name: string;
  vehicles: Array<{ id: string; lat: number; lon: number; speed: number; type: string }>;
};

export function useSimulation() {
  const [data, setData]       = useState<SimStep | null>(null);
  const [history, setHistory] = useState<SimStep[]>([]);
  const [status, setStatus]   = useState<"idle"|"running"|"complete"|"error">("idle");
  const ws = useRef<WebSocket | null>(null);

  const startSimulation = useCallback((config: any) => {
    setHistory([]);
    setData(null);
    const clientId = Math.random().toString(36).substring(7);
    const token = localStorage.getItem("token");
    ws.current = new WebSocket(`ws://localhost:8000/simulation/ws/${clientId}?token=${token}`);

    ws.current.onopen = () => {
      setStatus("running");
      ws.current?.send(JSON.stringify({ type: "START", config }));
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "STEP") {
        setData(message);
        setHistory(prev => [...prev.slice(-300), message]);  // keep last 300
      } else if (message.type === "COMPLETE") {
        setStatus("complete");
      } else if (message.type === "ERROR") {
        setStatus("error");
      }
    };

    ws.current.onclose = () => { 
        setStatus(prev => prev === "running" ? "idle" : prev); 
    };
    ws.current.onerror = () => setStatus("error");
  }, []);

  const stopSimulation = useCallback(() => {
    ws.current?.close();
    setStatus("idle");
  }, []);

  useEffect(() => () => { ws.current?.close(); }, []);

  return { data, history, status, startSimulation, stopSimulation };
}
