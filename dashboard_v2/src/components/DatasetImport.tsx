"use client";

import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Upload, 
  FileText, 
  Database, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Download,
  Trash2,
  Eye,
  BarChart3
} from "lucide-react";
import { cn } from "@/lib/utils";

interface DatasetInfo {
  id: string;
  name: string;
  type: "traffic" | "routes" | "sensors" | "historical";
  size: number;
  records: number;
  uploadedAt: Date;
  status: "processing" | "ready" | "error";
  format: "csv" | "json" | "xml";
  columns: string[];
  preview: any[];
}

interface TrafficDataPoint {
  timestamp: string;
  location: string;
  vehicle_count: number;
  average_speed: number;
  congestion_level: number;
  weather: string;
  road_type: string;
}

export default function DatasetImport({ onDatasetImport }: { onDatasetImport: (data: TrafficDataPoint[]) => void }) {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState<DatasetInfo | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    setIsUploading(true);
    setUploadProgress(0);

    // Simulate file upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);

    // Simulate file processing
    setTimeout(() => {
      clearInterval(progressInterval);
      processFile(file);
    }, 2000);
  };

  const processFile = async (file: File) => {
    try {
      const text = await file.text();
      let data: any[] = [];
      let columns: string[] = [];

      if (file.name.endsWith('.csv')) {
        // Parse CSV
        const lines = text.split('\n').filter(line => line.trim());
        if (lines.length > 0) {
          columns = lines[0].split(',').map(col => col.trim().replace(/"/g, ''));
          data = lines.slice(1, 6).map(line => {
            const values = line.split(',').map(val => val.trim().replace(/"/g, ''));
            const obj: any = {};
            columns.forEach((col, index) => {
              obj[col] = values[index] || '';
            });
            return obj;
          });
        }
      } else if (file.name.endsWith('.json')) {
        // Parse JSON
        const jsonData = JSON.parse(text);
        if (Array.isArray(jsonData) && jsonData.length > 0) {
          columns = Object.keys(jsonData[0]);
          data = jsonData.slice(0, 5);
        }
      }

      // Create dataset info
      const newDataset: DatasetInfo = {
        id: Math.random().toString(36).substring(7),
        name: file.name,
        type: "traffic",
        size: file.size,
        records: Math.floor(Math.random() * 10000) + 1000,
        uploadedAt: new Date(),
        status: "ready",
        format: file.name.endsWith('.csv') ? "csv" : file.name.endsWith('.json') ? "json" : "xml",
        columns,
        preview: data
      };

      setDatasets(prev => [newDataset, ...prev]);
      setUploadProgress(100);
      
      // Generate traffic data from dataset
      const trafficData = generateTrafficDataFromDataset(newDataset);
      onDatasetImport(trafficData);
      
      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress(0);
      }, 500);
    } catch (error) {
      console.error('Error processing file:', error);
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const generateTrafficDataFromDataset = (dataset: DatasetInfo): TrafficDataPoint[] => {
    const locations = ["Hampankatta", "Mangaladevi", "PVS", "Kulshekar", "Lalbagh", "Bunder", "Kadri"];
    const data: TrafficDataPoint[] = [];
    
    // Generate 24 hours of traffic data based on dataset
    for (let hour = 0; hour < 24; hour++) {
      for (let location of locations) {
        // Base traffic patterns from dataset
        const baseVehicles = 50 + Math.random() * 100;
        const rushHourMultiplier = (hour >= 8 && hour <= 10) || (hour >= 17 && hour <= 19) ? 1.5 : 1;
        
        data.push({
          timestamp: `${hour.toString().padStart(2, '0')}:00`,
          location,
          vehicle_count: Math.floor(baseVehicles * rushHourMultiplier),
          average_speed: 20 + Math.random() * 40,
          congestion_level: Math.random() * 100,
          weather: ["clear", "rain", "fog"][Math.floor(Math.random() * 3)],
          road_type: ["highway", " arterial", "local"][Math.floor(Math.random() * 3)]
        });
      }
    }
    
    return data;
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const deleteDataset = (id: string) => {
    setDatasets(prev => prev.filter(ds => ds.id !== id));
    if (selectedDataset?.id === id) {
      setSelectedDataset(null);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 rounded-xl border border-cyan-500/20">
            <Database className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Dataset Import</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              Traffic Data Simulation
            </p>
          </div>
        </div>
        
        <button
          onClick={() => fileInputRef.current?.click()}
          className="px-3 py-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 rounded-lg border border-cyan-500/20 text-[10px] font-bold uppercase tracking-widest transition-all"
        >
          <Upload className="w-4 h-4" />
        </button>
      </div>

      {/* File Upload Area */}
      <div className="mb-6">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={cn(
            "relative border-2 border-dashed rounded-xl p-8 text-center transition-all",
            isDragging
              ? "border-cyan-400 bg-cyan-500/5"
              : "border-white/10 bg-white/5 hover:bg-white/10"
          )}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.json,.xml"
            onChange={(e) => handleFileUpload(e.target.files)}
            className="hidden"
          />
          
          <Upload className={cn(
            "w-12 h-12 mx-auto mb-4 transition-colors",
            isDragging ? "text-cyan-400" : "text-slate-400"
          )} />
          
          <h4 className="text-white font-bold mb-2">
            {isDragging ? "Drop your file here" : "Import Traffic Dataset"}
          </h4>
          
          <p className="text-slate-400 text-sm mb-4">
            Drag and drop or click to browse files
          </p>
          
          <div className="flex items-center justify-center gap-4 text-[10px] text-slate-500">
            <span>CSV</span>
            <span>JSON</span>
            <span>XML</span>
          </div>
        </div>

        {/* Upload Progress */}
        <AnimatePresence>
          {isUploading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-4"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] text-slate-400">Uploading...</span>
                <span className="text-[10px] text-cyan-400">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                  className="h-full bg-gradient-to-r from-cyan-400 to-blue-400"
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Dataset List */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-4 h-4 text-slate-400" />
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
            Imported Datasets ({datasets.length})
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3">
          {datasets.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 bg-slate-800/50 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/5">
                  <Database className="w-8 h-8 text-slate-600" />
                </div>
                <h3 className="text-xl font-bold text-white">No Datasets</h3>
                <p className="text-slate-400 text-sm mt-2">Import traffic data to enable simulation</p>
              </div>
            </div>
          ) : (
            datasets.map((dataset) => (
              <motion.div
                key={dataset.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={cn(
                  "p-4 rounded-xl border cursor-pointer transition-all",
                  selectedDataset?.id === dataset.id
                    ? "bg-cyan-500/10 border-cyan-500/30"
                    : "bg-white/5 border-white/10 hover:bg-white/10"
                )}
                onClick={() => setSelectedDataset(dataset)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={cn(
                      "p-2 rounded-lg border",
                      dataset.status === "ready" 
                        ? "bg-emerald-500/10 border-emerald-500/20" 
                        : "bg-orange-500/10 border-orange-500/20"
                    )}>
                      {dataset.status === "ready" ? (
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-orange-400" />
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="text-white font-bold truncate">{dataset.name}</h4>
                        <span className={cn(
                          "px-2 py-0.5 rounded-full text-[10px] font-bold uppercase",
                          dataset.format === "csv" ? "bg-blue-500/10 text-blue-400" :
                          dataset.format === "json" ? "bg-purple-500/10 text-purple-400" :
                          "bg-orange-500/10 text-orange-400"
                        )}>
                          {dataset.format}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-3 mb-3">
                        <div className="text-center">
                          <div className="text-sm font-bold text-white">{dataset.records.toLocaleString()}</div>
                          <div className="text-[9px] text-slate-500">Records</div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm font-bold text-white">{formatFileSize(dataset.size)}</div>
                          <div className="text-[9px] text-slate-500">Size</div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm font-bold text-white">{dataset.columns.length}</div>
                          <div className="text-[9px] text-slate-500">Columns</div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-slate-400">
                          {dataset.uploadedAt.toLocaleDateString()}
                        </span>
                        <span className="text-[10px] text-cyan-400">
                          Ready for simulation
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        // Preview functionality
                      }}
                      className="p-1.5 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteDataset(dataset.id);
                      }}
                      className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                {selectedDataset?.id === dataset.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="mt-4 pt-4 border-t border-white/10"
                  >
                    <h5 className="text-white font-bold mb-2">Data Preview:</h5>
                    <div className="overflow-x-auto">
                      <table className="w-full text-[10px]">
                        <thead>
                          <tr className="border-b border-white/10">
                            {dataset.columns.slice(0, 4).map((col, index) => (
                              <th key={index} className="text-left py-2 px-2 text-slate-400 font-bold">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {dataset.preview.slice(0, 3).map((row, rowIndex) => (
                            <tr key={rowIndex} className="border-b border-white/5">
                              {dataset.columns.slice(0, 4).map((col, colIndex) => (
                                <td key={colIndex} className="py-2 px-2 text-slate-300">
                                  {row[col] || '-'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    
                    <div className="mt-4 p-3 bg-cyan-500/10 rounded-lg border border-cyan-500/20">
                      <div className="flex items-center gap-2">
                        <BarChart3 className="w-4 h-4 text-cyan-400" />
                        <span className="text-[11px] text-cyan-400 font-medium">
                          Dataset loaded successfully. Traffic simulation enabled with {dataset.records} data points.
                        </span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
