import math
import random
import tkinter as tk
from tkinter import ttk  # For dropdown

# Parameters
num_cities = 50
city_scale = 5
road_width = 3
padding = 100
cooling_rate = 0.995
initial_temp = 1000
best_edge_color = "blue"
excluded_edge_color = "grey"
node_color = "black"
start_node_color = "red"
pheromone_evaporation_rate = 0.5
pheromone_constant = 100.0
alpha = 1.0
beta = 2.0
num_ants = 30
num_iterations = 100


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, canvas, color='black'):
        canvas.create_oval(self.x - city_scale, self.y - city_scale,
                           self.x + city_scale, self.y + city_scale, fill=color)


class TravelingSalesman:
    def __init__(self, nodes):
        self.nodes = nodes
        self.best_path = self.nearest_neighbor()  # Start with a heuristic
        self.best_distance = self.calculate_total_distance(self.best_path)

    def calculate_total_distance(self, path):
        return sum(math.sqrt((self.nodes[path[i]].x - self.nodes[path[i - 1]].x) ** 2 +
                             (self.nodes[path[i]].y - self.nodes[path[i - 1]].y) ** 2)
                   for i in range(len(path)))

    def nearest_neighbor(self):
        unvisited = set(range(len(self.nodes)))
        path = [unvisited.pop()]

        while unvisited:
            last = path[-1]
            next_city = min(unvisited, key=lambda city: math.sqrt((self.nodes[last].x - self.nodes[city].x) ** 2 +
                                                                  (self.nodes[last].y - self.nodes[city].y) ** 2))
            path.append(next_city)
            unvisited.remove(next_city)

        return path

    def two_opt(self, path):
        best = path[:]
        improved = True
        while improved:
            improved = False
            for i in range(1, len(best) - 2):
                for j in range(i + 1, len(best)):
                    if j - i == 1: continue
                    new_path = best[:]
                    new_path[i:j] = best[j - 1:i - 1:-1]
                    new_distance = self.calculate_total_distance(new_path)
                    if new_distance < self.calculate_total_distance(best):
                        best = new_path
                        improved = True
            path = best
        return path

    def simulated_annealing(self):
        current_path = self.best_path[:]
        current_distance = self.best_distance
        temperature = initial_temp

        while temperature > 1:
            # Select a new neighboring solution by swapping two cities
            new_path = current_path[:]
            i, j = random.sample(range(len(self.nodes)), 2)
            new_path[i], new_path[j] = new_path[j], new_path[i]

            # Apply a two-opt move to the new path for local optimization
            new_path = self.two_opt(new_path)
            new_distance = self.calculate_total_distance(new_path)

            # Decide whether to accept the new solution
            if (new_distance < current_distance or
                    math.exp((current_distance - new_distance) / temperature) > random.random()):
                current_path, current_distance = new_path, new_distance
                if new_distance < self.best_distance:
                    self.best_path, self.best_distance = new_path, new_distance

            # Reduce the temperature slowly for gradual convergence
            temperature *= cooling_rate
            yield self.best_path, self.best_distance

    def ant_colony_optimization(self):
        num_nodes = len(self.nodes)
        pheromones = [[1.0 for _ in range(num_nodes)] for _ in range(num_nodes)]
        best_path = None
        best_distance = float('inf')

        for _ in range(num_iterations):
            paths = []
            distances = []

            for _ in range(num_ants):
                path = self.generate_ant_path(pheromones)
                distance = self.calculate_total_distance(path)
                paths.append(path)
                distances.append(distance)

                if distance < best_distance:
                    best_distance = distance
                    best_path = path

            for i in range(num_nodes):
                for j in range(i + 1, num_nodes):
                    pheromones[i][j] *= (1 - pheromone_evaporation_rate)
                    pheromones[j][i] = pheromones[i][j]

            for k, path in enumerate(paths):
                distance = distances[k]
                for i in range(len(path)):
                    a, b = path[i - 1], path[i]
                    pheromones[a][b] += pheromone_constant / distance
                    pheromones[b][a] = pheromones[a][b]

            yield best_path, best_distance

    def generate_ant_path(self, pheromones):
        path = [random.randint(0, len(self.nodes) - 1)]
        unvisited = set(range(len(self.nodes))) - {path[0]}

        while unvisited:
            current = path[-1]
            next_city = self.select_next_city(current, unvisited, pheromones)
            path.append(next_city)
            unvisited.remove(next_city)

        return path

    def select_next_city(self, current, unvisited, pheromones):
        probabilities = []
        for city in unvisited:
            edge_pheromone = pheromones[current][city]
            edge_distance = math.sqrt((self.nodes[current].x - self.nodes[city].x) ** 2 +
                                      (self.nodes[current].y - self.nodes[city].y) ** 2)
            probabilities.append((edge_pheromone ** alpha) * ((1 / edge_distance) ** beta))

        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]

        return random.choices(list(unvisited), weights=probabilities, k=1)[0]


class UI(tk.Tk):
    def __init__(self, tsp_solver):
        super().__init__()
        self.tsp_solver = tsp_solver
        self.canvas = tk.Canvas(self, width=800, height=600, bg="white")
        self.canvas.pack()
        self.nodes = tsp_solver.nodes
        self.current_edges = []
        self.distance_text = None
        self.solver_var = tk.StringVar(value="Simulated Annealing")
        self.initialize_ui()

    def initialize_ui(self):
        self.title("Traveling Salesman Problem - Solver Selection")
        self.distance_text = self.canvas.create_text(400, 20, text="Distance: 0", font=("Arial", 12))

        # Dropdown menu for solver selection
        solver_label = tk.Label(self, text="Select Solver:")
        solver_label.pack()
        solver_menu = ttk.Combobox(self, textvariable=self.solver_var,
                                   values=["Simulated Annealing", "Ant Colony Optimization"])
        solver_menu.pack()

        # Start button
        start_button = tk.Button(self, text="Start", command=self.start_solver)
        start_button.pack()

        self.draw_nodes()

    def draw_nodes(self):
        for i, node in enumerate(self.nodes):
            color = 'red' if i == 0 else 'black'
            node.draw(self.canvas, color=color)

    def draw_edges(self, path, distance):
        for edge in self.current_edges:
            self.canvas.delete(edge)
        self.current_edges = []

        for i in range(len(path)):
            a, b = self.nodes[path[i - 1]], self.nodes[path[i]]
            edge_id = self.canvas.create_line(a.x, a.y, b.x, b.y, fill="blue", width=road_width)
            self.current_edges.append(edge_id)

        self.canvas.itemconfig(self.distance_text, text=f"Distance: {distance:.2f}")
        self.canvas.update()

    def start_solver(self):
        solver_choice = self.solver_var.get()
        solver_func = self.tsp_solver.simulated_annealing if solver_choice == "Simulated Annealing" else self.tsp_solver.ant_colony_optimization
        for path, distance in solver_func():
            self.draw_edges(path, distance)


if __name__ == "__main__":
    nodes = [Node(random.randint(padding, 700), random.randint(padding, 500)) for _ in range(num_cities)]
    tsp_solver = TravelingSalesman(nodes)
    ui = UI(tsp_solver)
    ui.mainloop()
