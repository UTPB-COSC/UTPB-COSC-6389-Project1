import random
import tkinter as tk
import numpy as np
from multiprocessing import Pool, cpu_count
import logging
from tkinter.simpledialog import askinteger
import time

logging.basicConfig(level=logging.INFO)

num_cities = 25
city_scale = 5
road_width = 4
padding = 100
num_ants = 30
alpha = 1  # Importance of pheromone
beta = 2   # Importance of heuristic
evaporation_rate = 0.5 # Rate of pheromone evaporation
iterations = 100

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, canvas, color='black'):
        canvas.create_oval(self.x - city_scale, self.y - city_scale,
                           self.x + city_scale, self.y + city_scale, fill=color)

class ACO:
    def __init__(self, distance_matrix, num_ants, alpha, beta, evaporation_rate, iterations):
        # Initialize ACO parameters and pheromone matrix
        self.distance_matrix = distance_matrix
        self.num_cities = len(distance_matrix)
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.iterations = iterations
        self.pheromones = np.ones((self.num_cities, self.num_cities))

    def probability(self, current_city, unvisited):
        # Calculate the probability of moving to each unvisited city
        unvisited = list(unvisited)
        pheromones = np.array([self.pheromones[current_city, i] for i in unvisited])
        distances = np.array([self.distance_matrix[current_city, i] for i in unvisited])
        heuristic = 1 / distances # Inverse distance
        denom = np.sum((pheromones ** self.alpha) * (heuristic ** self.beta))
        probs = (pheromones ** self.alpha) * (heuristic ** self.beta) / denom
        return probs.tolist()

    def simulate_ant(self, seed):
        # Simulate a single ant's tour and return the roads tested
        random.seed(seed)
        tour = [random.randint(0, self.num_cities - 1)] # Start from a random city
        unvisited = set(range(self.num_cities)) - {tour[0]}
        tested_roads = []  # Collect roads tested by the ant

        while unvisited:
            current_city = tour[-1]
            probs = self.probability(current_city, unvisited) # Probabilities for next city
            next_city = random.choices(list(unvisited), weights=probs, k=1)[0]
            tour.append(next_city)
            unvisited.remove(next_city)

            # Record the road being tested
            tested_roads.append((current_city, next_city))

        return tour, self.total_distance(tour), tested_roads

    def update_pheromones(self, best_tour, best_distance):
        # Update the pheromone levels based on the best tour
        self.pheromones *= (1 - self.evaporation_rate) # Evaporate pheromones
        for i in range(len(best_tour)):
            start_city = best_tour[i]
            end_city = best_tour[(i + 1) % len(best_tour)]
            self.pheromones[start_city][end_city] += 1.0 / best_distance # Reinforce best path

    def total_distance(self, tour):
        #Calculate the total distance of a given tour
        return sum(self.distance_matrix[tour[i], tour[(i + 1) % self.num_cities]] for i in range(len(tour)))

    def run(self, canvas, cities_list, visualize = True):
        best_tour = None
        best_distance = float("inf")
        all_tested_roads = []  # Initialize to store tested roads

        with Pool(cpu_count()) as pool:
            for iteration in range(self.iterations):
                seeds = [random.randint(0, 10000) for _ in range(self.num_ants)]
                results = pool.map(self.simulate_ant, seeds)

                if visualize and iteration % 10 == 0:  # Only visualize every 10 iterations
                    canvas.delete("aco_paths")
                    for tour, _, _ in results:
                        for i in range(len(tour)):
                            start = cities_list[tour[i]]
                            end = cities_list[tour[(i + 1) % len(tour)]]
                            canvas.create_line(
                                start.x, start.y, end.x, end.y, fill="lightgreen", dash=(4, 2), tags="aco_paths"
                            )
                    canvas.update()

                for tour, tour_distance, tested_roads in results:
                    all_tested_roads.extend(tested_roads)
                    if tour_distance < best_distance:
                        best_distance = tour_distance
                        best_tour = tour

                self.update_pheromones(best_tour, best_distance)

            return best_tour, best_distance, all_tested_roads

class TravelingSalesmanUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Traveling Salesman Comparison - ACO vs GA")
        self.geometry("1200x800")

        self.toolbar = tk.Frame(self, bg="gray")
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(self.toolbar, text="Number of Cities:", bg="gray", fg="white").pack(side=tk.LEFT, padx=5, pady=5)

        self.city_entry = tk.Entry(self.toolbar, width=10)
        self.city_entry.insert(0, "25")
        self.city_entry.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(self.toolbar, text="Update", command=self.update_cities).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Run TSP ACO", command=self.run_tsp_aco).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Run TSP No ACO", command=self.run_tsp_no_aco).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Run Comparison", command=self.run_comparison).pack(side=tk.LEFT, padx=5, pady=5)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.cities_list = []
        self.num_cities = 25

    def update_cities(self):
        # Update the number of cities and regenerate the map
        try:
            num = int(self.city_entry.get())
            if 5 <= num <= 100:
                self.num_cities = num
                self.generate_cities()
            else:
                tk.messagebox.showerror("Error", "Please enter a number between 5 and 100.")
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid input. Please enter a number.")

    def generate_cities(self):
        # Generate random cities and display all possible roads
        self.cities_list = [Node(random.randint(50, self.winfo_width() - 50),
                                random.randint(50, self.winfo_height() - 50))
                            for _ in range(self.num_cities)]

        self.distance_matrix = self.calculate_distance_matrix()

        self.canvas.delete("all")
        for i in range(len(self.cities_list)):
            for j in range(i + 1, len(self.cities_list)):
                start_node = self.cities_list[i]
                end_node = self.cities_list[j]
                self.canvas.create_line(
                    start_node.x, start_node.y, end_node.x, end_node.y, fill='lightgray', dash=(4, 2), tags="all_roads"
                )
        for node in self.cities_list:
            node.draw(self.canvas) # Draw cities on top of the roads

    def calculate_distance_matrix(self):
        coordinates = np.array([[node.x, node.y] for node in self.cities_list])
        return np.sqrt(np.sum((coordinates[:, None, :] - coordinates[None, :, :]) ** 2, axis=2))

    def run_tsp_aco(self):
        # Run TSP using ACO
        if not self.cities_list:
            tk.messagebox.showwarning("Warning", "Please generate cities first.")
            return

        # Initialize ACO
        aco = ACO(self.distance_matrix, num_ants=50, alpha=1, beta=2, evaporation_rate=0.5, iterations=100)

        # Time the execution
        start_time = time.time()
        best_tour, best_distance, _ = aco.run(self.canvas, self.cities_list)
        execution_time = time.time() - start_time

        # Draw ACO route
        self.canvas.delete("aco_route")
        for i in range(len(best_tour)):
            start = self.cities_list[best_tour[i]]
            end = self.cities_list[best_tour[(i + 1) % len(best_tour)]]
            self.canvas.create_line(
                start.x, start.y, end.x, end.y, fill='lightgreen', width=4, tags="aco_route"
            )

        self.display_results("ACO", best_distance, execution_time, completed=True, tags="aco_text")
        logging.info(f"ACO completed in {execution_time:.2f}s")

    def run_tsp_no_aco(self):
        # Run TSP using GA
        if not self.cities_list:
            tk.messagebox.showwarning("Warning", "Please generate cities first.")
            return

        start_time = time.time()
        best_solution, best_distance = self.run_genetic_algorithm()
        execution_time = time.time() - start_time

        self.canvas.delete("ga_route") # draw GA route
        for i in range(len(best_solution)):
            start = self.cities_list[best_solution[i]]
            end = self.cities_list[best_solution[(i + 1) % len(best_solution)]]
            self.canvas.create_line(
                start.x, start.y, end.x, end.y, fill='orange', width=4, tags="ga_route"
            )

        self.display_results("GA", best_distance, execution_time, completed=True, tags="ga_text")
        logging.info(f"GA completed in {execution_time:.2f}s")

    def run_genetic_algorithm(self, visualize=True, update_interval=10):
        # TSP GA
        population = [random.sample(range(len(self.cities_list)), len(self.cities_list)) for _ in range(30)]
        best_solution = None
        best_distance = float("inf")

        for generation in range(100):  # Generations
            # Evolve the population
            population = self.evolve_population(population)

            # Find the best solution in the current generation
            current_best = min(population, key=self.total_distance)
            current_distance = self.total_distance(current_best)

            # Update global best if a new best is found
            if current_distance < best_distance:
                best_solution = current_best
                best_distance = current_distance

            # Visualize the current population and best route every `update_interval` generations
            if visualize and generation % update_interval == 0:
                self.canvas.delete("ga_paths")
                for tour in population:
                    for i in range(len(tour)):
                        start = self.cities_list[tour[i]]
                        end = self.cities_list[tour[(i + 1) % len(tour)]]
                        self.canvas.create_line(
                            start.x, start.y, end.x, end.y, fill="orange", dash=(4, 2), tags="ga_paths"
                        )

                # Highlight the current best route
                self.canvas.delete("ga_best")
                for i in range(len(best_solution)):
                    start = self.cities_list[best_solution[i]]
                    end = self.cities_list[best_solution[(i + 1) % len(best_solution)]]
                    self.canvas.create_line(
                        start.x, start.y, end.x, end.y, fill="orange", width=2, tags="ga_best"
                    )

                # Update the canvas
                self.canvas.update()

        # Final visualization for the best solution
        self.canvas.delete("ga_best")
        for i in range(len(best_solution)):
            start = self.cities_list[best_solution[i]]
            end = self.cities_list[best_solution[(i + 1) % len(best_solution)]]
            self.canvas.create_line(
                start.x, start.y, end.x, end.y, fill="orange", width=4, tags="ga_best"
            )

        return best_solution, best_distance

    def total_distance(self, tour):
        # Calculate the total distance of a tour
        return sum(self.distance_matrix[tour[i], tour[(i + 1) % len(tour)]] for i in range(len(tour)))

    def evolve_population(self, population):
        # Evolve the population
        def crossover(parent1, parent2):
            child = [None] * len(parent1)
            start, end = sorted(random.sample(range(len(parent1)), 2))
            child[start:end] = parent1[start:end]
            for gene in parent2:
                if gene not in child:
                    child[child.index(None)] = gene
            return child

        def mutate(tour):
            if random.random() < 0.01:
                i, j = random.sample(range(len(tour)), 2)
                tour[i], tour[j] = tour[j], tour[i]

        selected = sorted(population, key=self.total_distance)[:10]
        next_population = []

        while len(next_population) < len(population):
            parent1, parent2 = random.sample(selected, 2)
            child = crossover(parent1, parent2)
            mutate(child)
            next_population.append(child)

        return next_population

    def display_results(self, method, distance, time_taken, completed=False, tags=None):
        self.canvas.delete(tags)
        
        y_offset = {"ACO": 10, "GA": 50}[method]
        text = f"{method} - Best Distance: {distance:.2f}, Time: {time_taken:.2f}s"
        if completed:
            text += " (Completed)"
        
        text_id = self.canvas.create_text(
            10, y_offset, text=text, anchor="nw", tags=tags, fill="black", font=("Arial", 12)
        )
        bbox = self.canvas.bbox(text_id) # bounding box
        if bbox:
            x0, y0, x1, y1 = bbox
            self.canvas.create_rectangle(
                x0 - 5, y0 - 2, x1 + 5, y1 + 2, 
                fill="white", outline="black", tags=f"{tags}_bg"
            )
            self.canvas.tag_raise(text_id)
    
    def run_comparison(self):
        # Run both TSP algorithms sequentially for comparison
        
        # Run ACO
        start_time_aco = time.time()
        self.run_tsp_aco()
        time_taken_aco = time.time() - start_time_aco
        
        # Run GA
        start_time_ga = time.time()
        self.run_tsp_no_aco()
        time_taken_ga = time.time() - start_time_ga

        # Log the time comparison
        logging.info(f"ACO Execution Time: {time_taken_aco:.2f}s")
        logging.info(f"GA Execution Time: {time_taken_ga:.2f}s")

        #tk.messagebox.showinfo(
        #    "Comparison Results",
        #    f"Comparison Completed:\nACO Time: {time_taken_aco:.2f}s\nGA Time: {time_taken_ga:.2f}s"
        #)
        self.draw_legend()

    def draw_legend(self):
        padding = 10
        line_height = 20 
        explanation_text = (
            "ACO takes longer due to\n"
            "pheromone updates.\n"
            "GA is faster but may converge\n"
            "prematurely."
        )

        num_lines = 3 + len(explanation_text.split("\n"))

        legend_width = 200 
        legend_height = padding * 2 + line_height * (num_lines-1)

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        legend_x = canvas_width - legend_width - padding
        legend_y = padding

        self.canvas.create_rectangle(
            legend_x, legend_y,
            legend_x + legend_width, legend_y + legend_height,
            fill="white", outline="black", width=1, tags="legend"
        )

        # ACO route explanation
        line_y = legend_y + padding
        self.canvas.create_line(
            legend_x + padding, line_y, legend_x + padding + 30, line_y,
            fill="lightgreen", width=3, tags="legend"
        )
        self.canvas.create_text(
            legend_x + padding + 40, line_y, anchor="w",
            text="ACO Best Route", fill="black", font=("Arial", 10), tags="legend"
        )

        # GA route explanation
        line_y += line_height
        self.canvas.create_line(
            legend_x + padding, line_y, legend_x + padding + 30, line_y,
            fill="orange", width=3, tags="legend"
        )
        self.canvas.create_text(
            legend_x + padding + 40, line_y, anchor="w",
            text="GA Best Route", fill="black", font=("Arial", 10), tags="legend"
        )

        # All roads explanation
        line_y += line_height
        self.canvas.create_line(
            legend_x + padding, line_y, legend_x + padding + 30, line_y,
            fill="gray", dash=(4, 2), tags="legend"
        )
        self.canvas.create_text(
            legend_x + padding + 40, line_y, anchor="w",
            text="All Possible Roads", fill="black", font=("Arial", 10), tags="legend"
        )

        line_y += line_height
        self.canvas.create_text(
            legend_x + padding, line_y, anchor="nw",
            text=explanation_text, fill="black", font=("Arial", 9), tags="legend"
        )

class Node:
    """Represents a city node."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, canvas):
        city_scale = 5
        canvas.create_oval(self.x - city_scale, self.y - city_scale,
                           self.x + city_scale, self.y + city_scale, fill="black")

if __name__ == '__main__':
    app = TravelingSalesmanUI()
    app.mainloop()
