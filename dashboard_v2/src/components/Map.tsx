"use client";

import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix for default marker icons in Leaflet + Next.js
const DefaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

// Vehicle icon based on type and speed
function getVehicleIcon(type: string, speed: number) {
  const color = type === "emergency" ? "#ef4444"
    : type === "bus" ? "#f59e0b"
    : type === "autorickshaw" ? "#10b981"
    : type === "motorcycle" ? "#8b5cf6"
    : speed < 1 ? "#6b7280"   // stopped = gray
    : speed < 5 ? "#f97316"   // slow = orange
    : "#3b82f6";  // moving = blue

  const size = type === "bus" ? 14 : 10;

  return L.divIcon({
    className: "vehicle-marker",
    html: `<div style="
      width: ${size}px;
      height: ${size}px;
      background: ${color};
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 0 8px ${color}88, 0 0 4px rgba(0,0,0,0.3);
      transition: all 0.5s ease-out;
    "></div>`,
    iconSize: [size + 4, size + 4],
    iconAnchor: [(size + 4) / 2, (size + 4) / 2],
  });
}

interface Vehicle {
  id: string;
  lat: number;
  lng: number;
  speed: number;
  type?: string;
}

interface MapProps {
  center: [number, number];
  zoom: number;
  vehicles?: Vehicle[];
}

function ChangeView({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

// Convert backend vehicle format to frontend format
function normalizeVehicle(v: any): Vehicle {
  return {
    id: v.id,
    lat: v.lat,
    lng: v.lng ?? v.lon ?? 0,  // backend sends 'lng', fallback to 'lon'
    speed: v.speed ?? 0,
    type: v.type ?? "passenger",
  };
}

export default function Map({ center, zoom, vehicles = [] }: MapProps) {
  // Smooth vehicle positions with interpolation
  const [smoothVehicles, setSmoothVehicles] = useState<Vehicle[]>([]);

  useEffect(() => {
    const normalized = vehicles.map(normalizeVehicle);
    // Small delay for smooth transition animation
    const timer = setTimeout(() => setSmoothVehicles(normalized), 50);
    return () => clearTimeout(timer);
  }, [vehicles]);

  return (
    <MapContainer 
      center={center} 
      zoom={zoom} 
      style={{ height: "100%", width: "100%", background: "#0d1117" }}
      zoomControl={false}
    >
      <ChangeView center={center} zoom={zoom} />
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
      />
      
      {smoothVehicles.map((v) => (
        <Marker 
          key={v.id} 
          position={[v.lat, v.lng]} 
          icon={getVehicleIcon(v.type || "passenger", v.speed)}
        >
          <Popup className="custom-popup">
            <div className="p-2 min-w-[120px]">
              <p className="font-bold text-xs text-white">Vehicle {v.id}</p>
              <div className="mt-2 space-y-1">
                <div className="flex justify-between text-[10px]">
                  <span className="text-slate-400">Type:</span>
                  <span className="text-white capitalize">{v.type || "passenger"}</span>
                </div>
                <div className="flex justify-between text-[10px]">
                  <span className="text-slate-400">Speed:</span>
                  <span className={v.speed < 1 ? "text-red-400" : v.speed < 5 ? "text-yellow-400" : "text-blue-400"}>
                    {v.speed.toFixed(1)} m/s
                  </span>
                </div>
                <div className="flex justify-between text-[10px]">
                  <span className="text-slate-400">Position:</span>
                  <span className="text-slate-300 font-mono">
                    {v.lat.toFixed(4)}, {v.lng.toFixed(4)}
                  </span>
                </div>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
