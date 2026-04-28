def add_capacity(solver):
    demands = [loc.get("demand", 0) for loc in solver.locations]
    capacities = [v["payload_left"] for v in solver.vehicles]

    def demand_callback(from_index):
        node = solver.manager.IndexToNode(from_index)
        return int(demands[node])

    callback_id = solver.routing.RegisterUnaryTransitCallback(demand_callback)

    solver.routing.AddDimensionWithVehicleCapacity(
        callback_id,
        0,          # no slack
        capacities,
        True,       # start load at zero
        "Capacity",
    )

def add_range_limit(solver):
    ranges = [int(v["range_left"]) for v in solver.vehicles]

    solver.routing.AddDimensionWithVehicleTransitAndCapacity(
        solver.transit_callback_ids,
        0,       # no slack
        ranges,  # max distance per vehicle
        True,    # start at zero
        "Range",
    )

def add_optional_jobs(solver):
    for i, loc in enumerate(solver.locations):
        if loc["type"] == "job":
            penalty = int(loc["penalty"])

            solver.routing.AddDisjunction(
                [solver.manager.NodeToIndex(i)],
                penalty,
            )