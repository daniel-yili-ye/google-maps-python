from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def create_data_model(destinations):
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = get_distance_matrix(destinations)  # yapf: disable
    data['num_vehicles'] = 1
    data['starts'] = [0]
    data['ends'] = [len(data['distance_matrix']) - 1]
    return data

def get_distance_matrix(destinations):
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    matrix = gmaps.distance_matrix(destinations, destinations)
    distance_matrix = []
    for i in range(len(destinations)):
        sd = []
        for j in range(len(destinations)):
            sd.append(matrix["rows"][i]["elements"][j]["distance"]["value"])
        distance_matrix.append(sd)
    return distance_matrix

def get_solution(manager, routing, solution):
    """Prints solution on console."""
    distance = solution.ObjectiveValue()
    index = routing.Start(0)
    plan_output = []
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output.append(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output.append(manager.IndexToNode(index))
    return plan_output, distance #, route_distance

def main(destinations):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(destinations)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], 
                                           data['starts'], 
                                           data['ends'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        return get_solution(manager, routing, solution)