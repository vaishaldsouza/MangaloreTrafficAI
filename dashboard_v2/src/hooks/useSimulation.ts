"use client";

import { useState, useEffect, useRef, useCallback } from "react";

export type SimStep = {
  step: number;
  reward: number;
  total_queue: number;
  vehicles: Array<{ id: string; lat: number; lon: number; speed: number }>;
  congestion: string;
};

export function useSimulation() {
  const [data, setData] = useState<SimStep | null>(null);
  const [status, setStatus] = useState<"idle" | "running" | "complete" | "error">("idle");
  const ws = useRef<WebSocket | null>(null);

  const startSimulation = useCallback((config: any) => {
    const clientId = Math.random().toString(36).substring(7);
    const token = localStorage.getItem("token");
    
    // Connect to FastAPI WebSocket
    ws.current = new WebSocket(`ws://localhost:8000/simulation/ws/${clientId}?token=${token}`);

    ws.current.onopen = () => {
      setStatus("running");
      ws.current?.send(JSON.stringify({ type: "START", config }));
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "STEP") {
        setData(message);
      } else if (message.type === "COMPLETE") {
        setStatus("complete");
      } else if (message.type === "ERROR") {
        setStatus("error");
      }
    };

    ws.current.onclose = () => {
      if (status !== "complete") setStatus("idle");
    };

    ws.current.onerror = () => {
      setStatus("error");
    };
  }, [status]);

  const stopSimulation = useCallback(() => {
    ws.current?.close();
    setStatus("idle");
  }, []);

  useEffect(() => {
    return () => ws.current?.close();
  }, []);

  return { data, status, startSimulation, stopSimulation };
}
