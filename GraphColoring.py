import math
import random
import tkinter as tk
from tkinter import *

num_nodes = 50
num_edges = 100
node_scale = 15  # Increased to 15
edge_width = 2
padding = 100


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = None
        self.neighbors = []

    def draw(self, canvas):
        color = self.color if self.color else "black"
        canvas.create_oval(
            self.x - node_scale,
            self.y - node_scale,
            self.x + node_scale,
            self.y + node_scale,
            fill=color,
        )


class Edge:
    def __init__(self, a, b):
        self.node_a = a
        self.node_b = b
        self.length = math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    def draw(self, canvas, color="grey", style=(2, 4)):
        canvas.create_line(
            self.node_a.x,
            self.node_a.y,
            self.node_b.x,
            self.node_b.y,
            fill=color,
            width=edge_width,
            dash=style,
        )


class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Graph Coloring")
        self.option_add("*tearOff", FALSE)
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (width, height))
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=width, height=height)
        self.w = width - padding
        self.h = height - padding * 2

        self.nodes_list = []
        self.edges_list = []
        self.edges_set = set()

        self.solver_method = "greedy"  # Default solver method
        self.iteration_label = tk.Label(
            self, text="Iterations: 0", font=("Helvetica", 16)
        )
        self.iteration_label.place(x=10, y=10)

        def add_node():
            # Arrange nodes in a circular layout
            angle = (2 * math.pi / num_nodes) * len(self.nodes_list)
            radius = min(self.w, self.h) / 2 - padding
            center_x = self.w / 2 + padding / 2
            center_y = self.h / 2 + padding / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            node = Node(x, y)
            self.nodes_list.append(node)

        def add_edge():
            a = random.randint(0, len(self.nodes_list) - 1)
            b = random.randint(0, len(self.nodes_list) - 1)
            edge_key = (min(a, b), max(a, b))
            while a == b or edge_key in self.edges_set:
                a = random.randint(0, len(self.nodes_list) - 1)
                b = random.randint(0, len(self.nodes_list) - 1)
                edge_key = (min(a, b), max(a, b))

            edge = Edge(self.nodes_list[a], self.nodes_list[b])
            self.edges_set.add(edge_key)
            self.edges_list.append(edge)

            # Update neighbors
            self.nodes_list[a].neighbors.append(self.nodes_list[b])
            self.nodes_list[b].neighbors.append(self.nodes_list[a])

        def generate_graph():
            self.nodes_list.clear()
            self.edges_list.clear()
            self.edges_set.clear()
            self.iteration_label.config(text="Iterations: 0")
            for _ in range(num_nodes):
                add_node()
            for _ in range(num_edges):
                add_edge()
            draw_graph()

        def draw_graph():
            clear_canvas()
            for e in self.edges_list:
                e.draw(self.canvas)
            for n in self.nodes_list:
                n.draw(self.canvas)

        def clear_canvas():
            self.canvas.delete("all")

        def set_solver(method):
            self.solver_method = method

        def solve():
            self.iteration_label.config(text="Iterations: 0")
            if self.solver_method == "greedy":
                color_graph()
            elif self.solver_method == "genetic":
                genetic_algorithm()
            draw_graph()

        def color_graph():
            colors = [
                "red",
                "green",
                "blue",
                "yellow",
                "cyan",
                "magenta",
                "orange",
                "purple",
                "pink",
                "brown",
                "gray",
                "olive",
                "maroon",
            ]
            iteration = 1  # Since greedy algorithm runs once
            for node in self.nodes_list:
                used_colors = set(
                    neighbor.color for neighbor in node.neighbors if neighbor.color
                )
                for color in colors:
                    if color not in used_colors:
                        node.color = color
                        break
                else:
                    node.color = "black"  # Default color if no other color is available
            self.iteration_label.config(text=f"Iterations: {iteration}")

        def genetic_algorithm():
            # Parameters
            population_size = 100
            mutation_rate = 0.1
            max_iterations = 1000
            num_colors = 4  # Number of colors to use
            colors = ["red", "green", "blue", "yellow"]

            # Initialize population
            population = []
            for _ in range(population_size):
                individual = [random.choice(range(num_colors)) for _ in self.nodes_list]
                population.append(individual)

            best_individual = None
            best_fitness = float("inf")
            iteration = 0

            while iteration < max_iterations and best_fitness > 0:
                iteration += 1
                # Evaluate fitness
                fitness_scores = []
                for individual in population:
                    fitness = fitness_function(individual)
                    fitness_scores.append((fitness, individual))
                    if fitness < best_fitness:
                        best_fitness = fitness
                        best_individual = individual

                # Sort population by fitness
                fitness_scores.sort(key=lambda x: x[0])
                population = [ind for (_, ind) in fitness_scores]

                # Selection
                selected = selection(population, fitness_scores)

                # Crossover
                offspring = crossover(selected)

                # Mutation
                offspring = mutation(offspring, mutation_rate, num_colors)

                # Replace population
                population = offspring

                # Update iteration label
                self.iteration_label.config(text=f"Iterations: {iteration}")
                self.update_idletasks()

            # Assign colors to nodes
            for idx, node in enumerate(self.nodes_list):
                node.color = colors[best_individual[idx]]

        def fitness_function(individual):
            conflicts = 0
            for edge in self.edges_list:
                idx_a = self.nodes_list.index(edge.node_a)
                idx_b = self.nodes_list.index(edge.node_b)
                if individual[idx_a] == individual[idx_b]:
                    conflicts += 1
            return conflicts

        def selection(population, fitness_scores):
            selected = []
            tournament_size = 5
            for _ in range(len(population)):
                tournament = random.sample(fitness_scores, tournament_size)
                tournament.sort(key=lambda x: x[0])
                selected.append(
                    tournament[0][1]
                )  # Select the individual with best fitness
            return selected

        def crossover(parents):
            offspring = []
            for i in range(0, len(parents), 2):
                parent1 = parents[i]
                if i + 1 < len(parents):
                    parent2 = parents[i + 1]
                else:
                    parent2 = parents[0]  # If odd number, mate last with first
                # Perform single-point crossover
                crossover_point = random.randint(1, len(parent1) - 1)
                child1 = parent1[:crossover_point] + parent2[crossover_point:]
                child2 = parent2[:crossover_point] + parent1[crossover_point:]
                offspring.append(child1)
                offspring.append(child2)
            return offspring

        def mutation(offspring, mutation_rate, num_colors):
            for individual in offspring:
                for idx in range(len(individual)):
                    if random.random() < mutation_rate:
                        individual[idx] = random.choice(range(num_colors))
            return offspring

        # Create menu
        menu_bar = Menu(self)
        self["menu"] = menu_bar

        menu_gc = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_gc, label="Graph Coloring", underline=0)
        menu_gc.add_command(label="Generate", command=generate_graph, underline=0)
        menu_gc.add_command(label="Solve", command=solve, underline=0)

        menu_solver = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_solver, label="Solver", underline=0)
        menu_solver.add_command(
            label="Use Greedy Algorithm",
            command=lambda: set_solver("greedy"),
            underline=0,
        )
        menu_solver.add_command(
            label="Use Genetic Algorithm",
            command=lambda: set_solver("genetic"),
            underline=0,
        )

        self.mainloop()


if __name__ == "__main__":
    UI()
