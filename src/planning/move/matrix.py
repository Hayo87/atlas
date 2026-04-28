# matrix.py

import numpy as np
import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
from src.models.models import MovementMode


# Find nearest node in network
def snap_locations(G, locations):
    lons = [loc["lon"] for loc in locations]
    lats = [loc["lat"] for loc in locations]

    node_ids = ox.distance.nearest_nodes(G, X=lons, Y=lats)

    for loc, node_id in zip(locations, node_ids):
        loc["node_id"] = node_id

    return locations


# Main entry point
def build_cost_matrix_for_vehicle(G, locations, vehicle):
    cost_fn = _get_cost_fn(G, vehicle)
    return _build_matrix(locations, cost_fn)


def _get_cost_fn(G, vehicle):
    if vehicle.profile.movement_mode == MovementMode.AIR:
        return lambda a, b: geodesic(
            (a["lat"], a["lon"]),
            (b["lat"], b["lon"])
        ).meters

    return lambda a, b: nx.shortest_path_length(
        G,
        a["node_id"],
        b["node_id"],
        weight="length",
    )


def _build_matrix(locations, cost_fn):
    return np.array([
        [0 if i == j else int(cost_fn(a, b))
         for j, b in enumerate(locations)]
        for i, a in enumerate(locations)
    ])
