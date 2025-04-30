import pprint
import time
import heapq
import math
import requests


import networkx as nx
import matplotlib.pyplot as plt
last_visualized_path = None


# Configuration
server_ip = "10.216.146.79"
server_port = 5000
authKey = 44
team = 44

# Dictionary of nodes based on map intersections
nodes = {
    0:  {"label": "Aquatic Ave. & Beak St.",       "x": 452, "y":  29},
    1:  {"label": "Aquatic Ave. & Feather St.",    "x": 305, "y":  29},
    2:  {"label": "Aquatic Ave. & Waddle Way",     "x": 129, "y":  29},
    3:  {"label": "Aquatic Ave. & Waterfoul Way",  "x": 213, "y":  29},
    29: {"label": "Aquatic Ave. & Quack St.",      "x": 29,  "y":  29}, #estimated
    30: {"label": "Aquatic Ave. & Mallard St.",    "x": 585, "y":  29}, #estimated

    4:  {"label": "Breadcrumb Ave. & The Circle",  "x": 284, "y": 393},
    5:  {"label": "Breadcrumb Ave. & Waddle Way",  "x": 181, "y": 459},
    31: {"label": "Breadcrumb Ave. & Quack St.",   "x": 29,  "y": 459}, #estimated

    6:  {"label": "Dabbler Dr. & Beak St.",        "x": 452, "y": 293},
    7:  {"label": "Dabbler Dr. & The Circle",      "x": 350, "y": 324},
    8:  {"label": "Dabbler Dr. & Mallard St.",     "x": 585, "y": 293},

    9:  {"label": "Drake Dr. & Beak St.",          "x": 452, "y": 402},
    10: {"label": "Drake Dr. & Mallard St.",       "x": 576, "y": 354},

    11: {"label": "Duckling Dr. & Beak St.",       "x": 452, "y": 474},
    12: {"label": "Duckling Dr. & Mallard St.",    "x": 593, "y": 354},

    13: {"label": "Migration Ave. & Beak St.",     "x": 452, "y": 135},
    14: {"label": "Migration Ave. & Feather St.",  "x": 305, "y": 135},
    15: {"label": "Migration Ave. & Mallard St.",  "x": 585, "y": 135},
    16: {"label": "Migration Ave. & Quack St.",    "x":  29, "y": 135},
    17: {"label": "Migration Ave. & Waddle Way",   "x": 129, "y": 135},
    18: {"label": "Migration Ave. & Waterfoul Way","x": 213, "y": 135},

    19: {"label": "Pondside Ave. & Beak St.",      "x": 452, "y": 233},
    20: {"label": "Pondside Ave. & Feather St.",   "x": 305, "y": 233},
    21: {"label": "Pondside Ave. & Mallard St.",   "x": 585, "y": 233},
    22: {"label": "Pondside Ave. & Quack St.",     "x":  28, "y": 329},
    23: {"label": "Pondside Ave. & Waterfoul Way", "x": 214, "y": 241},
    24: {"label": "Pondside Ave. & Waddle Way",    "x": 157, "y": 266},

    25: {"label": "Tail Ave. & Beak St.",          "x": 452, "y": 465},
    26: {"label": "Tail Ave. & The Circle",        "x": 335, "y": 387},

    27: {"label": "Feather St. & The Circle",      "x": 305, "y": 296},
    28: {"label": "Waterfoul Way & The Circle",    "x": 273, "y": 307}
}

# Creating adjacency list
graph = { i: [] for i in nodes.keys() }

# 1) Compute Euclidean distance between node a and node b
def dist(a, b):
    dx = nodes[a]["x"] - nodes[b]["x"]
    dy = nodes[a]["y"] - nodes[b]["y"]
    return math.hypot(dx, dy)

# 4) Add edge with direction parameter
def add_edge(u, v, two_way=True):
    #add an edge from u->v. If two_way=True, also add v->u.
    d = dist(u, v)
    graph[u].append((v, d))
    if two_way:
        graph[v].append((u, d))

def add_sequence(seq, two_way=True):
    #add edges for each consecutive pair in seq.
    for i in range(len(seq) - 1):
        add_edge(seq[i], seq[i+1], two_way=two_way)

def add_sequence_reversed(seq, two_way=False):
    rseq = list(reversed(seq))
    add_sequence(rseq, two_way=two_way)

# 5) Define roads in physical order (left->right or bottom->top):
aquatic_ave       = [29, 2, 3, 1, 0, 30]
breadcrumb_ave    = [31, 5, 4]
dabbler_dr        = [7, 6, 8]
drake_dr          = [9, 10]
duckling_dr       = [11, 12]
migration_ave     = [16, 17, 18, 14, 13, 15]
pondside_ave      = [22, 24, 23, 20, 19, 21]
tail_ave          = [26, 25]
beak_st           = [0, 13, 19, 6, 9, 11]
feather_st        = [1, 14, 20, 27]
mallard_st        = [30, 15, 21, 8, 10, 12]
quack_st          = [29, 16, 22, 31]
waterfoul_way     = [3, 18, 23, 28]
waddle_way        = [2, 17, 24, 5]
the_circle        = [4, 28, 27, 7, 26]

# 6) Roads in physical order (left->right or bottom->top)
roads_info = [
    (aquatic_ave,    True),
    (breadcrumb_ave, True),
    (drake_dr,       False),
    (migration_ave,  True),
    (pondside_ave,   True),
    (tail_ave,       True),
    (beak_st,        True),
    (feather_st,     True),
    (waterfoul_way,  False),
    (mallard_st,     True),
    (quack_st,       True),
]

# 7) Add two-way or one-way edges for each
for road_sequence, is_two_way in roads_info:
    add_sequence(road_sequence, two_way=is_two_way)

# Add one ways for R->L or T->B
add_sequence_reversed(waddle_way, two_way=False)
add_sequence_reversed(dabbler_dr, two_way=False)
add_sequence_reversed(duckling_dr, two_way=False)

def add_ring(ring, two_way=False):
    n = len(ring)
    for i in range(n):
        u = ring[i]
        v = ring[(i + 1) % n]  # next, wrapping around
        add_edge(u, v, two_way=two_way)

add_ring(the_circle, two_way=False)

# 9) Print the final adjacency list
pprint.pprint(graph)

# Old graph vizualization code
'''
# ---------------------------
# Start of Visualization Code
# ---------------------------
import networkx as nx
import matplotlib.pyplot as plt

def visualize_graph(graph, nodes):
    
    #Builds and displays a NetworkX graph from the adjacency list (graph)
    #and node positions (nodes).
    
    G = nx.Graph()

    # 1. Add nodes
    for node_id in graph:
        G.add_node(node_id)

    # 2. Add edges
    for node_id, edges in graph.items():
        for (nbr, dist_val) in edges:
            # NetworkX won't double-count an edge if it's already added in the opposite direction
            G.add_edge(node_id, nbr, weight=dist_val)

    # 3. Prepare positions
    pos = {}
    for n_id, data in nodes.items():
        pos[n_id] = (data["x"], data["y"])

    # 4. Draw the graph using the given positions
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=500)

    # Optionally, draw edge labels for distances
    edge_labels = {}
    for (u, v, w) in G.edges(data='weight'):
        edge_labels[(u, v)] = f"{w:.1f}"  # one decimal place
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title("Map Graph Visualization")
    plt.axis('equal')  # Equal scaling on x/y axis
    plt.show()

# Call the visualization function
visualize_graph(graph, nodes)
# ---------------------------
# END of Visualization Code
'''

def main_loop():
    while True:
        # 1. Check match status
        match_data = check_match_status(server_ip, server_port, authKey)
        # If match_data is None (error) or inMatch is False or time is up, wait
        if (not match_data 
            or not match_data.get('inMatch') 
            or match_data.get('timeRemain', 0) <= 0):
            print("Waiting for match to start")
            time.sleep(2)
            continue

        # 2. Check if we already have a fare
        fare_status = get_current_fare(team)
        # If we have an active fare, handle it; otherwise try to claim a new fare
        if fare_status and fare_status.get('fare') is not None:
            handle_active_fare(fare_status['fare'])
        else:
            claim_a_fare()

        time.sleep(1)

# Checks the current match status from the VPFS server.
def check_match_status(server_ip, server_port, authKey):

    endpoint = f"http://{server_ip}:{server_port}/match?auth={authKey}"
    try:
        response = requests.get(endpoint, timeout=10)
        # If HTTP status not 2xx, raise an exception here
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error contacting /match endpoint: {e}")
        return None

    # Parse JSON response
    try:
        data = response.json()
    except ValueError as e:
        print(f"Error parsing JSON from /match endpoint: {e}")
        return None

    # Debug output
    if not data.get('inMatch'):
        print("Match Status: Your team is not currently in a match.")
    else:
        if not data.get('matchStart'):
            print(f"Match {data.get('match')} is set up but has not started yet.")
        else:
            print(f"Match {data.get('match')} is active.")
            time_remain = data.get('timeRemain', 0)
            if time_remain > 0:
                print(f"Time Remaining: {time_remain} seconds.")
            else:
                print("No time remaining in match")

    return data

# Retrieves the list of available fares, picks one to claim, and attempts to claim it.
def claim_a_fare():
  
    # 1. Get list of fares
    endpoint = f"http://{server_ip}:{server_port}/fares"
    try:
        r = requests.get(endpoint, timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error contacting /fares endpoint: {e}")
        return

    # 2. Parse JSON for fares
    try:
        fares = r.json()
    except ValueError as e:
        print(f"Error parsing JSON from /fares: {e}")
        return

    # 3. Choose a fare
    best_fare = pick_best_fare(fares)
    if not best_fare:
        print("No fare found")
        return

    # 4. Attempt to claim fare
    claim_endpoint = f"http://{server_ip}:{server_port}/fares/claim/{best_fare['id']}?auth={authKey}"
    try:
        r_claim = requests.get(claim_endpoint, timeout=10)
        r_claim.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error contacting /fares/claim endpoint: {e}")
        return

    # 5. Parse JSON response from the claim attempt
    try:
        data = r_claim.json()
    except ValueError as e:
        print(f"Error parsing JSON from /fares/claim: {e}")
        return

    # 6. Check if the claim was successful
    if data.get('success'):
        print(f"Successfully claimed fare {best_fare['id']}")
    else:
        print(f"Failed to claim fare {best_fare['id']}. Reason: {data.get('message', 'Unknown')}")


def handle_active_fare(fare_data):
    # Check if duck is picked up
    if not fare_data['pickedUp']:
        # Navigate to duck
        navigate_to(fare_data['src']['x'], fare_data['src']['y'])
    else:
        # Deliver duck
        if not fare_data['completed']:
            navigate_to(fare_data['dest']['x'], fare_data['dest']['y'])
        else:
            print("Fare completed, waiting for payment or new fare")
            claim_a_fare()

# Plans path from current position, returning list of node coordinates (intersecrions) to follow
def navigate_to(x, y):
    global last_visualized_path

    # 1. Get current position
    pos = get_vehicle_position(team)
    if not pos:
        print("No GPS data, can't navigate yet")
        return
    x_me, y_me = pos

    # 2. Compute path in graph
    path = plan_path(x_me, y_me, x, y, nodes, graph)
    if not path:
        print("No path to target found")
        return

    # ******   3. Send path to Local Path Planning  ********
    print(f"Navigating from ({x_me}, {y_me}) to ({x}, {y}) via {len(path)} waypoints.")
    print(path)
    print(interpret_turns(path))

    # Call path visualization for debugging (uncomment for graph visualization)
    if path != last_visualized_path:
        visualize_graph_with_path(graph, nodes, path)
        last_visualized_path = path

#Return the JSON from /fares/current/<team>, or None on error.
def get_current_fare(team):
    
    endpoint = f"http://{server_ip}:{server_port}/fares/current/{team}"
    try:
        r = requests.get(endpoint, timeout=5)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error contacting /fares/current endpoint: {e}")
        return None

    try:
        return r.json()
    except ValueError as e:
        print(f"Error parsing JSON from /fares/current: {e}")
        return None

#Return (x, y) from the /WhereAmI/<team> endpoint, or None on error.
def get_vehicle_position(team):

    endpoint = f"http://{server_ip}:{server_port}/whereami/{team}"
    try:
        r = requests.get(endpoint, timeout=5)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error contacting /WhereAmI endpoint: {e}")
        return None

    try:
        data = r.json()
    except ValueError as e:
        print(f"Error parsing JSON from /WhereAmI: {e}")
        return None

    if 'position' in data:
        return(data['position'][0]['x'], data['position'][0]['y'])
    return None

#Fare selection logic 
def pick_best_fare(fares):
    # Returning None means no fare gets claimed.

    #Temporary slection method (highest pay) for testing purposes
    unclaimed = [f for f in fares if not f["claimed"]]
    if not unclaimed:
        return None
    return max(unclaimed, key=lambda f: f["pay"])

    """
    Closest Fare selection method:

        # Returning None means no fare gets claimed.
    unclaimed = [f for f in fares if not f["claimed"]]
    if not unclaimed:
        return None

     # Get the current vehicle position (x, y)
    current_pos = get_vehicle_position(team)
    if current_pos is None:
        print("Error: Unable to retrieve vehicle position")
        return None
        
    x_me, y_me = current_pos
    best_fare = None
    min_distance = float('inf')
    
    for fare in unclaimed:
        fare_src = fare.get('src', {})
        if 'x' in fare_src and 'y' in fare_src:
            # Calculate Euclidean distance from the vehicle to the fare's pickup point
            distance = math.hypot(fare_src['x'] - x_me, fare_src['y'] - y_me)
            if distance < min_distance:
                min_distance = distance
                best_fare = fare
        else:
            print(f"Warning: Fare {fare.get('id', 'unknown')} missing source coordinates.")
    
    return best_fare

    """



def plan_path(current_x, current_y, target_x, target_y, nodes, graph):

    # 1. Add a temporary node for the vehicle position
    start_temp_id = add_temporary_node(current_x, current_y, nodes, graph)

    # 2. Add a temporary node for the target location
    goal_temp_id = add_temporary_node(target_x, target_y, nodes, graph, node_id_start=start_temp_id + 1)

    # 3. Run Dijkstra algorithm (shortest path)
    dist, path_node_ids = dijkstra(graph, start_temp_id, goal_temp_id)

    if dist == float('inf'):
        print("No route found")
        # Remove temp nodes
        remove_temporary_node(start_temp_id, nodes, graph)
        remove_temporary_node(goal_temp_id, nodes, graph)
        return []

    # 4. Convert path of node IDs to list of (x, y) coordinates
    waypoints = [(nodes[nid]['x'], nodes[nid]['y']) for nid in path_node_ids]

    # 5. Remove temp nodes
    remove_temporary_node(start_temp_id, nodes, graph)
    remove_temporary_node(goal_temp_id, nodes, graph)

    # 6. Return the waypoints
    return waypoints #*** SEND TO LOCAL PATH NAVIGATION? ***


def euclidiean_distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def add_temporary_node(x, y, nodes, graph, node_id_start=1000):
    # 1. Determine a unique ID
    new_id = node_id_start
    while new_id in nodes:
        new_id += 1

    # 2. Insert temp node into the 'nodes' dictionary
    nodes[new_id] = {'x': x, 'y': y}

    # 3. Find the single nearest intersection
    min_dist = float('inf')
    nearest_node = None
    for nid, data in nodes.items():
        if nid == new_id:
            continue
        d = euclidiean_distance(x, y, data['x'], data['y'])
        if d < min_dist:
            min_dist = d
            nearest_node = nid

    # 4. Connect new node to nearest intersection (undirected)
    graph[new_id] = []
    if nearest_node is not None:
        graph[new_id].append((nearest_node, min_dist))
        graph[nearest_node].append((new_id, min_dist))

    return new_id


def remove_temporary_node(node_id, nodes, graph):
    if node_id in nodes:
        del nodes[node_id]

    if node_id in graph:
        # Remove edges referencing this node
        for n, edges in graph.items():
            if n != node_id:
                new_edges = [(nbr, w) for (nbr, w) in edges if nbr != node_id]
                graph[n] = new_edges
        del graph[node_id]


def dijkstra(graph, start_id, goal_id):

    # Initialize distances
    dist = {n: float('inf') for n in graph}
    dist[start_id] = 0.0
    prev = {n: None for n in graph}

    # Min-heap for frontier
    heap = [(0.0, start_id)]

    while heap:
        current_dist, current_node = heapq.heappop(heap)

        if current_node == goal_id:
            # Found shortest path to goal
            break

        # If outdated, skip
        if current_dist > dist[current_node]:
            continue

        # Explore neighbors
        for (nbr, weight) in graph[current_node]:
            alt_dist = current_dist + weight
            if alt_dist < dist[nbr]:
                dist[nbr] = alt_dist
                prev[nbr] = current_node
                heapq.heappush(heap, (alt_dist, nbr))

    # If goal is unreachable, distance stays inf
    if dist[goal_id] == float('inf'):
        return float('inf'), []

    # Reconstruct path
    path = []
    node = goal_id
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()

    return dist[goal_id], path

def interpret_turns(waypoints, threshold_degrees=10):
    """
    Given a list of waypoints (each a tuple (x, y)), interpret the turns
    at each intermediate intersection as 'left turn', 'right turn', or 'go straight',
    and return the magnitude of the turn in degrees.
    
    Parameters:
        waypoints (list of tuple): List of (x, y) coordinates.
        threshold_degrees (float): Angle (in degrees) under which to consider the direction change negligible.
        
    Returns:
        list of tuple: Each tuple is (instruction, angle) where 'instruction' is a string 
                       and 'angle' is the magnitude of the turn in degrees.
                       For example: [("go straight", 0), ("left turn", 45), ("right turn", 30)]
    """
    instructions = []
    threshold = math.radians(threshold_degrees)
    
    for i in range(1, len(waypoints) - 1):
        p_prev = waypoints[i - 1]
        p_current = waypoints[i]
        p_next = waypoints[i + 1]
        
        # Create vectors: from p_prev to p_current and from p_current to p_next.
        vec_a = (p_current[0] - p_prev[0], p_current[1] - p_prev[1])
        vec_b = (p_next[0] - p_current[0], p_next[1] - p_current[1])
        
        dot = vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1]
        cross = vec_a[0] * vec_b[1] - vec_a[1] * vec_b[0]
        
        mag_a = math.hypot(*vec_a)
        mag_b = math.hypot(*vec_b)
        
        # If either vector is of zero length, we consider it as going straight.
        if mag_a == 0 or mag_b == 0:
            instructions.append(("S", 0))
            continue
        
        # Calculate the signed angle between vec_a and vec_b.
        signed_angle = math.atan2(cross, dot)
        angle_deg = abs(math.degrees(signed_angle))
        
        if abs(signed_angle) < threshold:
            instructions.append(("S", 0))
        elif signed_angle > 0:
            instructions.append(("L", angle_deg))
        else:
            instructions.append(("R", angle_deg))
    
    return instructions

#(uncomment for graph visualization)

def visualize_graph_with_path(graph, nodes, waypoints):
    """
    Visualizes the road network (graph) and overlays the computed path (waypoints).

    Parameters:
        graph (dict): The adjacency list for the map.
        nodes (dict): The dictionary containing node data with 'x' and 'y' coordinates.
        waypoints (list of tuple): A list of (x, y) coordinates representing the computed path.
    """
    # Create a NetworkX graph
    G = nx.Graph()
    for node_id in graph:
        G.add_node(node_id)
    
    # Add edges from the graph
    for node_id, edges in graph.items():
        for (nbr, weight) in edges:
            G.add_edge(node_id, nbr, weight=weight)
    
    # Build positions for nodes using the coordinates in the nodes dictionary
    pos = {node_id: (data["x"], data["y"]) for node_id, data in nodes.items()}
    
    # Draw the graph
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=500, node_color="lightblue")
    
    # Optionally, draw edge labels showing distances
    edge_labels = {(u, v): f"{w:.1f}" for (u, v, w) in G.edges(data="weight")}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # If a path (waypoints) was computed, overlay it on the graph
    if waypoints:
        xs, ys = zip(*waypoints)
        plt.plot(xs, ys, color="red", linewidth=3, marker="o", label="Computed Path")
        plt.legend()
    
    plt.title("Map Visualization with Computed Path")
    plt.axis("equal")
    plt.show()


if __name__ == "__main__":
    main_loop()