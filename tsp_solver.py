from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import googlemaps
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import requests

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


class TSPSolver:

    def __init__(self, url):
        # TODO -> implement error handling
        parts = urlparse(url)
        self.base_url = parts.scheme + "://" + parts.netloc
        self.directories = parts.path.strip('/').split('/')
        self.destinations = self.directories[2:-2]

    def solver(self, destinations, route_info):
        """Entry point of the program."""
        # TODO -> implement error handling

        self.destinations = destinations
        self.route_info = route_info
        self.data = self.create_data_model(self.destinations, self.route_info)

        # Create the routing index manager.
        self.manager = pywrapcp.RoutingIndexManager(len(self.data['distance_matrix']),
                                                    self.data['num_vehicles'],
                                                    self.data['starts'],
                                                    self.data['ends'])

        # Create Routing Model.
        self.routing = pywrapcp.RoutingModel(self.manager)

        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            return self.data['distance_matrix'][from_node][to_node]

        transit_callback_index = self.routing.RegisterTransitCallback(
            distance_callback)

        # Define cost of each arc.
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # Solve the problem.
        self.solution = self.routing.SolveWithParameters(search_parameters)

        # Print solution on console.
        self.solution_arr = self.create_solution_arr()

    def create_data_model(self):
        """Stores the data for the problem."""
        data = {}
        data['distance_matrix'], data['duration_matrix'] = self.create_matrices(
            self.destinations, self.route_info)  # yapf: disable
        data['num_vehicles'] = 1
        if self.route_info.fixed_start_point == "on":
            data['starts'] = [1]
        else:
            data['starts'] = [0]
        if self.route_info.fixed_end_point == "on":
            data['ends'] = [len(data['distance_matrix']) - 1]
        else:
            data['ends'] = [0]
        return data

    def create_matrices(self):
        gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
        matrix = gmaps.distance_matrix(
            self.destinations, self.destinations, mode=self.route_info.travel_mode)
        distance_matrix = [[0] * (len(self.destinations) + 1)]
        duration_matrix = []
        for i in range(len(self.destinations)):
            distance_row = [0]
            duration_row = []
            for j in range(len(self.destinations)):
                distance_row.append(
                    matrix["rows"][i]["elements"][j]["distance"]["value"])
                duration_row.append(
                    matrix["rows"][i]["elements"][j]["duration"]["value"])
            distance_matrix.append(distance_row)
            duration_matrix.append(duration_row)
        return distance_matrix, duration_matrix

    def create_solution_arr(self):
        """Prints solution on console."""
        # distance = self.solution.ObjectiveValue()
        index = self.routing.Start(0)
        plan_output = []
        route_distance = 0
        while not self.routing.IsEnd(index):
            plan_output.append(self.manager.IndexToNode(index))
            previous_index = index
            index = self.solution.Value(self.routing.NextVar(index))
            route_distance += self.routing.GetArcCostForVehicle(
                previous_index, index, 0)
        plan_output.append(self.manager.IndexToNode(index))
        return plan_output  # distance, route_distance

    def qs_constructor(self):
        self.solution_arr_update = list(
            filter(lambda x: x != -1, map(lambda x: x - 1, self.solution_arr)))
        solution = [self.destinations[i] for i in self.solution_arr_update]

        new_distance, old_distance, new_duration, old_duration = 0, 0, 0, 0

        # check for what number self.solution_arr should be subtracted by, if fixed_start_point and fixed_end_point both have values == "on", if needs to be 2, else 1

        # need to take into account that self.solution_arr will be longer if fixed start/end selected
        for i in range(len(self.solution_arr)-1):
            new_distance += self.data["distance_matrix"][self.solution_arr[i]
                                                         ][self.solution_arr[i+1]]
            # probably causing it to go oob as data matrix and self.solution_arr have different lengths
            old_distance += self.data["distance_matrix"][i][i+1]

        for i in range(len(self.solution_arr_update)-1):
            new_duration += self.data["duration_matrix"][self.solution_arr_update[i]
                                                         ][self.solution_arr_update[i+1]]

            old_duration += self.data["duration_matrix"][i][i+1]

        print(len(self.data["distance_matrix"]), len(self.solution_arr))
        print(new_distance, old_distance, new_duration, old_duration)

        distance_diff = old_distance - new_distance
        duration_diff = old_duration - new_duration

        print(distance_diff, duration_diff)

        # + directories[-2:-1]
        self.solution_url = self.directories[:2] + solution
        self.solution_url = [self.base_url, *self.solution_url]
        self.solution_url = "/".join(self.solution_url)
        return self.solution_url, solution
