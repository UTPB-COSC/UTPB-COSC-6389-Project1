import random
import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class LongestPathProblem:
    def __init__(self, num_vertices, num_edges):
        self.num_vertices = num_vertices
        self.num_edges = num_edges
        self.graph = nx.Graph()
        self.generate_graph()

    def generate_graph(self):
        self.graph.clear()
        self.graph.add_nodes_from(range(self.num_vertices))
        while self.graph.number_of_edges() < self.num_edges:
            u = random.randint(0, self.num_vertices - 1)
            v = random.randint(0, self.num_vertices - 1)
            if u != v and not self.graph.has_edge(u, v):
                self.graph.add_edge(u, v)


class GeneticAlgorithm:
    def __init__(
        self,
        graph,
        population_size=50,
        generations=100,
        callback=None,
        show_steps=False,
    ):
        self.graph = graph
        self.population_size = population_size
        self.generations = generations
        self.callback = callback
        self.show_steps = show_steps

    def generate_individual(self):
        return random.sample(list(self.graph.nodes()), self.graph.number_of_nodes())

    def fitness(self, individual):
        path_length = 0
        for i in range(len(individual) - 1):
            if self.graph.has_edge(individual[i], individual[i + 1]):
                path_length += 1
            else:
                break
        return path_length

    def crossover(self, parent1, parent2):
        crossover_point = random.randint(1, len(parent1) - 1)
        child = parent1[:crossover_point]
        for gene in parent2:
            if gene not in child:
                child.append(gene)
        return child

    def mutate(self, individual):
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]
        return individual

    def solve(self):
        population = [self.generate_individual() for _ in range(self.population_size)]
        best_solution = None
        best_fitness = -1

        for generation in range(self.generations):
            population = sorted(population, key=self.fitness, reverse=True)
            current_best = population[0]
            current_best_fitness = self.fitness(current_best)

            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_solution = current_best

            # Callback for intermediate visualization
            if self.show_steps and self.callback and generation % 10 == 0:
                # Show intermediate result
                self.callback(best_solution)

            if generation % 10 == 0:
                print(f"GA Generation {generation}: Best fitness = {best_fitness}")

            # Create new population
            new_population = population[:2]  # Elitism
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(population[:10], 2)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)

            population = new_population

        return best_solution, best_fitness


class AntColonyOptimization:
    def __init__(
        self,
        graph,
        num_ants=10,
        iterations=100,
        alpha=1,
        beta=1,
        evaporation_rate=0.5,
        callback=None,
        show_steps=False,
    ):
        self.graph = graph
        self.num_ants = num_ants
        self.iterations = iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.pheromone = {(u, v): 1.0 for u, v in self.graph.edges()}
        self.callback = callback
        self.show_steps = show_steps

    def solve(self):
        best_path = []
        best_length = 0

        for iteration in range(self.iterations):
            paths = self.construct_paths()
            self.update_pheromone(paths)

            iteration_best_path = max(paths, key=lambda x: len(x) - 1)
            iteration_best_length = len(iteration_best_path) - 1

            if iteration_best_length > best_length:
                best_path = iteration_best_path
                best_length = iteration_best_length

            if self.show_steps and self.callback and iteration % 10 == 0:
                self.callback(best_path)

            if iteration % 10 == 0:
                print(f"ACO Iteration {iteration}: Best length = {best_length}")

        return best_path, best_length

    def construct_paths(self):
        paths = []
        for _ in range(self.num_ants):
            path = self.construct_path()
            paths.append(path)
        return paths

    def construct_path(self):
        start_node = random.choice(list(self.graph.nodes()))
        path = [start_node]
        current_node = start_node

        while True:
            neighbors = list(self.graph.neighbors(current_node))
            unvisited_neighbors = [n for n in neighbors if n not in path]

            if not unvisited_neighbors:
                break

            probabilities = self.calculate_probabilities(
                current_node, unvisited_neighbors
            )
            next_node = random.choices(unvisited_neighbors, weights=probabilities)[0]

            path.append(next_node)
            current_node = next_node

        return path

    def calculate_probabilities(self, current_node, neighbors):
        probabilities = []
        for neighbor in neighbors:
            pheromone = self.pheromone.get((current_node, neighbor), 1.0)
            probabilities.append(pheromone**self.alpha)
        return probabilities

    def update_pheromone(self, paths):
        for edge in self.pheromone:
            self.pheromone[edge] *= 1 - self.evaporation_rate

        for path in paths:
            path_length = len(path) - 1
            if path_length > 0:
                for i in range(path_length):
                    edge = tuple(sorted([path[i], path[i + 1]]))
                    self.pheromone[edge] += 1.0 / path_length


class Backtracking:
    def __init__(self, graph, callback=None, show_steps=False):
        self.graph = graph
        self.best_path = []
        self.best_length = 0
        self.callback = callback
        self.show_steps = show_steps

    def solve(self):
        for start_node in self.graph.nodes():
            self.dfs(start_node, [start_node])
        return self.best_path, self.best_length

    def dfs(self, node, path):
        if len(path) > self.best_length:
            self.best_path = path.copy()
            self.best_length = len(path)
            print(f"Backtracking: New best length = {self.best_length}")
            # Show intermediate steps if enabled
            if self.show_steps and self.callback:
                self.callback(self.best_path)

        neighbors = list(self.graph.neighbors(node))
        for neighbor in neighbors:
            if neighbor not in path:
                self.dfs(neighbor, path + [neighbor])


class LongestPathUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Longest Path Problem Solver")
        self.geometry("800x600")

        self.problem = None
        self.pos = None
        self.show_steps_var = tk.BooleanVar(value=False)
        self.create_widgets()

    def create_widgets(self):
        self.frame = ttk.Frame(self)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.vertices_var = tk.IntVar(value=10)
        self.edges_var = tk.IntVar(value=15)

        ttk.Label(self.frame, text="Number of Vertices:").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Entry(self.frame, textvariable=self.vertices_var).grid(row=0, column=1)

        ttk.Label(self.frame, text="Number of Edges:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.edges_var).grid(row=1, column=1)

        ttk.Button(self.frame, text="Generate Graph", command=self.generate_graph).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        ttk.Button(self.frame, text="Solve with GA", command=self.solve_ga).grid(
            row=3, column=0, pady=5
        )
        ttk.Button(self.frame, text="Solve with ACO", command=self.solve_aco).grid(
            row=3, column=1, pady=5
        )
        ttk.Button(
            self.frame, text="Solve with Backtracking", command=self.solve_backtracking
        ).grid(row=4, column=0, columnspan=2, pady=5)

        show_steps_check = ttk.Checkbutton(
            self.frame, text="Show intermediate steps", variable=self.show_steps_var
        )
        show_steps_check.grid(row=5, column=0, columnspan=2, pady=5)

        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=6, column=0, columnspan=2, pady=10)

    def generate_graph(self):
        num_vertices = self.vertices_var.get()
        num_edges = self.edges_var.get()
        self.problem = LongestPathProblem(num_vertices, num_edges)

        # Calculate and store a fixed layout for consistent visualization
        self.pos = nx.spring_layout(self.problem.graph)

        self.draw_graph()

    def draw_graph(self, path=None):
        if not self.problem:
            return
        self.ax.clear()
        # Use stored positions for consistency
        nx.draw(
            self.problem.graph,
            self.pos,
            ax=self.ax,
            with_labels=True,
            node_color="lightblue",
            node_size=500,
            font_size=8,
            font_weight="bold",
        )

        if path:
            path_edges = list(zip(path[:-1], path[1:]))
            nx.draw_networkx_edges(
                self.problem.graph,
                self.pos,
                edgelist=path_edges,
                edge_color="r",
                width=2,
                ax=self.ax,
            )

        self.canvas.draw()

    def intermediate_callback(self, path):
        # Callback function to update UI with intermediate solutions
        self.draw_graph(path)
        self.update_idletasks()

    def solve_ga(self):
        if not self.problem:
            messagebox.showerror("Error", "Please generate a graph first.")
            return

        ga = GeneticAlgorithm(
            self.problem.graph,
            callback=self.intermediate_callback,
            show_steps=self.show_steps_var.get(),
        )
        solution, length = ga.solve()
        self.draw_graph(solution)
        messagebox.showinfo("Result", f"GA found a path of length {length}")

    def solve_aco(self):
        if not self.problem:
            messagebox.showerror("Error", "Please generate a graph first.")
            return

        aco = AntColonyOptimization(
            self.problem.graph,
            callback=self.intermediate_callback,
            show_steps=self.show_steps_var.get(),
        )
        solution, length = aco.solve()
        self.draw_graph(solution)
        messagebox.showinfo("Result", f"ACO found a path of length {length}")

    def solve_backtracking(self):
        if not self.problem:
            messagebox.showerror("Error", "Please generate a graph first.")
            return

        backtracking = Backtracking(
            self.problem.graph,
            callback=self.intermediate_callback,
            show_steps=self.show_steps_var.get(),
        )
        solution, length = backtracking.solve()
        self.draw_graph(solution)
        messagebox.showinfo("Result", f"Backtracking found a path of length {length}")


if __name__ == "__main__":
    app = LongestPathUI()
    app.mainloop()
