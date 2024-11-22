import math
import random
import tkinter as tk
from tkinter import Menu, FALSE, Canvas, Frame, Button

# Configuration parameters
num_cities = 25
city_scale = 5
road_width = 2
padding = 50
alpha = 1.0  # Influence of pheromone
beta = 5.0  # Influence of distance
rho = 0.5  # Pheromone evaporation rate
q = 100  # Constant used in pheromone update
num_ants = 20  # Number of ants
iterations = 100  # Number of iterations

class Node:
    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.index = index  # Unique identifier for the city

    def draw(self, canvas, color='yellow'):
        canvas.create_oval(
            self.x - city_scale * 2, self.y - city_scale * 2,
            self.x + city_scale * 2, self.y + city_scale * 2,
            fill=color, outline='black'
        )
        canvas.create_text(
            self.x, self.y - city_scale * 3,
            text=str(self.index),
            font=('Arial', 12),
            fill='blue'
        )

class Edge:
    def __init__(self, a, b):
        self.city_a = a
        self.city_b = b
        self.length = math.hypot(a.x - b.x, a.y - b.y)

    def draw(self, canvas, color='grey', style=None):
        kwargs = {'fill': color, 'width': road_width}
        if style:
            kwargs['dash'] = style
        canvas.create_line(
            self.city_a.x, self.city_a.y,
            self.city_b.x, self.city_b.y,
            **kwargs
        )

class AntColonyOptimizer:
    def __init__(self, cities, num_ants, alpha, beta, rho, q, iterations):
        self.cities = cities
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        self.iterations = iterations
        self.num_cities = len(cities)
        self.distance_matrix = self.calculate_distance_matrix()
        self.pheromone_matrix = [[1.0] * self.num_cities for _ in range(self.num_cities)]
        self.best_solution = None
        self.best_distance = float('inf')

    def calculate_distance_matrix(self):
        matrix = [[0]*self.num_cities for _ in range(self.num_cities)]
        for i in range(self.num_cities):
            for j in range(i+1, self.num_cities):
                dist = math.hypot(
                    self.cities[i].x - self.cities[j].x,
                    self.cities[i].y - self.cities[j].y
                )
                matrix[i][j] = dist
                matrix[j][i] = dist
        return matrix

    def optimize(self):
        for iteration in range(self.iterations):
            print(f"Iteration: {iteration + 1}")
            all_solutions = []
            for _ in range(self.num_ants):
                solution = self.construct_solution()
                distance = self.calculate_total_distance(solution)
                all_solutions.append((solution, distance))
                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_solution = solution
            self.update_pheromones(all_solutions)

    def construct_solution(self):
        solution = [random.randint(0, self.num_cities - 1)]
        while len(solution) < self.num_cities:
            current_city = solution[-1]
            next_city = self.select_next_city(current_city, solution)
            solution.append(next_city)
        return solution

    def select_next_city(self, current_city, visited):
        probabilities = []
        for next_city in range(self.num_cities):
            if next_city not in visited:
                pheromone = self.pheromone_matrix[current_city][next_city] ** self.alpha
                distance = self.distance_matrix[current_city][next_city] ** (-self.beta)
                probabilities.append((next_city, pheromone * distance))
        total_prob = sum(prob for _, prob in probabilities)
        rand = random.uniform(0, total_prob)
        cumulative_prob = 0.0
        for next_city, prob in probabilities:
            cumulative_prob += prob
            if rand <= cumulative_prob:
                return next_city
        return probabilities[-1][0]

    def update_pheromones(self, all_solutions):
        # Evaporate pheromones
        for i in range(self.num_cities):
            for j in range(self.num_cities):
                self.pheromone_matrix[i][j] *= (1 - self.rho)
        # Add pheromones based on solutions
        for solution, distance in all_solutions:
            for i in range(len(solution)):
                a = solution[i]
                b = solution[(i + 1) % len(solution)]
                self.pheromone_matrix[a][b] += self.q / distance
                self.pheromone_matrix[b][a] += self.q / distance

    def calculate_total_distance(self, solution):
        distance = 0
        for i in range(len(solution)):
            a = solution[i]
            b = solution[(i + 1) % len(solution)]
            distance += self.distance_matrix[a][b]
        return distance

class UI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Traveling Salesman Problem Solver")
        self.option_add("*tearOff", FALSE)
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}+0+0")
        self.state("zoomed")

        # Main Frame
        self.main_frame = Frame(self)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # Canvas for drawing cities and roads
        self.canvas = Canvas(self.main_frame, bg='white')
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Control frame for buttons
        self.control_frame = Frame(self.main_frame)
        self.control_frame.pack(side=tk.BOTTOM, pady=20)

        # Menu bar setup
        menu_bar = Menu(self)
        self.config(menu=menu_bar)
        menu_TS = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_TS, label='Salesman', underline=0)

        menu_TS.add_command(label="Generate", command=self.generate, underline=0)
        menu_TS.add_command(label="Run ACO", command=self.start_aco_solver, underline=0)

        # City list and solver instance
        self.cities_list = []
        self.aco_solver = None
        self.is_running = False

        # Control buttons
        self.generate_button = Button(self.control_frame, text="Generate Cities", command=self.generate, font=('Arial', 14))
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.run_button = Button(self.control_frame, text="Run ACO Solver", command=self.start_aco_solver, font=('Arial', 14))
        self.run_button.pack(side=tk.LEFT, padx=5)

    def generate(self):
        self.clear_canvas()
        self.cities_list.clear()
        for i in range(num_cities):
            self.add_city(i)
        self.draw_cities()

    def add_city(self, index):
        x = random.randint(padding, self.width - padding)
        y = random.randint(padding, self.height - padding)
        node = Node(x, y, index)
        self.cities_list.append(node)

    def draw_cities(self):
        for city in self.cities_list:
            city.draw(self.canvas)

    def clear_canvas(self):
        self.canvas.delete("all")

    def start_aco_solver(self):
        if not self.cities_list:
            self.generate()
        self.aco_solver = AntColonyOptimizer(
            self.cities_list, num_ants, alpha, beta, rho, q, iterations
        )
        self.is_running = True
        self.run_aco_solver()

    def run_aco_solver(self):
        if self.is_running:
            self.aco_solver.optimize()
            self.clear_canvas()
            # Draw the best solution found by ACO
            self.draw_solution(self.aco_solver.best_solution, path_color='green', city_color='blue')
            self.canvas.update()
            self.is_running = False
            self.display_best_distance()

    def display_best_distance(self):
        # Add a message to display the best distance found
        self.canvas.create_text(
            padding, padding,
            text=f"Best Distance Found: {int(self.aco_solver.best_distance)}",
            font=('Arial', 20, 'bold'),
            fill='green',
            anchor='nw'
        )

    def draw_solution(self, solution, path_color='red', city_color='blue', draw_cities=True):
        # Draw the path
        for i in range(len(solution)):
            city_a = self.cities_list[solution[i]]
            city_b = self.cities_list[solution[(i + 1) % len(solution)]]
            edge = Edge(city_a, city_b)
            edge.draw(self.canvas, color=path_color)  # Use the specified path color
        # Draw the cities if required
        if draw_cities:
            for city in self.cities_list:
                city.draw(self.canvas, color=city_color)
        # Display current best distance
        self.canvas.create_text(
            padding, padding // 2,
            text=f"Current Best Distance: {int(self.aco_solver.best_distance)}",
            font=('Arial', 20, 'bold'),
            fill='green',
            anchor='nw'
        )

if __name__ == '__main__':
    ui = UI()
    ui.mainloop()
