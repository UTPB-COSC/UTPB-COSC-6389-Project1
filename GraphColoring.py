import tkinter as tk
import random
import math
from tkinter import messagebox

class GraphColoringApp(tk.Tk):  # Change here: Subclassing tk.Tk
    def __init__(self):
        super().__init__()  # Call the parent constructor
        self.title("Graph Coloring Problem (Genetic Algorithm)")

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

        # Button to solve graph coloring
        solve_button = tk.Button(self.input_frame, text="Find Solution", command=self.solve_with_genetic_algorithm)
        solve_button.grid(row=3, column=0, columnspan=2)

        # Label to display generation count
        self.generation_label = tk.Label(self, text="Generation: 0")
        self.generation_label.pack()

        # Label to indicate solution status
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Ready")
        self.status_label = tk.Label(self, textvariable=self.status_var, fg="green")
        self.status_label.pack(pady=10)

        # Parameters for genetic algorithm
        self.population_size = 100
        self.num_colors = None
        self.adj_list = None

    def create_graph(self):
        """Generate random adjacency list based on user input and start algorithm."""
        num_vertices = int(self.vertex_entry.get())
        self.num_colors = int(self.color_entry.get())
        self.num_vertices = num_vertices
        self.adj_list = self.generate_random_graph(num_vertices)

        # Clear the solution message and canvas
        self.status_var.set("Status: Ready")  # Reset status
        self.canvas.delete("all")  # Clear previous graph

        self.vertices_positions = self.generate_vertices_positions()
        self.draw_graph()

    def generate_random_graph(self, num_vertices):
        """Generate a connected random graph as an adjacency list."""
        # Start with a simple path to ensure connectivity
        adj_list = {i: set() for i in range(num_vertices)}
        for i in range(num_vertices - 1):
            adj_list[i].add(i + 1)
            adj_list[i + 1].add(i)

        # Randomly add additional edges to increase complexity
        for _ in range(num_vertices * 2):  # Adjust the multiplier for more edges
            u = random.randint(0, num_vertices - 1)
            v = random.randint(0, num_vertices - 1)
            if u != v:  # Avoid self-loops
                adj_list[u].add(v)
                adj_list[v].add(u)

        return adj_list

    def generate_vertices_positions(self):
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
        self.canvas.delete("all")
        colors = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"]

        for i, (x, y) in enumerate(self.vertices_positions):
            color = colors[solution[i] % len(colors)] if solution else "gray"
            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color, outline="black")
            self.canvas.create_text(x, y, text=str(i + 1), font=("Arial", 14))

        for i in range(self.num_vertices):
            for j in self.adj_list[i]:
                x1, y1 = self.vertices_positions[i]
                x2, y2 = self.vertices_positions[j]
                self.canvas.create_line(x1, y1, x2, y2, fill="black")

    def solve_with_genetic_algorithm(self):
        """Run the genetic algorithm to solve the graph coloring problem."""
        self.population = self.generate_population()
        self.evolve_graph_coloring()

    def generate_population(self):
        """Initialize a random population of color assignments."""
        return [[random.randint(0, self.num_colors - 1) for _ in range(self.num_vertices)]
                for _ in range(self.population_size)]

    def fitness(self, individual):
        """Calculate fitness based strictly on the number of conflicts."""
        conflicts = 0
        for i in range(self.num_vertices):
            for j in self.adj_list[i]:
                if individual[i] == individual[j]:
                    conflicts += 1
        return conflicts  # Lower is better; zero conflicts is ideal.

    def evolve_graph_coloring(self):
        generations = 1000
        for generation in range(generations):
            # Update generation label on UI
            self.generation_label.config(text=f"Generation: {generation}")
            self.update_idletasks()

            fitness_scores = [self.fitness(ind) for ind in self.population]
            best_fitness = min(fitness_scores)

            # Check if a solution has been found
            if best_fitness == 0:  # Ideal solution reached
                solution = self.population[fitness_scores.index(best_fitness)]
                self.draw_graph(solution)

                # Update status and show success message
                self.status_var.set("Status: Solution Found!")
                messagebox.showinfo("Success", "A solution has been found!")
                return

            # Select parents and generate new population
            parents = self.select_parents(fitness_scores)
            new_population = parents[:]
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(parents, 2)
                child = self.multi_point_crossover(parent1, parent2)
                child = self.adaptive_mutate(child, generation)
                new_population.append(child)

            # Update population and show best solution found so far
            self.population = new_population
            self.draw_graph(self.population[fitness_scores.index(best_fitness)])

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
        mutation_rate = max(0.05, 0.5 - (generation * 0.0005))
        for i in range(self.num_vertices):
            if random.random() < mutation_rate:
                individual[i] = random.randint(0, self.num_colors - 1)
        return individual

# Run the app
if __name__ == '__main__':
    app = GraphColoringApp()
    app.mainloop()
