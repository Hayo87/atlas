from pathlib import Path
import osmnx as ox

# Demo area
WEST, SOUTH, EAST, NORTH = 22.60, 53.85, 23.95, 54.55
NETWORK_TYPE = "drive"

def load_network():
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)

    graph_path = cache_dir / "network.graphml"

    if graph_path.exists():
        G = ox.load_graphml(graph_path)
    else:
        bbox = (WEST, SOUTH, EAST, NORTH)

        G = ox.graph.graph_from_bbox(
            bbox,
            network_type="drive",
            simplify=True
        )
        ox.save_graphml(G, graph_path)
    return G

def enrich_network(G):
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    return G