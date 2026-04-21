"use client";

import dynamic from "next/dynamic";
import React from "react";

// Dynamically import the Map component with no SSR
const Map = dynamic(() => import("./Map"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-slate-900/10 animate-pulse">
      <p className="text-slate-500 font-medium">Initializing Map Engine...</p>
    </div>
  ),
});

interface MapViewProps {
  center: [number, number];
  zoom: number;
  vehicles?: Array<any>;
}

export default function MapView(props: MapViewProps) {
  return <Map {...props} />;
}
