# src/cv/sumo_virtual_camera.py
"""
SUMO Virtual Camera — bridge between SUMO FCD output and the CV pipeline.

Parses SUMO's floating car data (fcd-output) XML and renders synthetic
top-down frames so the CV pipeline can be tested without a real camera.

How to enable fcd-output in simulation/config.sumocfg:
    <output>
        <fcd-output value="output/fcd.xml"/>
        <summary-output value="output/summary.xml"/>
    </output>

Run SUMO once to generate fcd.xml, then pass it to run_cv_demo.py --source sumo.
"""
import xml.etree.ElementTree as ET
import numpy as np
import cv2


# ── FCD parsing ──────────────────────────────────────────────────────────────

def parse_fcd_output(fcd_xml_path: str) -> dict[float, list[dict]]:
    """
    Parse a SUMO fcd-output XML file into a timestep → vehicle list mapping.

    SUMO fcd-output records x, y, speed, and angle of every vehicle at every
    simulation timestep.  Enable it in config.sumocfg with:
        <fcd-output value="output/fcd.xml"/>

    Args:
        fcd_xml_path : Path to the fcd.xml output file.

    Returns:
        Dict keyed by simulation time (float seconds) → list of vehicle dicts:
            id    – SUMO vehicle ID
            x, y  – SUMO network coordinates
            speed – m/s
            type  – vehicle type string
    """
    tree = ET.parse(fcd_xml_path)
    root = tree.getroot()
    frames: dict[float, list[dict]] = {}

    for timestep in root.findall("timestep"):
        t = float(timestep.attrib["time"])
        vehicles = []
        for v in timestep.findall("vehicle"):
            vehicles.append(
                {
                    "id":    v.attrib["id"],
                    "x":     float(v.attrib["x"]),
                    "y":     float(v.attrib["y"]),
                    "speed": float(v.attrib["speed"]),
                    "type":  v.attrib.get("type", "car"),
                }
            )
        frames[t] = vehicles

    return frames


# ── Synthetic frame rendering ─────────────────────────────────────────────────

def render_topdown_frame(
    vehicles: list[dict],
    world_bounds: tuple[float, float, float, float],
    frame_size: tuple[int, int] = (640, 480),
) -> np.ndarray:
    """
    Render a synthetic top-down camera frame from SUMO vehicle positions.

    Vehicles are drawn as coloured circles on a dark road background.
    Used to test the CV pipeline without a real camera feed.

    Args:
        vehicles     : List of vehicle dicts from parse_fcd_output().
        world_bounds : (min_x, min_y, max_x, max_y) in SUMO network coordinates.
        frame_size   : Output frame dimensions (width, height).

    Returns:
        BGR numpy array of shape (height, width, 3).
    """
    W, H = frame_size
    x_min, y_min, x_max, y_max = world_bounds

    # Dark-grey tarmac background
    frame = np.full((H, W, 3), 50, dtype=np.uint8)

    x_range = x_max - x_min or 1.0
    y_range = y_max - y_min or 1.0

    for v in vehicles:
        px = int((v["x"] - x_min) / x_range * W)
        # SUMO y-axis is inverted relative to image coordinates
        py = int((1.0 - (v["y"] - y_min) / y_range) * H)

        # Clamp to frame bounds
        px = max(0, min(px, W - 1))
        py = max(0, min(py, H - 1))

        color = (0, 200, 255) if v["type"] == "car" else (100, 100, 255)
        cv2.circle(frame, (px, py), 6, color, -1)

    return frame


# ── Network bounds extraction ─────────────────────────────────────────────────

def get_world_bounds_from_net(net_xml_path: str) -> tuple[float, float, float, float]:
    """
    Read the SUMO network XML to extract coordinate bounding box.

    Args:
        net_xml_path : Path to the .net.xml file.

    Returns:
        Tuple (min_x, min_y, max_x, max_y) in SUMO network coordinates.
        Falls back to (0, 0, 1000, 1000) if the location element is missing.
    """
    tree = ET.parse(net_xml_path)
    root = tree.getroot()
    loc  = root.find("location")

    if loc is None:
        return (0.0, 0.0, 1000.0, 1000.0)

    boundary = loc.attrib.get("convBoundary", "0,0,1000,1000")
    x1, y1, x2, y2 = map(float, boundary.split(","))
    return x1, y1, x2, y2


def get_junction_bounds(net_xml_path: str, junction_id: str, padding: float = 150.0) -> tuple[float, float, float, float]:
    """
    Extract coordinate bounds centered on a specific junction.
    
    Args:
        net_xml_path : Path to .net.xml.
        junction_id  : SUMO junction ID.
        padding      : Meters to show around the center.
        
    Returns:
        (min_x, min_y, max_x, max_y)
    """
    tree = ET.parse(net_xml_path)
    root = tree.getroot()
    
    # Find the specific junction node (or any junction if id is cluster)
    # SUMO clusters might not have a single 'junction' tag with that ID in the XML
    # depending on how it's saved. We'll search for it.
    for node in root.findall("junction"):
        if node.attrib.get("id") == junction_id:
            x = float(node.attrib["x"])
            y = float(node.attrib["y"])
            return (x - padding, y - padding, x + padding, y + padding)
            
    # Fallback to whole network if junction not found
    return get_world_bounds_from_net(net_xml_path)
