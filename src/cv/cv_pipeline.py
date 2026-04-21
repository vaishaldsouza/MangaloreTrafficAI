# src/cv/cv_pipeline.py
"""
Assembled CV pipeline: frame → lane vehicle counts.

CVPipeline.process_frame() is a drop-in replacement for TraCI's
getLastStepVehicleNumber() — it returns the same semantic information
(vehicles per lane) derived from a camera frame instead of SUMO sensors.

CVPipeline.counts_to_observation() matches the output shape of
SumoTrafficEnv._get_obs(), so the PPO/DQN agent works unchanged.
"""
import cv2
import numpy as np

from .detector import VehicleDetector
from .tracker import VehicleTracker
from .lane_counter import LaneROICounter


class CVPipeline:
    """
    Full CV pipeline: BGR frame → per-lane vehicle counts.

    Args:
        frame_width  : Expected frame width (pixels).
        frame_height : Expected frame height (pixels).
        yolo_model   : YOLOv8 weights path or name (e.g. "yolov8n.pt").
        conf         : Detection confidence threshold.
        device       : Inference device ("cpu" | "cuda").
    """

    def __init__(
        self,
        frame_width: int = 640,
        frame_height: int = 480,
        yolo_model: str = "yolov8n.pt",
        conf: float = 0.4,
        device: str = "cpu",
    ):
        self.detector    = VehicleDetector(yolo_model, conf=conf, device=device)
        self.tracker     = VehicleTracker(max_age=30)
        self.counter     = LaneROICounter(frame_width, frame_height)
        self.last_counts = {"N": 0, "S": 0, "E": 0, "W": 0}

    def process_frame(
        self, frame: np.ndarray, visualize: bool = False
    ) -> tuple[dict[str, int], np.ndarray] | dict[str, int]:
        """
        Run the full detect → track → count pipeline on one frame.

        Args:
            frame     : BGR numpy array.
            visualize : If True, draw bounding boxes and ROI overlays.

        Returns:
            When visualize=False : dict {"N": int, "S": int, "E": int, "W": int}
            When visualize=True  : (counts_dict, annotated_frame)
        """
        detections       = self.detector.detect(frame)
        tracks           = self.tracker.update(detections, frame)
        counts           = self.counter.count(tracks)
        self.last_counts = counts

        if visualize:
            annotated = self.detector.annotate(frame, detections)
            annotated = self.counter.draw_zones(annotated, counts)
            return counts, annotated

        return counts

    def counts_to_observation(self, max_vehicles: int = 20) -> np.ndarray:
        """
        Normalise last_counts into a [0, 1] float32 vector for the RL agent.

        The output format mirrors SumoTrafficEnv._get_obs():
            [count_N, count_S, count_E, count_W] / max_vehicles

        Args:
            max_vehicles : Saturation point for normalisation.

        Returns:
            np.ndarray of shape (4,), dtype float32, clipped to [0, 1].
        """
        lanes = ["N", "S", "E", "W"]
        return np.clip(
            np.array(
                [self.last_counts[l] / max_vehicles for l in lanes],
                dtype=np.float32,
            ),
            0.0,
            1.0,
        )
