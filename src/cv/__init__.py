# src/cv/__init__.py
"""
Computer Vision perception layer for Mangalore Traffic AI.
Provides a drop-in replacement for TraCI sensor reads using
YOLOv8 detection + DeepSORT tracking + ROI lane counting.
"""
from .detector import VehicleDetector
from .tracker import VehicleTracker
from .lane_counter import LaneROICounter
from .cv_pipeline import CVPipeline

__all__ = ["VehicleDetector", "VehicleTracker", "LaneROICounter", "CVPipeline"]
