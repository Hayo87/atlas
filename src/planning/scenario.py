from src.models.models import Vehicle, VehicleState, Location
from src.models.catalog import JEEP, DRONE
from src.planning.move.matrix import snap_locations


PROFILES = {
    "jeep": JEEP,
    "drone": DRONE,
}
BASE_PENALTY = 10_0000


def unit(id, type, lat, lon, range_left=None, payload_left=0,end_lat=None, end_lon=None,):
    return {
        "id": id,
        "type": type,
        "lat": lat,
        "lon": lon,
        "range_left": range_left,
        "payload_left": payload_left,
        "end_lat": end_lat,
        "end_lon": end_lon,
    }


def job(id, lat, lon, demand=0, priority=1):
    return {
        "id": id,
        "lat": lat,
        "lon": lon,
        "demand": demand,
        "priority": priority,
    }


def create_vehicle(u, start_index):
    profile = PROFILES[u["type"]]

    return Vehicle(
        id=u["id"],
        profile=profile,
        location=Location(lat=u["lat"], lon=u["lon"]),
        start_index=start_index,
        end_index=start_index,
        state=VehicleState(
            range_left=u["range_left"] if u["range_left"] is not None else profile.max_range,
            payload_left=u["payload_left"],
        ),
    )


def vehicle_to_solver(v):
    return {
        "id": v.id,
        "type": v.profile.name,
        "start_index": v.start_index,
        "end_index": v.end_index,
        "range_left": v.state.range_left,
        "payload_left": v.state.payload_left,
    }


def prepare_scenario(units, jobs, G=None):
    locations = []
    vehicles = []

    for u in units:
        start_index = len(locations)

        locations.append({
            "id": u["id"],
            "type": "vehicle_start",
            "lat": u["lat"],
            "lon": u["lon"],
            "demand": 0,
        })

        vehicle = create_vehicle(u, start_index)

        # end
        if u["end_lat"] is None:
            vehicle.end_index = start_index
        else:
            end_index = len(locations)

            locations.append({
                "id": f"{u['id']}_end",
                "type": "vehicle_end",
                "lat": u["end_lat"],
                "lon": u["end_lon"],
                "demand": 0,
            })

            vehicle.end_index = end_index

        vehicles.append(vehicle)



    for j in jobs:
        priority = j.get("priority", 1)

        locations.append({
            "id": j["id"],
            "type": "job",
            "lat": j["lat"],
            "lon": j["lon"],
            "demand": j["demand"],
            "priority": priority,
            "penalty": priority * BASE_PENALTY,
        })

    if G is not None:
        locations = snap_locations(G, locations)

    solver_units = [vehicle_to_solver(v) for v in vehicles]

    return locations, vehicles, solver_units