from pathlib import Path
import folium
import networkx as nx
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

def plot_routes_folium(G, locations, routes):
    location_by_id = {loc["id"]: loc for loc in locations}

    center = [
        sum(loc["lat"] for loc in locations) / len(locations),
        sum(loc["lon"] for loc in locations) / len(locations),
    ]

    m = folium.Map(location=center, zoom_start=10)

    icon_dir = Path(__file__).parent / "icons"

    # Markers
    for loc in locations:
        icon_file = "vehicle_start.png" if loc.get("type") == "vehicle_start" else "job.png"

        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            popup=loc["id"],
            icon=folium.CustomIcon(str(icon_dir / icon_file), icon_size=(32, 32)),
        ).add_to(m)

    colors = ["red", "blue", "green", "purple", "orange"]

    # Routes
    for idx, route in enumerate(routes):
        color = colors[idx % len(colors)]
        route_ids = route["route"]
        vehicle_type = route.get("vehicle_type")

        for a, b in zip(route_ids[:-1], route_ids[1:]):
            origin = location_by_id[a]
            dest = location_by_id[b]

            if vehicle_type == "drone":
                coords = [
                    [origin["lat"], origin["lon"]],
                    [dest["lat"], dest["lon"]],
                ]
            else:
                path = nx.shortest_path(
                    G,
                    origin["node_id"],
                    dest["node_id"],
                    weight="length",
                )
                coords = [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in path]

            folium.PolyLine(
                coords,
                color=color,
                weight=5,
                opacity=0.8,
                popup=route["vehicle_id"],
            ).add_to(m)

    return m


def plot_routes_kepler(G, locations, routes):
    from keplergl import KeplerGl

    location_by_id = {loc["id"]: loc for loc in locations}

    # Points
    points_df = pd.DataFrame(locations)

    # Lines
    lines = []

    for route in routes:
        route_ids = route["route"]
        vehicle_type = route.get("vehicle_type")

        for a, b in zip(route_ids[:-1], route_ids[1:]):
            origin = location_by_id[a]
            dest = location_by_id[b]

            if vehicle_type == "drone":
                coords = [
                    (origin["lon"], origin["lat"]),
                    (dest["lon"], dest["lat"]),
                ]
            else:
                path = nx.shortest_path(
                    G,
                    origin["node_id"],
                    dest["node_id"],
                    weight="length",
                )
                coords = [
                    (G.nodes[n]["x"], G.nodes[n]["y"])
                    for n in path
                ]

            lines.append({
                "vehicle_id": route["vehicle_id"],
                "vehicle_type": vehicle_type,
                "geometry": LineString(coords),
            })

    routes_gdf = gpd.GeoDataFrame(lines, geometry="geometry", crs="EPSG:4326")

    m = KeplerGl(height=700)
    m.add_data(points_df, "locations")
    m.add_data(routes_gdf, "routes")

    return m