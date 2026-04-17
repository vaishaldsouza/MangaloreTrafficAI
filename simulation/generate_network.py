"""
Downloads Mangalore OSM data and converts it to SUMO network format.
Run once: python simulation/generate_network.py
"""
import osmnx as ox
import subprocess
import os

# Enable setting required for saving OSM XML
ox.settings.all_oneway = True

OUT_DIR = "simulation"
os.makedirs(OUT_DIR, exist_ok=True)

# Mangalore center approx coordinates and 2km radius
CENTER_LAT = 12.8700
CENTER_LON = 74.8436
RADIUS_METERS = 2000

# 1. Download road graph from OpenStreetMap
print("Downloading Mangalore road network from OSM (using a 2km radius)...")
G = ox.graph_from_point((CENTER_LAT, CENTER_LON), dist=RADIUS_METERS, network_type="drive", simplify=False)
ox.save_graph_xml(G, filepath=f"{OUT_DIR}/mangalore.osm")
print("Saved mangalore.osm")

def generate_sumo_network(osm_path: str, output_net: str, output_routes: str):
    """
    Converts an OSM file to a SUMO network and generates random routes.
    """
    # 2. Convert OSM -> SUMO network using netconvert
    print(f"Converting {osm_path} to SUMO network...")
    subprocess.run([
        "netconvert",
        "--osm-files", osm_path,
        "--output-file", output_net,
        "--geometry.remove",
        "--roundabouts.guess",
        "--ramps.guess",
        "--junctions.join",
        "--tls.guess-signals",
        "--tls.discard-simple",
        "--tls.join",
    ], check=True)
    print(f"Generated {output_net}")

    # 3. Generate random vehicle routes for simulation
    sumo_random_trips = os.path.join(os.environ.get('SUMO_HOME', ''), 'tools', 'randomTrips.py')
    if not os.path.exists(sumo_random_trips):
        # fallback for common windows paths if environment variable is missing
        for fb in [
            "C:/Program Files/Eclipse/Sumo/tools/randomTrips.py",
            "C:/Program Files (x86)/Eclipse/Sumo/tools/randomTrips.py",
            "D:/SUMO/tools/randomTrips.py",
        ]:
            if os.path.exists(fb):
                sumo_random_trips = fb
                break

    subprocess.run([
        "py", sumo_random_trips,
        "-n", output_net,
        "-o", os.path.join(OUT_DIR, "trips.xml"),
        "--route-file", output_routes,
        "-b", "0", "-e", "3600",
        "--period", "2",
        "--validate",
    ], check=True)
    print(f"Generated {output_routes}")


if __name__ == "__main__":
    # 1. Download road graph from OpenStreetMap
    print("Downloading Mangalore road network from OSM (using a 2km radius)...")
    G = ox.graph_from_point((CENTER_LAT, CENTER_LON), dist=RADIUS_METERS, network_type="drive", simplify=False)
    osm_file = f"{OUT_DIR}/mangalore.osm"
    ox.save_graph_xml(G, filepath=osm_file)
    print(f"Saved {osm_file}")

    generate_sumo_network(
        osm_path=osm_file,
        output_net=f"{OUT_DIR}/mangalore.net.xml",
        output_routes=f"{OUT_DIR}/routes.xml"
    )
    print("Done. Now run: py src/controller.py")
