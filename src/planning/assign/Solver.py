from ortools.constraint_solver import pywrapcp, routing_enums_pb2

class Solver:
    def __init__(self, locations, vehicles, cost_matrices):
        self.locations = locations
        self.vehicles = vehicles
        self.cost_matrices = cost_matrices
        self.manager = None
        self.routing = None
        self.solution = None

    def build(self):
        starts = [v["start_index"] for v in self.vehicles]
        ends = [v.get("end_index", v["start_index"]) for v in self.vehicles]

        self.manager = pywrapcp.RoutingIndexManager(
            len(self.locations), len(self.vehicles), starts, ends
        )
        self.routing = pywrapcp.RoutingModel(self.manager)

        self.transit_callback_ids = []

        for vehicle_id, vehicle in enumerate(self.vehicles):
            matrix = self.cost_matrices[vehicle["type"]]

            def cost_cb(from_i, to_i, matrix=matrix):
                return int(matrix[
                    self.manager.IndexToNode(from_i)
                ][
                    self.manager.IndexToNode(to_i)
                ])

            cb_id = self.routing.RegisterTransitCallback(cost_cb)
            self.transit_callback_ids.append(cb_id)

            self.routing.SetArcCostEvaluatorOfVehicle(cb_id, vehicle_id)

        return self

    def solve(self, time_limit=10):
        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        params.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        params.time_limit.seconds = time_limit

        self.solution = self.routing.SolveWithParameters(params)
        return self.decode()

    def decode(self):
        if self.solution is None:
            return None

        return [
            self._decode_vehicle(vehicle_id, vehicle)
            for vehicle_id, vehicle in enumerate(self.vehicles)
        ]

    def _decode_vehicle(self, vehicle_id, vehicle):
        index = self.routing.Start(vehicle_id)
        route = []
        total_cost = 0

        while not self.routing.IsEnd(index):
            route.append(self.locations[self.manager.IndexToNode(index)]["id"])

            prev = index
            index = self.solution.Value(self.routing.NextVar(index))
            total_cost += self.routing.GetArcCostForVehicle(prev, index, vehicle_id)

        route.append(self.locations[self.manager.IndexToNode(index)]["id"])

        return {
            "vehicle_id": vehicle["id"],
            "vehicle_type": vehicle["type"],
            "route": route,
            "total_cost": total_cost,
        }
    