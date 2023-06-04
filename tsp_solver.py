from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import googlemaps
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


class TSPSolver:

    def __init__(self, route_info):
        # TODO -> implement error handling

        self.old_url = route_info.url
        self.travel_mode = route_info.travel_mode
        self.fixed_start_point = route_info.fixed_start_point
        self.fixed_end_point = route_info.fixed_end_point

        parts = urlparse(self.old_url)
        
        self.base_url = parts.scheme + "://" + parts.netloc
        self.directories = parts.path.strip('/').split('/')
        try:
            at_index = list(map(lambda x: "@" in x, self.directories)).index(True)
            self.destinations = self.directories[2:at_index]
        except:
            self.destinations = self.directories[2:]
        

    def solver(self, matrix_type):
        # TODO -> implement error handling

        self.data = self.create_data_model(matrix_type)

        # Create the routing index manager.
        self.manager = pywrapcp.RoutingIndexManager(len(self.data[matrix_type]),
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
            return self.data[matrix_type][from_node][to_node]

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

    def qs_constructor(self):
        
        self.solution_arr_str = list(
            filter(lambda x: x != -1, map(lambda x: x - 1, self.solution_arr)))
        solution_str = [self.destinations[i] for i in self.solution_arr_str]

        url = self.directories[:2] + solution_str
        url = [self.base_url, *url]
        
        self.new_url = "/".join(url)

        new_distance, old_distance, new_duration, old_duration = 0, 0, 0, 0

        # need to take into account that self.solution_arr will be longer if both fixed start/end deselected
        x = 1
        if self.fixed_start_point == None and self.fixed_end_point == None:
            x = 2

        print(x)
        print(len(self.solution_arr))
        print(self.solution_arr)
        print(len(self.data["duration_matrix"]))
        print(self.data["duration_matrix"])
        print(len(self.data["distance_matrix"]))
        print(self.data["distance_matrix"])

        for i in range(len(self.solution_arr)-x):
            new_duration += self.data["duration_matrix"][self.solution_arr[i]][self.solution_arr[i+1]]
            old_duration += self.data["duration_matrix"][i][i+1]

            new_distance += self.data["distance_matrix"][self.solution_arr[i]][self.solution_arr[i+1]]
            old_distance += self.data["distance_matrix"][i][i+1]
            
        self.distance_diff = old_distance - new_distance
        self.duration_diff = old_duration - new_duration

    def create_data_model(self, matrix_type):
        """Stores the data for the problem."""
        data = {}
        data['distance_matrix'], data['duration_matrix'] = self.create_matrices()  # yapf: disable
        data['num_vehicles'] = 1
        if self.fixed_start_point == "on":
            data['starts'] = [1]
        else:
            data['starts'] = [0]
        if self.fixed_end_point == "on":
            data['ends'] = [len(data[matrix_type]) - 1]
        else:
            data['ends'] = [0]
        return data

    def create_matrices(self):
        gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
        matrix = gmaps.distance_matrix(
            self.destinations, self.destinations, mode=self.travel_mode)
        distance_matrix = [[0] * (len(self.destinations) + 1)]
        duration_matrix = [[0] * (len(self.destinations) + 1)]
        for i in range(len(self.destinations)):
            distance_row = [0]
            duration_row = [0]
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
        index = self.routing.Start(0)
        plan_output = []
        while not self.routing.IsEnd(index):
            plan_output.append(self.manager.IndexToNode(index))
            index = self.solution.Value(self.routing.NextVar(index))
        plan_output.append(self.manager.IndexToNode(index))
        return plan_output
