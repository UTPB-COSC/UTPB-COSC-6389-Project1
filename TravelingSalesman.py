import math
import random
import tkinter as tk
from tkinter import Menu, FALSE, Canvas, Frame, Button

# Configuration parameters
num_cities = 25
city_scale = 5
road_width = 2
padding = 50

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

class TSP_Solver:
    def __init__(self, cities):
        self.cities = cities
        self.num_cities = len(cities)
        self.distance_matrix = self.calculate_distance_matrix()
        self.current_solution = list(range(self.num_cities))
        random.shuffle(self.current_solution)
        self.best_solution = self.current_solution[:]
        self.best_distance = self.calculate_total_distance(self.best_solution)
        self.temperature = 1000  # Adjusted initial temperature
        self.min_temperature = 1e-4  # Minimum temperature for stopping
        self.cooling_rate = 0.999  # Slower cooling rate
        self.iterations_per_temp = 100  # More iterations at each temperature
        self.iteration = 0
        self.max_iterations = 100000  # Maximum iterations
        self.no_improvement_counter = 0
        self.max_no_improvement = 1000  # Early stopping criteria

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

    def calculate_total_distance(self, solution):
        distance = 0
        for i in range(len(solution)):
            a = solution[i]
            b = solution[(i + 1) % len(solution)]
            distance += self.distance_matrix[a][b]
        return distance

    def two_opt_swap(self, solution):
        new_solution = solution[:]
        i, k = sorted(random.sample(range(1, self.num_cities), 2))
        new_solution[i:k] = reversed(new_solution[i:k])
        return new_solution

    def anneal(self):
        for _ in range(self.iterations_per_temp):
            self.iteration += 1
            new_solution = self.two_opt_swap(self.current_solution)
            current_distance = self.calculate_total_distance(self.current_solution)
            new_distance = self.calculate_total_distance(new_solution)
            acceptance_prob = self.acceptance_probability(current_distance, new_distance, self.temperature)
            if acceptance_prob > random.random():
                self.current_solution = new_solution
                current_distance = new_distance
                if current_distance < self.best_distance:
                    self.best_distance = current_distance
                    self.best_solution = self.current_solution[:]
                    self.no_improvement_counter = 0
                else:
                    self.no_improvement_counter += 1
            else:
                self.no_improvement_counter += 1
            if self.no_improvement_counter > self.max_no_improvement or self.iteration > self.max_iterations:
                self.temperature = self.min_temperature  # Force termination
                break
        self.temperature = max(self.temperature * self.cooling_rate, self.min_temperature)

    def acceptance_probability(self, current_distance, new_distance, temperature):
        if new_distance < current_distance:
            return 1.0
        else:
            return math.exp((current_distance - new_distance) / temperature)

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
        menu_TS.add_command(label="Run", command=self.start_solver, underline=0)

        # City list and solver instance
        self.cities_list = []
        self.tsp_solver = None
        self.is_running = False

        # Control buttons
        self.generate_button = Button(self.control_frame, text="Generate Cities", command=self.generate, font=('Arial', 14))
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.run_button = Button(self.control_frame, text="Run Solver", command=self.start_solver, font=('Arial', 14))
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

    def start_solver(self):
        if not self.cities_list:
            self.generate()
        self.tsp_solver = TSP_Solver(self.cities_list)
        self.is_running = True
        self.run_solver()

    def run_solver(self):
        if self.is_running and self.tsp_solver.temperature > self.tsp_solver.min_temperature:
            self.tsp_solver.anneal()
            self.clear_canvas()
            # Draw the best solution so far
            self.draw_solution(self.tsp_solver.best_solution, path_color='green', city_color='blue')
            # Optionally, draw the current solution in a different color
            self.draw_solution(self.tsp_solver.current_solution, path_color='red', city_color='yellow', draw_cities=False)
            self.canvas.update()
            self.after(1, self.run_solver)
        else:
            self.is_running = False
            print(f"Best distance found: {self.tsp_solver.best_distance}")
            self.display_best_distance()

    def display_best_distance(self):
        # Add a message to display the best distance found
        self.canvas.create_text(
            padding, padding,
            text=f"Best Distance Found: {int(self.tsp_solver.best_distance)}",
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
            text=f"Current Best Distance: {int(self.tsp_solver.best_distance)}",
            font=('Arial', 20, 'bold'),
            fill='green',
            anchor='nw'
        )

if __name__ == '__main__':
    ui = UI()
    ui.mainloop()
