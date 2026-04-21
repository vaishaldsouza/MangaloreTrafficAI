# src/cv/lane_counter.py
"""
Polygon ROI (Region-of-Interest) lane counter.

Each approach to the intersection is defined as a polygon in pixel space.
Counts how many confirmed vehicle centers fall inside each zone per frame.

For real deployment : draw ROIs using cv2 on a snapshot of your CCTV feed.
For SUMO testing    : ROIs are defined relative to the rendered frame size.
"""
import cv2
import numpy as np


class LaneROICounter:
    """
    Defines polygon zones for each lane approach to a 4-way intersection
    (North, South, East, West) and counts vehicles currently inside each zone.

    Args:
        frame_width  : Width of the input frame in pixels.
        frame_height : Height of the input frame in pixels.
    """

    def __init__(self, frame_width: int, frame_height: int):
        W, H = frame_width, frame_height
        CX, CY = W // 2, H // 2

        # Polygon vertices for each incoming approach lane
        self.zones: dict[str, np.ndarray] = {
            "N": np.array(
                [[CX - 60, 0], [CX + 60, 0], [CX + 60, CY - 40], [CX - 60, CY - 40]],
                np.int32,
            ),
            "S": np.array(
                [[CX - 60, CY + 40], [CX + 60, CY + 40], [CX + 60, H], [CX - 60, H]],
                np.int32,
            ),
            "E": np.array(
                [[CX + 40, CY - 60], [W, CY - 60], [W, CY + 60], [CX + 40, CY + 60]],
                np.int32,
            ),
            "W": np.array(
                [[0, CY - 60], [CX - 40, CY - 60], [CX - 40, CY + 60], [0, CY + 60]],
                np.int32,
            ),
        }

    def count(self, tracks: list[dict]) -> dict[str, int]:
        """
        Count vehicles whose center point lies inside each ROI zone.

        Args:
            tracks : List of active tracks from VehicleTracker.update().

        Returns:
            Dict mapping lane name → vehicle count, e.g. {"N": 3, "S": 1, ...}
        """
        counts: dict[str, int] = {lane: 0 for lane in self.zones}
        for track in tracks:
            cx, cy = track["center"]
            for lane, poly in self.zones.items():
                if cv2.pointPolygonTest(poly, (float(cx), float(cy)), False) >= 0:
                    counts[lane] += 1
                    break   # assign vehicle to at most one zone
        return counts

    def draw_zones(self, frame: np.ndarray, counts: dict[str, int]) -> np.ndarray:
        """
        Overlay ROI zone outlines and live vehicle counts on the frame.
        Useful for debugging zone placement.

        Args:
            frame  : BGR frame to draw on (mutated in place).
            counts : Output of count().

        Returns:
            Annotated frame.
        """
        colors = {
            "N": (255, 100, 0),
            "S": (255, 100, 0),
            "E": (0, 150, 255),
            "W": (0, 150, 255),
        }
        for lane, poly in self.zones.items():
            cv2.polylines(frame, [poly], True, colors[lane], 2)
            cx = int(poly[:, 0].mean())
            cy = int(poly[:, 1].mean())
            cv2.putText(
                frame,
                f"{lane}: {counts.get(lane, 0)}",
                (cx - 20, cy),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                colors[lane],
                2,
            )
        return frame
