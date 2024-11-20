import tkinter as tk
import random
import math
from tkinter import messagebox
import threading

class GraphColoringApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Graph Coloring Problem (Genetic Algorithm & ACO)")

        # Canvas to visualize graph
        self.canvas = tk.Canvas(self, width=400, height=400, bg="white")
        self.canvas.pack(pady=10)

        # Frame for inputs and buttons
        self.input_frame = tk.Frame(self)
        self.input_frame.pack(pady=10)

        # Prompt user for number of vertices
        tk.Label(self.input_frame, text="Enter number of vertices:").grid(row=0, column=0)
        self.vertex_entry = tk.Entry(self.input_frame)
        self.vertex_entry.grid(row=0, column=1)

        # Prompt user for number of colors
        tk.Label(self.input_frame, text="Enter number of colors:").grid(row=1, column=0)
        self.color_entry = tk.Entry(self.input_frame)
        self.color_entry.grid(row=1, column=1)

        # Button to create graph
        create_button = tk.Button(self.input_frame, text="Create Graph", command=self.create_graph)
        create_button.grid(row=2, column=0, columnspan=2)

        # Solver selection
        tk.Label(self.input_frame, text="Select Solver:").grid(row=3, column=0)
        self.solver_var = tk.StringVar(value="Genetic Algorithm")
        solver_options = ["Genetic Algorithm", "Ant Colony Optimization"]
        self.solver_menu = tk.OptionMenu(self.input_frame, self.solver_var, *solver_options)
        self.solver_menu.grid(row=3, column=1)

        # Button to solve graph coloring
        solve_button = tk.Button(self.input_frame, text="Find Solution", command=self.solve_graph_coloring)
        solve_button.grid(row=4, column=0, columnspan=2)

        # Label to display generation or iteration count
        self.status_label = tk.Label(self, text="")
        self.status_label.pack()

        # Label to indicate solution status
        self.result_var = tk.StringVar()
        self.result_var.set("Status: Ready")
        self.result_label = tk.Label(self, textvariable=self.result_var, fg="green")
        self.result_label.pack(pady=10)

        # Parameters for algorithms
        self.population_size = 200  # Increased population size for GA
        self.num_colors = None
        self.adj_list = None
        self.vertices_positions = None

    def create_graph(self):
        """Generate random adjacency list based on user input and start algorithm."""
        try:
            num_vertices = int(self.vertex_entry.get())
            self.num_colors = int(self.color_entry.get())
            if num_vertices <= 0 or self.num_colors <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter positive integers for vertices and colors.")
            return

        self.num_vertices = num_vertices
        self.adj_list = self.generate_random_graph(num_vertices)
        print("Adjacency List:", self.adj_list)  # Debug: Print the adjacency list

        # Clear the solution message and canvas
        self.result_var.set("Status: Ready")  # Reset status
        self.canvas.delete("all")  # Clear previous graph

        self.vertices_positions = self.generate_vertices_positions()
        self.draw_graph()

    def generate_random_graph(self, num_vertices):
        """Generate a connected random graph as an adjacency list."""
        adj_list = {i: set() for i in range(num_vertices)}
        max_degree = min(self.num_colors - 1 if self.num_colors > 1 else num_vertices - 1, num_vertices - 1)

        # Start with a simple path to ensure connectivity
        for i in range(num_vertices - 1):
            adj_list[i].add(i + 1)
            adj_list[i + 1].add(i)

        # Randomly add additional edges
        edge_attempts = 0
        max_edge_attempts = num_vertices * (num_vertices - 1) // 2  # Maximum possible edges
        while edge_attempts < num_vertices * 2 and edge_attempts < max_edge_attempts:
            u, v = random.sample(range(num_vertices), 2)
            if len(adj_list[u]) < max_degree and len(adj_list[v]) < max_degree and v not in adj_list[u]:
                adj_list[u].add(v)
                adj_list[v].add(u)
            edge_attempts += 1

        return adj_list

    def generate_vertices_positions(self):
        """Calculate positions for vertices in a circle layout."""
        radius = 150
        center_x, center_y = 200, 200
        positions = []
        for i in range(self.num_vertices):
            angle = 2 * math.pi * i / self.num_vertices
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions.append((x, y))
        return positions

    def draw_graph(self, solution=None):
        """Draw the graph on the canvas, coloring vertices based on the solution."""
        self.canvas.delete("all")
        # Generate a list of distinct colors
        colors = self.generate_color_list(self.num_colors)

        for i, (x, y) in enumerate(self.vertices_positions):
            color_index = solution[i] % len(colors) if solution else None
            color = colors[color_index] if solution else "gray"
            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color, outline="black")
            self.canvas.create_text(x, y, text=str(i + 1), font=("Arial", 14))

        drawn_edges = set()
        for i in range(self.num_vertices):
            for j in self.adj_list[i]:
                if (i, j) not in drawn_edges and (j, i) not in drawn_edges:
                    x1, y1 = self.vertices_positions[i]
                    x2, y2 = self.vertices_positions[j]
                    if solution and solution[i] == solution[j]:
                        line_color = "red"  # Highlight conflicts in red
                    else:
                        line_color = "black"
                    self.canvas.create_line(x1, y1, x2, y2, fill=line_color)
                    drawn_edges.add((i, j))

    def generate_color_list(self, num_colors):
        """Generate a list of distinct colors."""
        import colorsys
        colors = []
        for i in range(num_colors):
            hue = i / num_colors
            lightness = 0.5
            saturation = 0.7
            rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
            hex_color = '#%02x%02x%02x' % tuple(int(c * 255) for c in rgb)
            colors.append(hex_color)
        return colors

    def solve_graph_coloring(self):
        """Determine which solver to use based on user selection."""
        solver = self.solver_var.get()
        if solver == "Genetic Algorithm":
            threading.Thread(target=self.solve_with_genetic_algorithm).start()
        elif solver == "Ant Colony Optimization":
            threading.Thread(target=self.solve_with_aco).start()

    # Genetic Algorithm methods

    def solve_with_genetic_algorithm(self):
        """Run the genetic algorithm to solve the graph coloring problem."""
        self.population = self.generate_population()
        self.evolve_graph_coloring()

    def generate_population(self):
        """Initialize a random population of color assignments."""
        return [[random.randint(0, self.num_colors - 1) for _ in range(self.num_vertices)]
                for _ in range(self.population_size)]

    def fitness(self, individual):
        """Calculate fitness based on the number of conflicts."""
        conflicts = 0
        for i in range(self.num_vertices):
            for j in self.adj_list[i]:
                if j > i and individual[i] == individual[j]:
                    conflicts += 1
        return conflicts  # Lower is better; zero conflicts is ideal.

    def evolve_graph_coloring(self):
        """Evolve the population over generations to find a solution."""
        generations = 2000  # Increased number of generations
        solution_found = False
        for generation in range(generations):
            # Update generation label on UI every 10 generations
            if generation % 10 == 0:
                self.after(0, self.update_status_label, f"Generation: {generation}")
                self.after(0, self.draw_graph, self.population[0])

            fitness_scores = [self.fitness(ind) for ind in self.population]
            best_fitness = min(fitness_scores)

            # Debug statement
            if generation % 100 == 0:
                print(f"Generation {generation}: Best Fitness = {best_fitness}")

            # Check if a solution has been found
            if best_fitness == 0:
                solution_found = True
                solution = self.population[fitness_scores.index(best_fitness)]
                self.after(0, self.draw_graph, solution)
                self.result_var.set("Status: Solution Found!")
                messagebox.showinfo("Success", "A solution has been found!")
                break

            # Select parents and generate new population
            parents = self.select_parents(fitness_scores)
            new_population = parents[:]
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(parents, 2)
                child = self.multi_point_crossover(parent1, parent2)
                child = self.adaptive_mutate(child, generation)
                new_population.append(child)

            # Update population
            self.population = new_population

        if not solution_found:
            self.result_var.set("Status: No Solution Found")
            messagebox.showinfo("Result", "No valid coloring was found after 2000 generations.")

    def update_status_label(self, text):
        """Update the status label in a thread-safe manner."""
        self.status_label.config(text=text)

    def select_parents(self, fitness_scores):
        """Select individuals with the lowest fitness scores (less conflicts)."""
        sorted_population = [ind for _, ind in sorted(zip(fitness_scores, self.population), key=lambda x: x[0])]
        return sorted_population[:self.population_size // 2]

    def multi_point_crossover(self, parent1, parent2):
        """Perform multi-point crossover with two crossover points."""
        crossover_point1 = random.randint(1, self.num_vertices // 2)
        crossover_point2 = random.randint(crossover_point1, self.num_vertices - 1)
        return parent1[:crossover_point1] + parent2[crossover_point1:crossover_point2] + parent1[crossover_point2:]

    def adaptive_mutate(self, individual, generation):
        """Adaptive mutation rate to allow more exploration in early generations."""
        mutation_rate = max(0.01, 0.1 - (generation * 0.00005))
        for i in range(self.num_vertices):
            if random.random() < mutation_rate:
                individual[i] = random.randint(0, self.num_colors - 1)
        return individual

    # Ant Colony Optimization methods

    def solve_with_aco(self):
        """Run the Ant Colony Optimization algorithm to solve the graph coloring problem."""
        max_iterations = 2000  # Increased number of iterations
        num_ants = 100  # Increased number of ants
        evaporation_rate = 0.3
        alpha = 1  # Pheromone importance
        beta = 5   # Heuristic importance

        pheromone = [[1.0 for _ in range(self.num_colors)] for _ in range(self.num_vertices)]
        best_solution = None
        best_conflicts = float('inf')  # Correct initialization

        for iteration in range(max_iterations):
            all_solutions = []
            for ant in range(num_ants):
                solution = self.construct_solution(pheromone, alpha, beta)
                conflicts = self.fitness(solution)
                # Debug: Print conflicts for each ant
                # print(f"Iteration {iteration}, Ant {ant}: Conflicts = {conflicts}")

                all_solutions.append((solution, conflicts))
                if conflicts < best_conflicts:
                    best_solution = solution
                    best_conflicts = conflicts

            # Update pheromones
            pheromone = self.update_pheromones(pheromone, all_solutions, evaporation_rate)

            # Update UI every 10 iterations
            if iteration % 10 == 0:
                self.after(0, self.update_status_label, f"Iteration: {iteration}")
                self.after(0, self.draw_graph, best_solution)
                # Debug statement
                print(f"Iteration {iteration}: Best Conflicts = {best_conflicts}")

            # Check if a solution has been found
            if best_conflicts == 0:
                self.after(0, self.draw_graph, best_solution)
                self.result_var.set("Status: Solution Found!")
                messagebox.showinfo("Success", "A solution has been found!")
                return

        # If no solution is found
        self.result_var.set("Status: No Solution Found")
        messagebox.showinfo("Result", "No valid coloring was found after 2000 iterations.")

    def construct_solution(self, pheromone, alpha, beta):
        """Construct a solution based on pheromone levels and heuristic information."""
        solution = [-1] * self.num_vertices
        for vertex in range(self.num_vertices):
            probabilities = []
            for color in range(self.num_colors):
                pheromone_level = pheromone[vertex][color] ** alpha
                heuristic = self.calculate_heuristic(vertex, color, solution) ** beta
                probabilities.append(pheromone_level * heuristic)
            total = sum(probabilities)
            if total == 0:
                probabilities = [1 / self.num_colors] * self.num_colors
            else:
                probabilities = [p / total for p in probabilities]
            color = self.random_choice(probabilities)
            solution[vertex] = color
        return solution

    def calculate_heuristic(self, vertex, color, solution):
        """Calculate heuristic value for assigning a color to a vertex."""
        conflict = 0
        for neighbor in self.adj_list[vertex]:
            if solution[neighbor] == color:
                conflict += 1
        return 1.0 / (1 + conflict)

    def random_choice(self, probabilities):
        """Choose an index based on a list of probabilities."""
        r = random.uniform(0, 1)
        cumulative = 0.0
        for i, p in enumerate(probabilities):
            cumulative += p
            if r <= cumulative:
                return i
        return len(probabilities) - 1

    def update_pheromones(self, pheromone, all_solutions, evaporation_rate):
        """Update the pheromone levels on the graph."""
        # Evaporate pheromones
        for i in range(self.num_vertices):
            for c in range(self.num_colors):
                pheromone[i][c] *= (1 - evaporation_rate)

        # Deposit new pheromones
        for solution, conflicts in all_solutions:
            deposit = 1.0 / (1 + conflicts)
            for vertex, color in enumerate(solution):
                pheromone[vertex][color] += deposit

        return pheromone

# Run the app
if __name__ == '__main__':
    app = GraphColoringApp()
    app.mainloop()
