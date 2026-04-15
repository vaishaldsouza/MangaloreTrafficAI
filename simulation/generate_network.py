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

# 2. Convert OSM -> SUMO network using netconvert
print("Converting to SUMO network...")
subprocess.run([
    "netconvert",
    "--osm-files", f"{OUT_DIR}/mangalore.osm",
    "--output-file", f"{OUT_DIR}/mangalore.net.xml",
    "--geometry.remove",
    "--roundabouts.guess",
    "--ramps.guess",
    "--junctions.join",
    "--tls.guess-signals",
    "--tls.discard-simple",
    "--tls.join",
], check=True)
print("Generated mangalore.net.xml")

# 3. Generate random vehicle routes for simulation
sumo_random_trips = os.path.join(os.environ.get('SUMO_HOME', ''), 'tools', 'randomTrips.py')
subprocess.run([
    "py", sumo_random_trips,
    "-n", f"{OUT_DIR}/mangalore.net.xml",
    "-o", f"{OUT_DIR}/trips.xml",
    "--route-file", f"{OUT_DIR}/routes.xml",
    "-b", "0", "-e", "3600",   # 1 hour
    "--period", "2",            # vehicle every 2 seconds
    "--validate",
], check=True)
print("Generated routes.xml")
print("Done. Now run: py src/controller.py")
