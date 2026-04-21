# src/cv/run_cv_demo.py
"""
Live CV pipeline demo — runs the full detection+tracking+counting stack.

Usage
-----
  # Webcam (device 0)
  python src/cv/run_cv_demo.py --source 0

  # Video file
  python src/cv/run_cv_demo.py --source path/to/traffic.mp4

  # SUMO FCD virtual camera (run SUMO with fcd-output first)
  python src/cv/run_cv_demo.py --source sumo

Press 'q' to quit the live window at any time.
"""
import argparse
import os
import sys

# Ensure 'src/' is on the path regardless of where the script is invoked from
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import cv2
from src.cv.cv_pipeline import CVPipeline


# ── Video / webcam demo ───────────────────────────────────────────────────────

def run_on_video(source: str) -> None:
    """
    Run the CV pipeline on a webcam or a video file.

    Args:
        source : "0" for webcam device 0, or a path to a video file.
    """
    pipeline = CVPipeline(frame_width=640, frame_height=480, conf=0.35)
    cap_src  = 0 if source == "0" else source
    cap      = cv2.VideoCapture(cap_src)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open video source: {source}")
        return

    print("[CV] Starting inference — press 'q' to quit.")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        counts, annotated = pipeline.process_frame(frame, visualize=True)

        # Lane count summary
        summary = "  ".join([f"{k}: {v}" for k, v in counts.items()])
        cv2.putText(
            annotated, summary, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
        )

        # RL observation vector
        obs     = pipeline.counts_to_observation()
        obs_str = "obs: " + " ".join([f"{v:.2f}" for v in obs])
        cv2.putText(
            annotated, obs_str, (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 255, 180), 1,
        )

        cv2.imshow("Mangalore Traffic CV", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


# ── SUMO FCD virtual camera demo ─────────────────────────────────────────────

def run_on_sumo_fcd(fcd_path: str, net_path: str) -> None:
    """
    Replay a SUMO FCD output as synthetic camera frames through the CV pipeline.

    Args:
        fcd_path : Path to simulation/output/fcd.xml.
        net_path : Path to simulation/mangalore.net.xml (for coordinate bounds).
    """
    from src.cv.sumo_virtual_camera import (
        parse_fcd_output,
        render_topdown_frame,
        get_world_bounds_from_net,
    )

    pipeline = CVPipeline(frame_width=640, frame_height=480, conf=0.2)
    frames   = parse_fcd_output(fcd_path)
    bounds   = get_world_bounds_from_net(net_path)

    print(f"[CV] Loaded {len(frames)} SUMO timesteps — press 'q' to quit.")
    for t, vehicles in sorted(frames.items()):
        frame            = render_topdown_frame(vehicles, bounds)
        counts, annotated = pipeline.process_frame(frame, visualize=True)

        cv2.putText(
            annotated, f"t={t:.0f}s  {counts}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2,
        )
        cv2.imshow("SUMO Virtual Camera", annotated)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mangalore Traffic CV pipeline demo"
    )
    parser.add_argument(
        "--source",
        default="0",
        help=(
            "Input source: '0' for webcam, path to video file, "
            "or 'sumo' to replay SUMO FCD output."
        ),
    )
    args = parser.parse_args()

    if args.source == "sumo":
        run_on_sumo_fcd(
            fcd_path="simulation/output/fcd.xml",
            net_path="simulation/mangalore.net.xml",
        )
    else:
        run_on_video(args.source)
