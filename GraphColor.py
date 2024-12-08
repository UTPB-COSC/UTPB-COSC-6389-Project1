import tkinter as tk
import numpy as np
import random
from random import randint

class GraphColoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Coloring Problem (Genetic Algorithm)")

        # Prompt user for number of vertices
        tk.Label(root, text="Enter number of vertices:").grid(row=0, column=0)
        self.vertex_entry = tk.Entry(root)
        self.vertex_entry.grid(row=0, column=1)

        # Button to create graph
        create_button = tk.Button(root, text="Create Graph", command=self.create_graph)
        create_button.grid(row=1, column=0, columnspan=2)

        # Canvas to visualize graph
        self.canvas = tk.Canvas(root, width=500, height=500)
        self.canvas.grid(row=2, column=0, columnspan=2)

        # Label to display generation count
        self.generation_label = tk.Label(root, text="Generation: 0")
        self.generation_label.grid(row=3, column=0, columnspan=2)

        # Label to indicate solution status
        self.solution_label = tk.Label(root, text="", fg="green")
        self.solution_label.grid(row=4, column=0, columnspan=2)

        # Button to solve graph coloring
        self.solve_button = tk.Button(root, text="Find Solution", command=self.solve_with_genetic_algorithm)
        self.solve_button.grid(row=5, column=0, columnspan=2)

        # Button to restart
        self.restart_button = tk.Button(root, text="Restart", command=self.restart, state=tk.DISABLED)
        self.restart_button.grid(row=6, column=0, columnspan=2)

        # Parameters for genetic algorithm
        self.population_size = 60
        self.max_num_colors = None
        self.graph = None

        # Extended color palette for vertices
        self.colors = [
            "red", "blue", "green", "yellow", "purple", "orange", "pink",
            "cyan", "brown", "gray", "magenta", "lime", "teal", "navy",
            "olive", "maroon", "aqua", "fuchsia", "silver", "gold", "indigo",
            "violet",  "turquoise", "beige", "lavender",
            "coral", "chocolate", "salmon", "plum", "khaki"
        ]

    def create_graph(self):
        """Generate circular adjacency matrix based on user input and start algorithm."""
        self.n = int(self.vertex_entry.get())  # Number of vertices
        self.graph = np.zeros((self.n, self.n), dtype=int)

        # Set adjacency in a circular manner
        for i in range(self.n):
            self.graph[i][(i + 1) % self.n] = 1  # Connect to next vertex
            self.graph[(i + 1) % self.n][i] = 1  # Connect back to previous vertex

        self.max_num_colors = self.get_max_colors()
        self.population = self.create_population()

        # Clear the solution message and canvas
        self.solution_label.config(text="")  # Reset solution status
        self.canvas.delete("all")  # Clear previous graph

        # Draw the initial graph layout without coloring (before solution)
        self.draw_graph()

    def get_max_colors(self):
        """Get maximum number of colors based on graph structure."""
        return self.n  # Maximum colors needed could be the number of vertices in the worst case

    def create_chromosome(self):
        """Generate a random chromosome for a solution."""
        return np.random.randint(1, self.max_num_colors + 1, size=(self.n))

    def create_population(self):
        """Create a population of chromosomes."""
        return np.array([self.create_chromosome() for _ in range(self.population_size)])

    def calc_fitness(self, chromosome):
        """Calculate fitness based on penalty for adjacent vertices sharing the same color."""
        penalty = 0
        for vertex1 in range(self.n):
            for vertex2 in range(vertex1 + 1, self.n):
                if self.graph[vertex1][vertex2] == 1 and chromosome[vertex1] == chromosome[vertex2]:
                    penalty += 1
        # Higher fitness score is better, so we return negative of penalty
        return -penalty

    def targeted_mutation(self, chromosome, chance):
        """Enhanced mutation to resolve conflicts in coloring adjacent vertices."""
        if random.uniform(0, 1) <= chance:
            for vertex1 in range(self.n):
                for vertex2 in range(self.n):
                    if self.graph[vertex1][vertex2] == 1 and chromosome[vertex1] == chromosome[vertex2]:
                        # Change the color of one of the conflicting vertices
                        chromosome[vertex1] = random.choice(
                            [color for color in range(1, self.max_num_colors + 1) if color != chromosome[vertex2]]
                        )
        return chromosome

    def roulette_wheel_selection(self):
        """Roulette wheel selection to choose parents for crossover."""
        fitness_values = np.array([self.calc_fitness(p) for p in self.population])

        # Invert fitness scores to get selection probabilities (lower fitness = higher probability)
        max_fitness = fitness_values.max() + 1
        probabilities = (max_fitness - fitness_values) / np.sum(max_fitness - fitness_values)

        # Ensure population is 1-dimensional for np.random.choice
        selected_indices = np.random.choice(len(self.population), size=self.population_size, replace=True,
                                            p=probabilities)
        parents = self.population[selected_indices]

        return parents

    def two_point_crossover(self, parent1, parent2):
        """Two-point crossover between two parents."""
        split_point1 = randint(1, self.n - 2)
        split_point2 = randint(split_point1 + 1, self.n - 1)
        child1 = np.concatenate((parent1[:split_point1], parent2[split_point1:split_point2], parent1[split_point2:]))
        child2 = np.concatenate((parent2[:split_point1], parent1[split_point1:split_point2], parent2[split_point2:]))
        return child1, child2

    def solve_with_genetic_algorithm(self):
        """Run the genetic algorithm to solve the graph coloring problem."""
        generations = 1000
        best_fitness = float('inf')
        fittest = None

        for generation in range(generations):
            self.generation_label.config(text=f"Generation: {generation}")
            self.root.update_idletasks()  # Update the display

            # Selection, Crossover, Mutation, and Population Update as before
            population = self.roulette_wheel_selection()
            children_population = []

            for i in range(0, len(population) - 1, 2):
                child1, child2 = self.two_point_crossover(population[i], population[i + 1])
                child1 = self.targeted_mutation(child1, 0.65 if generation < 100 else 0.15)
                child2 = self.targeted_mutation(child2, 0.65 if generation < 100 else 0.15)
                children_population.append(child1)
                children_population.append(child2)

            self.population = np.array(children_population)
            best_fitness, fittest = self.get_best_fitness()

            if best_fitness == 0:
                if self.check_solution_validity(fittest):  # New method for strict validation
                    self.draw_graph(fittest)
                    self.solution_label.config(text="Solution Found!")
                    self.solve_button.config(state=tk.DISABLED)
                    self.restart_button.config(state=tk.NORMAL)
                    return
                else:
                    best_fitness = float('inf')  # Reset and continue if validation fails

        self.draw_graph(fittest)

    def draw_graph(self, solution=None):
        """Draw the graph on the canvas, showing adjacency and highlighting conflicts if any."""
        self.canvas.delete("all")  # Clear previous graph

        # Generate positions for vertices in a circle
        positions = self.generate_vertices_positions()

        # Draw edges (connections between adjacent vertices)
        for i in range(self.n):
            next_vertex = (i + 1) % self.n  # Circular adjacency
            x1, y1 = positions[i]
            x2, y2 = positions[next_vertex]

            # Check if the vertices share the same color in the solution
            if solution is not None and solution[i] == solution[next_vertex]:
                # Draw red line for conflict
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2)
            else:
                # Draw normal line for adjacency
                self.canvas.create_line(x1, y1, x2, y2, fill="black", dash=(2, 2))

        # Draw vertices (nodes)
        for i in range(self.n):
            x, y = positions[i]

            # Determine the color for the node based on the solution (if available)
            color = self.colors[solution[i] % len(self.colors)] if solution is not None else "gray"

            # Draw node circle with color
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill=color, outline="black")

            # Label the node with its index
            self.canvas.create_text(x, y, text=str(i), fill="white")

    def generate_vertices_positions(self):
        """Generate positions for the vertices on the canvas."""
        radius = 150
        center_x, center_y = 250, 250
        positions = []
        for i in range(self.n):
            angle = 2 * np.pi * i / self.n
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            positions.append((x, y))
        return positions

    def get_best_fitness(self):
        """Get the best fitness from the current population."""
        best_fitness = float('inf')
        fittest = None
        for individual in self.population:
            fitness = self.calc_fitness(individual)
            if fitness < best_fitness:
                best_fitness = fitness
                fittest = individual
        return best_fitness, fittest

    # New method outside of the loop
    def check_solution_validity(self, solution):
        """Validate solution to ensure no adjacent vertices share the same color."""
        for vertex1 in range(self.n):
            for vertex2 in range(vertex1 + 1, self.n):
                if self.graph[vertex1][vertex2] == 1 and solution[vertex1] == solution[vertex2]:
                    return False
        return True
    def restart(self):
        """Reset everything to start from scratch."""
        self.solve_button.config(state=tk.NORMAL)  # Enable solve button
        self.restart_button.config(state=tk.DISABLED)  # Disable restart button
        self.solution_label.config(text="")  # Reset solution message
        self.generation_label.config(text="Generation: 0")  # Reset generation label
        self.canvas.delete("all")  # Clear canvas


# Run the app
root = tk.Tk()
app = GraphColoringApp(root)
root.mainloop()
