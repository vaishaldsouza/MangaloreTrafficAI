"use client";

import React, { useEffect } from "react";
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

// Custom vehicle icon
const vehicleIcon = L.divIcon({
  className: "custom-vehicle-icon",
  html: `<div style="width: 12px; height: 12px; background: #3b82f6; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px rgba(59,130,246,0.5);"></div>`,
  iconSize: [12, 12],
  iconAnchor: [6, 6],
});

interface MapProps {
  center: [number, number];
  zoom: number;
  vehicles?: Array<{ id: string; lat: number; lon: number; speed: number }>;
}

function ChangeView({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

export default function Map({ center, zoom, vehicles = [] }: MapProps) {
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
      
      {vehicles.map((v) => (
        <Marker 
          key={v.id} 
          position={[v.lat, v.lon]} 
          icon={vehicleIcon}
        >
          <Popup className="custom-popup">
            <div className="p-1">
              <p className="font-bold text-xs">Vehicle: {v.id}</p>
              <p className="text-[10px] text-slate-500">Speed: {v.speed.toFixed(1)} m/s</p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
