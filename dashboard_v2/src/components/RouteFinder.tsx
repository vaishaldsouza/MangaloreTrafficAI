"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import DatasetImport from "./DatasetImport";
import RouteMap from "./RouteMap";
import { 
  MapPin, 
  Navigation, 
  Clock, 
  TrendingDown, 
  Route, 
  Car,
  Zap,
  AlertTriangle,
  CheckCircle,
  Search,
  X,
  ArrowRight,
  TrafficCone
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Location {
  id: string;
  name: string;
  lat: number;
  lon: number;
  address: string;
}

interface RouteOption {
  id: string;
  name: string;
  type: "fastest" | "least_traffic" | "shortest" | "balanced";
  distance: number;
  duration: number;
  trafficLevel: "low" | "medium" | "high";
  congestionScore: number;
  co2Emission: number;
  waypoints: Array<{ lat: number; lon: number }>;
  instructions: string[];
  realTimeUpdates: boolean;
}

interface TrafficData {
  roadId: string;
  congestionLevel: number;
  averageSpeed: number;
  vehicleCount: number;
  incidents: Array<{ type: string; severity: string; location: string }>;
}

const mangaloreLocations: Location[] = [
  { id: "1",  name: "Hampankatta",     lat: 12.8700, lon: 74.8400, address: "City Center" },
  { id: "2",  name: "Mangaladevi",     lat: 12.8780, lon: 74.8450, address: "Temple Area" },
  { id: "3",  name: "PVS Circle",      lat: 12.8650, lon: 74.8350, address: "PVS Junction" },
  { id: "4",  name: "Kulshekar",       lat: 12.8800, lon: 74.8500, address: "Northern Area" },
  { id: "5",  name: "Lalbagh",         lat: 12.8600, lon: 74.8300, address: "Southern Area" },
  { id: "6",  name: "Bunder",          lat: 12.8750, lon: 74.8250, address: "Port Area" },
  { id: "7",  name: "Kadri",           lat: 12.8850, lon: 74.8550, address: "Kadri Hills" },
  { id: "8",  name: "Surathkal",       lat: 12.9800, lon: 74.8200, address: "NITK Area" },
  { id: "9",  name: "Bejai",           lat: 12.8720, lon: 74.8480, address: "Bejai Market" },
  { id: "10", name: "Attavar",         lat: 12.8660, lon: 74.8420, address: "Attavar Junction" },
  { id: "11", name: "Kankanady",       lat: 12.8830, lon: 74.8530, address: "Kankanady Cross" },
  { id: "12", name: "Bondel",          lat: 12.8900, lon: 74.8600, address: "Bondel Junction" },
  { id: "13", name: "Urwa",            lat: 12.8580, lon: 74.8460, address: "Urwa Market" },
  { id: "14", name: "Falnir",          lat: 12.8740, lon: 74.8370, address: "Falnir Road" },
  { id: "15", name: "Mangalore Central Station", lat: 12.8673, lon: 74.8431, address: "Railway Station" },
  { id: "16", name: "Old Port Road",   lat: 12.8710, lon: 74.8220, address: "Old Port" },
  { id: "17", name: "Pandeshwar",      lat: 12.8695, lon: 74.8388, address: "Pandeshwar Junction" },
  { id: "18", name: "Kodialbail",      lat: 12.8760, lon: 74.8330, address: "Kodialbail" },
];

export default function RouteFinder() {
  const [startPoint, setStartPoint] = useState<Location | null>(null);
  const [endPoint, setEndPoint] = useState<Location | null>(null);
  const [routes, setRoutes] = useState<RouteOption[]>([]);
  const [selectedRoute, setSelectedRoute] = useState<RouteOption | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  
  // Separate states for start and end search
  const [startQuery, setStartQuery] = useState("");
  const [endQuery, setEndQuery] = useState("");
  const [showStartSugg, setShowStartSugg] = useState(false);
  const [showEndSugg, setShowEndSugg] = useState(false);

  const [trafficData, setTrafficData] = useState<TrafficData[]>([]);
  const [isLiveTraffic, setIsLiveTraffic] = useState(false);
  const [activeView, setActiveView] = useState<"routes" | "map">("routes");

  // Simulate real-time traffic data
  useEffect(() => {
    if (!isLiveTraffic) return;

    const interval = setInterval(() => {
      const newTrafficData: TrafficData[] = mangaloreLocations.map((loc, index) => ({
        roadId: `road_${index}`,
        congestionLevel: Math.random() * 100,
        averageSpeed: 20 + Math.random() * 40,
        vehicleCount: Math.floor(Math.random() * 200),
        incidents: Math.random() > 0.8 ? [{
          type: "accident",
          severity: Math.random() > 0.5 ? "major" : "minor",
          location: `Near ${loc.name}`
        }] : []
      }));
      setTrafficData(newTrafficData);
    }, 5000);

    return () => clearInterval(interval);
  }, [isLiveTraffic]);

  const calculateRoutes = async () => {
    if (!startPoint || !endPoint) return;

    setIsCalculating(true);
    setRoutes([]);

    // Simulate route calculation
    setTimeout(() => {
      const calculatedRoutes: RouteOption[] = [
        {
          id: "1",
          name: "Fastest Route",
          type: "fastest",
          distance: 5.2,
          duration: 12,
          trafficLevel: "medium",
          congestionScore: 45,
          co2Emission: 2.1,
          waypoints: generateWaypoints(startPoint, endPoint),
          instructions: [
            "Head north on NH-66",
            "Continue straight for 2km",
            "Turn right at Hampankatta",
            "Arrive at destination"
          ],
          realTimeUpdates: true
        },
        {
          id: "2",
          name: "Least Traffic Route",
          type: "least_traffic",
          distance: 6.8,
          duration: 15,
          trafficLevel: "low",
          congestionScore: 15,
          co2Emission: 2.8,
          waypoints: generateWaypoints(startPoint, endPoint, true),
          instructions: [
            "Head east on Service Road",
            "Take bypass highway",
            "Continue through residential area",
            "Turn left at Mangaladevi",
            "Arrive at destination"
          ],
          realTimeUpdates: true
        },
        {
          id: "3",
          name: "Shortest Route",
          type: "shortest",
          distance: 4.1,
          duration: 18,
          trafficLevel: "high",
          congestionScore: 75,
          co2Emission: 3.2,
          waypoints: generateWaypoints(startPoint, endPoint, false, true),
          instructions: [
            "Take direct city road",
            "Navigate through downtown",
            "Multiple turns required",
            "Arrive at destination"
          ],
          realTimeUpdates: true
        },
        {
          id: "4",
          name: "Balanced Route",
          type: "balanced",
          distance: 5.5,
          duration: 14,
          trafficLevel: "medium",
          congestionScore: 35,
          co2Emission: 2.3,
          waypoints: generateWaypoints(startPoint, endPoint),
          instructions: [
            "Mix of main roads and side streets",
            "Optimal balance of time and traffic",
            "Moderate fuel consumption",
            "Arrive at destination"
          ],
          realTimeUpdates: true
        }
      ];

      setRoutes(calculatedRoutes);
      setIsCalculating(false);
    }, 2000);
  };

  const generateWaypoints = (start: Location, end: Location, avoidTraffic = false, shortest = false) => {
    const waypoints = [];
    const steps = avoidTraffic ? 8 : shortest ? 4 : 6;
    
    for (let i = 0; i <= steps; i++) {
      const progress = i / steps;
      const lat = start.lat + (end.lat - start.lat) * progress + (Math.random() - 0.5) * 0.01;
      const lon = start.lon + (end.lon - start.lon) * progress + (Math.random() - 0.5) * 0.01;
      waypoints.push({ lat, lon });
    }
    
    return waypoints;
  };

  const getTrafficColor = (level: string) => {
    switch (level) {
      case "low": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "medium": return "text-orange-400 bg-orange-500/10 border-orange-500/20";
      case "high": return "text-red-400 bg-red-500/10 border-red-500/20";
      default: return "text-slate-400 bg-slate-500/10 border-slate-500/20";
    }
  };

  const getRouteIcon = (type: RouteOption["type"]) => {
    switch (type) {
      case "fastest": return <Zap className="w-4 h-4" />;
      case "least_traffic": return <TrendingDown className="w-4 h-4" />;
      case "shortest": return <Route className="w-4 h-4" />;
      case "balanced": return <Navigation className="w-4 h-4" />;
    }
  };

  const getRouteColor = (type: RouteOption["type"]) => {
    switch (type) {
      case "fastest": return "text-blue-400 bg-blue-500/10 border-blue-500/20";
      case "least_traffic": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "shortest": return "text-purple-400 bg-purple-500/10 border-purple-500/20";
      case "balanced": return "text-cyan-400 bg-cyan-500/10 border-cyan-500/20";
    }
  };

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-green-500/10 rounded-xl border border-green-500/20">
            <Navigation className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Best Route Finder</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              AI-Powered Traffic Navigation
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveView("routes")}
              className={cn(
                "px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all",
                activeView === "routes"
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-white/5 text-slate-400 border border-transparent"
              )}
            >
              Routes
            </button>
            <button
              onClick={() => setActiveView("map")}
              className={cn(
                "px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all",
                activeView === "map"
                  ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30"
                  : "bg-white/5 text-slate-400 border border-transparent"
              )}
            >
              Map
            </button>
          </div>
          
          <div className={cn(
            "w-2 h-2 rounded-full animate-pulse",
            isLiveTraffic ? "bg-emerald-500" : "bg-slate-500"
          )} />
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
            {isLiveTraffic ? "Live Traffic" : "Static Data"}
          </span>
        </div>
      </div>

      {/* Route Input Section */}
      <div className="space-y-4 mb-6">
        <div className="relative">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/20 rounded-lg">
              <MapPin className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search starting point..."
                value={startPoint ? startPoint.name : startQuery}
                onChange={(e) => {
                  setStartQuery(e.target.value);
                  setShowStartSugg(true);
                  setStartPoint(null);
                }}
                onFocus={() => setShowStartSugg(true)}
                onBlur={() => setTimeout(() => setShowStartSugg(false), 150)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-emerald-500 transition-all"
              />
              {startPoint && (
                <button
                  onClick={() => {
                    setStartPoint(null);
                    setStartQuery("");
                  }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
          
          <AnimatePresence>
            {showStartSugg && !startPoint && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute top-full left-0 right-0 mt-2 bg-slate-900/95 backdrop-blur-md rounded-xl border border-white/10 z-50 max-h-48 overflow-y-auto shadow-2xl"
              >
                {mangaloreLocations
                  .filter(l => l.name.toLowerCase().includes(startQuery.toLowerCase()))
                  .map((location) => (
                    <button
                      key={location.id}
                      onMouseDown={(e) => {
                        e.preventDefault();
                        setStartPoint(location);
                        setStartQuery("");
                        setShowStartSugg(false);
                      }}
                      className="w-full px-4 py-3 text-left hover:bg-white/5 transition-colors border-b border-white/5 last:border-b-0"
                    >
                      <div className="text-white font-medium text-sm">{location.name}</div>
                      <div className="text-[10px] text-slate-400">{location.address}</div>
                    </button>
                  ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="relative">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/20 rounded-lg">
              <MapPin className="w-4 h-4 text-red-400" />
            </div>
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search destination..."
                value={endPoint ? endPoint.name : endQuery}
                onChange={(e) => {
                  setEndQuery(e.target.value);
                  setShowEndSugg(true);
                  setEndPoint(null);
                }}
                onFocus={() => setShowEndSugg(true)}
                onBlur={() => setTimeout(() => setShowEndSugg(false), 150)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-red-500 transition-all"
              />
              {endPoint && (
                <button
                  onClick={() => {
                    setEndPoint(null);
                    setEndQuery("");
                  }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
          
          <AnimatePresence>
            {showEndSugg && !endPoint && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute top-full left-0 right-0 mt-2 bg-slate-900/95 backdrop-blur-md rounded-xl border border-white/10 z-50 max-h-48 overflow-y-auto shadow-2xl"
              >
                {mangaloreLocations
                  .filter(l => l.name.toLowerCase().includes(endQuery.toLowerCase()) && l.id !== startPoint?.id)
                  .map((location) => (
                    <button
                      key={location.id}
                      onMouseDown={(e) => {
                        e.preventDefault();
                        setEndPoint(location);
                        setEndQuery("");
                        setShowEndSugg(false);
                      }}
                      className="w-full px-4 py-3 text-left hover:bg-white/5 transition-colors border-b border-white/5 last:border-b-0"
                    >
                      <div className="text-white font-medium text-sm">{location.name}</div>
                      <div className="text-[10px] text-slate-400">{location.address}</div>
                    </button>
                  ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="flex gap-3">
          <button
            onClick={calculateRoutes}
            disabled={!startPoint || !endPoint || isCalculating}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-semibold transition-all",
              startPoint && endPoint && !isCalculating
                ? "bg-green-600 hover:bg-green-500 text-white shadow-lg shadow-green-600/20"
                : "bg-white/5 text-white/50 cursor-not-allowed"
            )}
          >
            {isCalculating ? (
              <>
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                <span>Finding Routes...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Find Best Routes</span>
              </>
            )}
          </button>
          
          <button
            onClick={() => setIsLiveTraffic(!isLiveTraffic)}
            className={cn(
              "px-4 py-3 rounded-xl font-semibold transition-all border",
              isLiveTraffic
                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                : "bg-white/5 text-slate-400 border-white/10"
            )}
          >
            <TrafficCone className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <AnimatePresence mode="wait">
          {activeView === "routes" && (
            <motion.div
              key="routes"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex-1 overflow-hidden flex flex-col"
            >
              {isCalculating && (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-blue-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-blue-500/20">
                      <Navigation className="w-8 h-8 text-blue-400 animate-pulse" />
                    </div>
                    <h3 className="text-xl font-bold text-white">Calculating Routes</h3>
                    <p className="text-slate-400 text-sm mt-2">Analyzing traffic patterns and finding optimal paths...</p>
                  </div>
                </div>
              )}

              {!isCalculating && routes.length === 0 && (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-slate-800/50 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/5">
                      <Route className="w-8 h-8 text-slate-600" />
                    </div>
                    <h3 className="text-xl font-bold text-white">No Routes Found</h3>
                    <p className="text-slate-400 text-sm mt-2">Select start and destination points to find routes</p>
                  </div>
                </div>
              )}

              {!isCalculating && routes.length > 0 && (
                <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-none">
                  {routes.map((route, index) => (
                    <motion.div
                      key={route.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => setSelectedRoute(route)}
                      className={cn(
                        "p-4 rounded-xl border cursor-pointer transition-all hover:scale-[1.01]",
                        selectedRoute?.id === route.id
                          ? "bg-blue-500/10 border-blue-500/30"
                          : "bg-white/5 border-white/10 hover:bg-white/10"
                      )}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-3 flex-1">
                          <div className={cn(
                            "p-2 rounded-lg border",
                            getRouteColor(route.type)
                          )}>
                            {getRouteIcon(route.type)}
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="text-white font-bold text-sm">{route.name}</h4>
                              <span className={cn(
                                "px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest",
                                getRouteColor(route.type)
                              )}>
                                {route.type}
                              </span>
                            </div>
                            
                            <div className="grid grid-cols-3 gap-3 mb-3">
                              <div className="text-center">
                                <div className="text-md font-bold text-white">{route.distance}km</div>
                                <div className="text-[8px] text-slate-500 uppercase">Distance</div>
                              </div>
                              <div className="text-center">
                                <div className="text-md font-bold text-white">{route.duration}min</div>
                                <div className="text-[8px] text-slate-500 uppercase">Duration</div>
                              </div>
                              <div className="text-center">
                                <div className="text-md font-bold text-white">{route.co2Emission}kg</div>
                                <div className="text-[8px] text-slate-500 uppercase">CO2</div>
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <span className={cn(
                                "px-2 py-0.5 rounded-md text-[9px] font-bold",
                                getTrafficColor(route.trafficLevel)
                              )}>
                                {route.trafficLevel.toUpperCase()} TRAFFIC
                              </span>
                              <span className="text-[9px] text-slate-400 font-medium">
                                Congestion: {route.congestionScore}%
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex flex-col items-end gap-2">
                          {route.realTimeUpdates && (
                            <div className="flex items-center gap-1 text-[9px] text-emerald-400 font-bold uppercase tracking-tighter">
                              <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
                              Live
                            </div>
                          )}
                          <ArrowRight className="w-4 h-4 text-slate-500" />
                        </div>
                      </div>
                      
                      {selectedRoute?.id === route.id && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          className="mt-4 pt-4 border-t border-white/10"
                        >
                          <h5 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Turn-by-turn Navigation</h5>
                          <div className="space-y-3">
                            {route.instructions.map((instruction, idx) => (
                              <div key={idx} className="flex items-start gap-3">
                                <div className="w-5 h-5 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 border border-blue-500/30">
                                  <span className="text-[10px] text-blue-400 font-black">{idx + 1}</span>
                                </div>
                                <p className="text-[11px] text-slate-300 leading-relaxed">{instruction}</p>
                              </div>
                            ))}
                          </div>
                          
                          <div className="mt-4 p-3 bg-emerald-500/5 rounded-xl border border-emerald-500/10">
                            <div className="flex items-center gap-3">
                              <div className="p-1.5 bg-emerald-500/20 rounded-lg">
                                <CheckCircle className="w-3 h-3 text-emerald-400" />
                              </div>
                              <span className="text-[10px] text-emerald-400 font-medium leading-tight">
                                This route saves {(route.congestionScore < 50 ? "35%" : "15%")} fuel compared to peak traffic averages.
                              </span>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {activeView === "map" && (
            <motion.div
              key="map"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex-1"
            >
              <RouteMap 
                startPoint={startPoint}
                endPoint={endPoint}
                selectedRoute={selectedRoute}
                trafficData={trafficData.map(t => ({
                  location: mangaloreLocations.find(l => l.id === t.roadId.split('_')[1])?.name || '',
                  congestionLevel: t.congestionLevel,
                  averageSpeed: t.averageSpeed,
                  vehicleCount: t.vehicleCount
                }))}
                isSimulating={isLiveTraffic && routes.length > 0}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Traffic Incidents */}
      {isLiveTraffic && trafficData.some(t => t.incidents.length > 0) && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-orange-400" />
            <span className="text-[10px] text-orange-400 font-bold uppercase tracking-widest">
              Live Incidents
            </span>
          </div>
          <div className="space-y-1">
            {trafficData
              .filter(t => t.incidents.length > 0)
              .slice(0, 2)
              .map((traffic) =>
                traffic.incidents.map((incident, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-[10px] text-orange-400/80 bg-orange-500/5 p-2 rounded-lg border border-orange-500/10">
                    <div className="w-1.5 h-1.5 bg-orange-400 rounded-full shadow-[0_0_5px_rgba(251,146,60,0.5)]" />
                    <span>{incident.type.toUpperCase()} - {incident.severity} at {incident.location}</span>
                  </div>
                ))
              )}
          </div>
        </div>
      )}
    </div>
  );
}
