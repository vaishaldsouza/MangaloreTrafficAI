"use client";
import { useEffect, useRef } from "react";
import { SimStep } from "@/hooks/useSimulation";

export default function LiveMetricsChart({ history }: { history: SimStep[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || history.length < 2) return;
    const ctx = canvas.getContext("2d")!;
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    const queues = history.map(h => h.total_queue);
    const max = Math.max(...queues, 1);

    // Draw queue line
    ctx.strokeStyle = "#3b82f6";
    ctx.lineWidth = 2;
    ctx.beginPath();
    queues.forEach((q, i) => {
      const x = (i / (queues.length - 1)) * W;
      const y = H - (q / max) * (H - 20) - 10;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Label
    ctx.fillStyle = "#94a3b8";
    ctx.font = "11px sans-serif";
    ctx.fillText(`Queue: ${queues.at(-1)?.toFixed(0)} vehicles`, 8, 16);
  }, [history]);

  return (
    <canvas
      ref={canvasRef}
      width={600}
      height={160}
      style={{ width: "100%", borderRadius: 8, background: "rgba(0,0,0,0.2)" }}
    />
  );
}
