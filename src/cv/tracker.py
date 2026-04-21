# src/cv/tracker.py
"""
DeepSORT vehicle tracker — gives each vehicle a persistent ID across frames.
Critical for counting entries/exits per lane rather than just instantaneous presence.

Install: pip install deep-sort-realtime
"""
from deep_sort_realtime.deepsort_tracker import DeepSort
import numpy as np


class VehicleTracker:
    """
    Wraps DeepSORT to maintain vehicle identity across frames.

    Persistent IDs prevent double-counting the same vehicle as it moves
    through an ROI zone.  The track_history dict (track_id → list of
    center coords) can be used for trajectory visualisation.

    Args:
        max_age : Number of frames to keep a track alive without a match.
    """

    def __init__(self, max_age: int = 30):
        self.tracker = DeepSort(max_age=max_age)
        self.track_history: dict[int, list[tuple[int, int]]] = {}

    def update(self, detections: list[dict], frame: np.ndarray) -> list[dict]:
        """
        Update tracker with the current frame's detections.

        Args:
            detections : Output of VehicleDetector.detect().
            frame      : Original BGR frame (needed for appearance embedding).

        Returns:
            List of active confirmed tracks, each dict has:
                id     – persistent integer track ID
                bbox   – (x1, y1, x2, y2)
                center – (cx, cy)
        """
        # DeepSORT input format: ([x1, y1, w, h], confidence, class_name)
        ds_input = []
        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            ds_input.append(
                ([x1, y1, x2 - x1, y2 - y1], d["confidence"], d["class_name"])
            )

        tracks = self.tracker.update_tracks(ds_input, frame=frame)

        active = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            tid = track.track_id
            x1, y1, x2, y2 = map(int, track.to_ltrb())
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            self.track_history.setdefault(tid, []).append((cx, cy))
            active.append({"id": tid, "bbox": (x1, y1, x2, y2), "center": (cx, cy)})

        return active
