"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { 
  MapPin, 
  Navigation, 
  Car, 
  Activity, 
  AlertTriangle,
  Layers,
  ZoomIn,
  ZoomOut,
  RotateCcw
} from "lucide-react";
import { cn } from "@/lib/utils";

interface MapLocation {
  id: string;
  name: string;
  lat: number;
  lon: number;
  address: string;
}

interface RoutePoint {
  lat: number;
  lon: number;
  congestion?: number;
  speed?: number;
}

interface SimulatedVehicle {
  id: string;
  position: { lat: number; lon: number };
  destination: { lat: number; lon: number };
  speed: number;
  routeIndex: number;
  color: string;
}

interface TrafficData {
  location: string;
  congestionLevel: number;
  averageSpeed: number;
  vehicleCount: number;
}

export default function RouteMap({ 
  startPoint, 
  endPoint, 
  selectedRoute, 
  trafficData, 
  isSimulating 
}: {
  startPoint: MapLocation | null;
  endPoint: MapLocation | null;
  selectedRoute: any;
  trafficData: TrafficData[];
  isSimulating: boolean;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [vehicles, setVehicles] = useState<SimulatedVehicle[]>([]);
  const [mapCenter] = useState({ lat: 12.8700, lon: 74.8400 }); // Mangalore center

  // Mangalore locations with coordinates
  const locations: MapLocation[] = [
    { id: "1", name: "Hampankatta", lat: 12.8700, lon: 74.8400, address: "City Center" },
    { id: "2", name: "Mangaladevi", lat: 12.8780, lon: 74.8450, address: "Temple Area" },
    { id: "3", name: "PVS", lat: 12.8650, lon: 74.8350, address: "PVS Circle" },
    { id: "4", name: "Kulshekar", lat: 12.8800, lon: 74.8500, address: "Northern Area" },
    { id: "5", name: "Lalbagh", lat: 12.8600, lon: 74.8300, address: "Southern Area" },
    { id: "6", name: "Bunder", lat: 12.8750, lon: 74.8250, address: "Port Area" },
    { id: "7", name: "Kadri", lat: 12.8850, lon: 74.8550, address: "Eastern Area" },
    { id: "8", name: "Surathkal", lat: 12.9800, lon: 74.8200, address: "Northern Suburb" },
  ];

  // Simulate vehicles on routes
  useEffect(() => {
    if (!isSimulating || !selectedRoute || !startPoint || !endPoint) {
      setVehicles([]);
      return;
    }

    const interval = setInterval(() => {
      setVehicles(prev => {
        const updated = prev.map(vehicle => {
          // Move vehicle along route
          const newRouteIndex = vehicle.routeIndex + 1;
          if (newRouteIndex >= selectedRoute.waypoints.length) {
            // Reset vehicle to start
            return {
              ...vehicle,
              position: { lat: startPoint.lat, lon: startPoint.lon },
              routeIndex: 0
            };
          }

          const nextWaypoint = selectedRoute.waypoints[newRouteIndex];
          return {
            ...vehicle,
            position: nextWaypoint,
            routeIndex: newRouteIndex
          };
        });

        // Add new vehicles if needed
        if (updated.length < 5 && Math.random() > 0.7) {
          const colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"];
          updated.push({
            id: Math.random().toString(36).substring(7),
            position: { lat: startPoint.lat, lon: startPoint.lon },
            destination: { lat: endPoint.lat, lon: endPoint.lon },
            speed: 30 + Math.random() * 20,
            routeIndex: 0,
            color: colors[Math.floor(Math.random() * colors.length)]
          });
        }

        return updated;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isSimulating, selectedRoute, startPoint, endPoint]);

  // Draw map on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Clear canvas
    ctx.fillStyle = '#0F172A';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = '#1E293B';
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.width; i += 50) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, canvas.height);
      ctx.stroke();
    }
    for (let i = 0; i < canvas.height; i += 50) {
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(canvas.width, i);
      ctx.stroke();
    }

    // Convert lat/lon to canvas coordinates
    const latLonToCanvas = (lat: number, lon: number) => {
      const x = ((lon - mapCenter.lon) * 10000 * zoom) + canvas.width / 2 + offset.x;
      const y = ((mapCenter.lat - lat) * 10000 * zoom) + canvas.height / 2 + offset.y;
      return { x, y };
    };

    // Draw roads between locations
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 2;
    locations.forEach((loc1, i) => {
      locations.slice(i + 1).forEach(loc2 => {
        if (Math.random() > 0.6) { // Draw some roads
          const start = latLonToCanvas(loc1.lat, loc1.lon);
          const end = latLonToCanvas(loc2.lat, loc2.lon);
          
          ctx.beginPath();
          ctx.moveTo(start.x, start.y);
          ctx.lineTo(end.x, end.y);
          ctx.stroke();
        }
      });
    });

    // Draw traffic congestion on roads
    trafficData.forEach(traffic => {
      const loc = locations.find(l => l.name === traffic.location);
      if (!loc) return;

      const congestion = traffic.congestionLevel;
      const color = congestion > 70 ? '#EF4444' : congestion > 40 ? '#F59E0B' : '#10B981';
      
      // Draw congestion indicator
      const pos = latLonToCanvas(loc.lat, loc.lon);
      ctx.fillStyle = color + '40';
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 30 * zoom, 0, Math.PI * 2);
      ctx.fill();
    });

    // Draw selected route
    if (selectedRoute && startPoint && endPoint) {
      ctx.strokeStyle = '#3B82F6';
      ctx.lineWidth = 4;
      ctx.setLineDash([10, 5]);
      
      ctx.beginPath();
      selectedRoute.waypoints.forEach((point: RoutePoint, index: number) => {
        const pos = latLonToCanvas(point.lat, point.lon);
        if (index === 0) {
          ctx.moveTo(pos.x, pos.y);
        } else {
          ctx.lineTo(pos.x, pos.y);
        }
      });
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Draw locations
    locations.forEach(loc => {
      const pos = latLonToCanvas(loc.lat, loc.lon);
      const isStart = startPoint?.id === loc.id;
      const isEnd = endPoint?.id === loc.id;
      
      // Draw location marker
      ctx.fillStyle = isStart ? '#10B981' : isEnd ? '#EF4444' : '#6B7280';
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 8 * zoom, 0, Math.PI * 2);
      ctx.fill();
      
      // Draw location name
      ctx.fillStyle = '#FFFFFF';
      ctx.font = `${12 * zoom}px system-ui`;
      ctx.textAlign = 'center';
      ctx.fillText(loc.name, pos.x, pos.y - 15 * zoom);
    });

    // Draw simulated vehicles
    vehicles.forEach(vehicle => {
      const pos = latLonToCanvas(vehicle.position.lat, vehicle.position.lon);
      
      // Draw vehicle
      ctx.fillStyle = vehicle.color;
      ctx.fillRect(pos.x - 4 * zoom, pos.y - 4 * zoom, 8 * zoom, 8 * zoom);
      
      // Draw vehicle trail
      ctx.strokeStyle = vehicle.color + '60';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 12 * zoom, 0, Math.PI * 2);
      ctx.stroke();
    });

    // Draw legend
    ctx.fillStyle = '#1E293B';
    ctx.fillRect(10, 10, 200, 120);
    ctx.strokeStyle = '#334155';
    ctx.strokeRect(10, 10, 200, 120);
    
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '12px system-ui';
    ctx.fillText('Traffic Legend', 20, 30);
    
    // Legend items
    const legendItems = [
      { color: '#10B981', label: 'Low Traffic' },
      { color: '#F59E0B', label: 'Medium Traffic' },
      { color: '#EF4444', label: 'High Traffic' },
      { color: '#3B82F6', label: 'Selected Route' }
    ];
    
    legendItems.forEach((item, index) => {
      ctx.fillStyle = item.color;
      ctx.fillRect(20, 40 + index * 20, 15, 15);
      ctx.fillStyle = '#FFFFFF';
      ctx.font = '11px system-ui';
      ctx.fillText(item.label, 45, 52 + index * 20);
    });

  }, [zoom, offset, startPoint, endPoint, selectedRoute, trafficData, vehicles, mapCenter]);

  const handleZoomIn = () => setZoom(prev => Math.min(prev * 1.2, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev / 1.2, 0.5));
  const handleReset = () => {
    setZoom(1);
    setOffset({ x: 0, y: 0 });
  };

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-500/10 rounded-xl border border-blue-500/20">
            <Layers className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Route Map</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              Real-time Traffic Visualization
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomIn}
            className="p-2 bg-white/5 hover:bg-white/10 rounded-lg transition-all"
          >
            <ZoomIn className="w-4 h-4 text-slate-400" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2 bg-white/5 hover:bg-white/10 rounded-lg transition-all"
          >
            <ZoomOut className="w-4 h-4 text-slate-400" />
          </button>
          <button
            onClick={handleReset}
            className="p-2 bg-white/5 hover:bg-white/10 rounded-lg transition-all"
          >
            <RotateCcw className="w-4 h-4 text-slate-400" />
          </button>
        </div>
      </div>

      <div className="flex-1 relative bg-slate-900 rounded-xl overflow-hidden">
        <canvas
          ref={canvasRef}
          className="w-full h-full cursor-move"
          style={{ imageRendering: 'crisp-edges' }}
        />
        
        {/* Map overlay info */}
        <div className="absolute top-4 right-4 bg-slate-900/90 backdrop-blur-sm rounded-lg p-3 border border-white/10">
          <div className="space-y-2 text-[10px]">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
              <span className="text-white font-medium">
                {isSimulating ? 'Simulating' : 'Idle'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Car className="w-3 h-3 text-slate-400" />
              <span className="text-slate-300">{vehicles.length} vehicles</span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-3 h-3 text-slate-400" />
              <span className="text-slate-300">Zoom: {(zoom * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>

        {/* Route info overlay */}
        {selectedRoute && startPoint && endPoint && (
          <div className="absolute bottom-4 left-4 bg-slate-900/90 backdrop-blur-sm rounded-lg p-3 border border-white/10">
            <div className="space-y-1 text-[10px]">
              <div className="flex items-center gap-2">
                <Navigation className="w-3 h-3 text-blue-400" />
                <span className="text-white font-medium">{selectedRoute.name}</span>
              </div>
              <div className="text-slate-300">
                {startPoint.name} to {endPoint.name}
              </div>
              <div className="flex items-center gap-4 text-slate-400">
                <span>{selectedRoute.distance}km</span>
                <span>{selectedRoute.duration}min</span>
                <span className={cn(
                  "px-2 py-0.5 rounded text-[8px] font-bold",
                  selectedRoute.trafficLevel === 'low' ? "bg-emerald-500/20 text-emerald-400" :
                  selectedRoute.trafficLevel === 'medium' ? "bg-orange-500/20 text-orange-400" :
                  "bg-red-500/20 text-red-400"
                )}>
                  {selectedRoute.trafficLevel}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Traffic alerts */}
        {trafficData.some(t => t.congestionLevel > 70) && (
          <div className="absolute top-4 left-4 bg-red-500/10 backdrop-blur-sm rounded-lg p-3 border border-red-500/20">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <span className="text-red-400 text-[10px] font-medium">
                High Traffic Detected
              </span>
            </div>
            <div className="text-[9px] text-red-400/80 mt-1">
              {trafficData.filter(t => t.congestionLevel > 70).length} locations affected
            </div>
          </div>
        )}
      </div>

      {/* Map controls info */}
      <div className="mt-4 flex items-center justify-between text-[10px] text-slate-500">
        <div className="flex items-center gap-4">
          <span>Drag to pan</span>
          <span>Scroll to zoom</span>
          <span>Double-click to center</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-emerald-400 rounded-full" />
          <span>Live traffic data</span>
        </div>
      </div>
    </div>
  );
}
