import math
import random
import tkinter as tk

# Configuration constants
num_cities = 25
city_scale = 5
road_width = 2
padding = 100


# Node class representing a city
class Node:
    def __init__(self, x, y):
        self.x = x # x-coordinate of the city
        self.y = y # y-coordinate of the city

    def draw(self, canvas, color='black'):
        # Draw the city as a circle on the canvas
        canvas.create_oval(self.x - city_scale, self.y - city_scale,
                           self.x + city_scale, self.y + city_scale, fill=color)


# Edge class representing a road between two cities
class Edge:
    def __init__(self, a, b):
        self.city_a = a # First city
        self.city_b = b # Second city
        self.length = math.hypot(a.x - b.x, a.y - b.y) # Calculate road length

    def draw(self, canvas, color='grey', style=(2, 4)):
        # Draw the road as a dashed line on the canvas
        canvas.create_line(self.city_a.x,
                           self.city_a.y,
                           self.city_b.x,
                           self.city_b.y,
                           fill=color,
                           width=road_width,
                           dash=style)


# UI class for the application
class UI(tk.Tk):
    def __init__(self):
        # Initialize the Tkinter window
        super().__init__()
        self.title("Traveling Salesman Problem")

        # Set the window size to full screen
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{width}x{height}+0+0")
        self.state("zoomed")

        # Create a canvas for drawing
        self.canvas = tk.Canvas(self)
        self.canvas.place(x=0, y=0, width=width, height=height)

        # Initialize lists to hold cities and edges
        self.cities = []
        self.edges = []

        # Create a menu bar
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        # Add options to the menu
        salesman_menu = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=salesman_menu, label='Salesman')
        salesman_menu.add_command(label="Generate Cities", command=self.generate_cities_and_edges)
        salesman_menu.add_command(label="Solve with 2-Opt", command=self.solve_with_two_opt)
        salesman_menu.add_command(label="Solve with Genetic Algorithm", command=self.solve_with_genetic)
        salesman_menu.add_command(label="Solve with PSO", command=self.solve_with_pso)

        self.mainloop()

    def generate_cities_and_edges(self):
        # Clear previous cities and edges
        self.cities.clear()
        self.edges.clear()

        # Generate new cities and edges
        self.create_random_cities()
        self.create_edges_between_cities()
        self.display_cities_and_edges()

    def create_random_cities(self):
        # Create a specified number of random cities
        for _ in range(num_cities):
            x = random.randint(padding, self.winfo_width() - padding)
            y = random.randint(padding, self.winfo_height() - padding)
            city = Node(x, y)
            self.cities.append(city)

    def create_edges_between_cities(self):
        # Create edges between all pairs of cities
        for i in range(len(self.cities)):
            for j in range(i + 1, len(self.cities)):
                edge = Edge(self.cities[i], self.cities[j])
                self.edges.append(edge)

    def display_cities_and_edges(self):
        # Clear the canvas and draw cities and edges
        self.canvas.delete("all")
        for edge in self.edges:
            edge.draw(self.canvas, color='grey', style=(2, 4))
        for city in self.cities:
            city.draw(self.canvas, color='black')

    def solve_with_two_opt(self):
        # Check if cities are available to solve
        if not self.cities:
            return
        self.initialize_tour()
        self.display_current_tour()
        self.perform_two_opt_optimization()

    def initialize_tour(self):
        # Create an initial random tour of cities
        self.tour = list(range(len(self.cities)))
        random.shuffle(self.tour)
        self.best_distance = self.calculate_tour_distance(self.tour)
        self.iteration_i = 1
        self.iteration_k = self.iteration_i + 1

    def calculate_tour_distance(self, tour):
        # Calculate the total distance of the tour
        total_distance = 0
        for i in range(len(tour)):
            city_a = self.cities[tour[i]]
            city_b = self.cities[tour[(i + 1) % len(tour)]]
            distance = math.hypot(city_a.x - city_b.x, city_a.y - city_b.y)
            total_distance += distance
        return total_distance

    def swap_two_opt(self, tour, i, k):
        # Swap the tour segments for the 2-opt optimization
        new_tour = tour[:i] + tour[i:k + 1][::-1] + tour[k + 1:]
        return new_tour

    def perform_two_opt_optimization(self):
        # Perform the 2-opt optimization step
        if self.iteration_i >= len(self.tour) - 1:
            print(f"2-Opt Optimization complete. Final distance: {self.best_distance:.2f}")
            return

        i = self.iteration_i
        k = self.iteration_k
        new_tour = self.swap_two_opt(self.tour, i, k) # Swap segments
        new_distance = self.calculate_tour_distance(new_tour) # Calculate new distance

        if new_distance < self.best_distance:
            self.tour = new_tour # Update tour if new distance is better
            self.best_distance = new_distance
            print(f"New best distance: {self.best_distance:.2f}")
            self.iteration_i = 1 # Reset iteration indices
            self.iteration_k = self.iteration_i + 1
            self.display_current_tour() # Display updated tour
        else:
            self.iteration_k += 1 # Increment k for next swap
            if self.iteration_k >= len(self.tour):
                self.iteration_i += 1 # Increment i to move to the next segment
                self.iteration_k = self.iteration_i + 1

        self.after(1, self.perform_two_opt_optimization) # Schedule next optimization step

    def display_current_tour(self):
        # Clear the canvas and draw the current tour
        self.canvas.delete("all")
        for edge in self.edges:
            edge.draw(self.canvas, color='grey', style=(2, 4))

        for i in range(len(self.tour)):
            city_a = self.cities[self.tour[i]]
            city_b = self.cities[self.tour[(i + 1) % len(self.tour)]]
            self.canvas.create_line(city_a.x, city_a.y, city_b.x, city_b.y, fill='red', width=road_width)

        for city in self.cities:
            city.draw(self.canvas, 'red') # Draw current cities in red

    def solve_with_genetic(self):
        # Check if cities are available to solve
        if not self.cities:
            return
        self.setup_genetic_algorithm() # Initialize genetic algorithm
        self.evolve_population() # Start evolving population

    def setup_genetic_algorithm(self):
        # Initialize parameters for the genetic algorithm
        self.population_size = 100
        self.generations = 500
        self.mutation_rate = 0.01
        self.create_initial_population() # Create initial population
        self.generation = 0 # Start generation count
        self.best_individual = None # Track the best individual found
        self.best_distance = float('inf') # Initialize best distance

    def create_initial_population(self):
        # Create a random initial population
        self.population = []
        for _ in range(self.population_size):
            individual = list(range(len(self.cities)))
            random.shuffle(individual) # Shuffle to create a random tour
            self.population.append(individual)

    def evolve_population(self):
        # Evolve the population over generations
        if self.generation >= self.generations:
            print(f"Genetic Algorithm complete. Final distance: {self.best_distance:.2f}")
            self.tour = self.best_individual # Set the best tour found
            self.display_current_tour()
            return

        self.generation += 1 # increment generation count
        self.evaluate_population() # Evaluate fitness of individuals
        self.perform_selection() # Select individuals for the next generation
        self.perform_crossover() # Create new individuals via crossover
        self.perform_mutation() # Apply mutation to the population
        self.after(1, self.evolve_population) # Schedule next evolution step

    def evaluate_population(self):
        # Evaluate the fitness of each individual in the population
        fitness_scores = []
        for individual in self.population:
            distance = self.calculate_tour_distance(individual) # Calculate distance of the tour
            fitness_scores.append((1 / distance, individual))
            if distance < self.best_distance:
                self.best_distance = distance
                self.best_individual = individual.copy()
                print(f"Generation {self.generation}: New best distance: {self.best_distance:.2f}")
                self.tour = self.best_individual
                self.display_current_tour()

        self.fitness_scores = fitness_scores

    def perform_selection(self):
        # Select individuals for the next generation using roulette wheel selection
        self.population = [ind for _, ind in sorted(self.fitness_scores, reverse=True)]
        total_fitness = sum(score for score, _ in self.fitness_scores)
        probabilities = [score / total_fitness for score, _ in self.fitness_scores]
        cumulative_probabilities = []
        cumulative = 0
        for p in probabilities:
            cumulative += p
            cumulative_probabilities.append(cumulative)

        new_population = []
        for _ in range(self.population_size):
            r = random.random()
            for i, cumulative_probability in enumerate(cumulative_probabilities):
                if r < cumulative_probability:
                    new_population.append(self.population[i])
                    break
        self.population = new_population

    def perform_crossover(self):
        # Perform crossover between selected individuals
        new_population = []
        for _ in range(self.population_size // 2):
            parent_a = random.choice(self.population)
            parent_b = random.choice(self.population)
            crossover_point = random.randint(1, len(parent_a) - 1)
            child_a = parent_a[:crossover_point] + [gene for gene in parent_b if gene not in parent_a[:crossover_point]]
            child_b = parent_b[:crossover_point] + [gene for gene in parent_a if gene not in parent_b[:crossover_point]]
            new_population.append(child_a)
            new_population.append(child_b)
        self.population = new_population

    def perform_mutation(self):
        # Apply mutation to the population
        for individual in self.population:
            if random.random() < self.mutation_rate:
                idx_a, idx_b = random.sample(range(len(individual)), 2)
                individual[idx_a], individual[idx_b] = individual[idx_b], individual[idx_a]

    def solve_with_pso(self):
        # Check if cities are available to solve
        if not self.cities:
            return
        self.setup_pso_algorithm()
        self.run_pso()

    def setup_pso_algorithm(self):
        # Initialize parameters for the PSO algorithm
        self.num_particles = 30
        self.max_iterations = 100
        self.particles = []
        self.best_global_position = None
        self.best_global_distance = float('inf')

        # Create particles with random initial positions
        for _ in range(self.num_particles):
            particle = {
                'position': list(range(len(self.cities))),
                'velocity': [random.uniform(-1, 1) for _ in range(len(self.cities))],
                'best_position': None,
                'best_distance': float('inf')
            }
            random.shuffle(particle['position'])
            self.particles.append(particle)

    def run_pso(self):
        # Main PSO loop
        for iteration in range(self.max_iterations):
            for particle in self.particles:
                distance = self.calculate_tour_distance(particle['position'])

                # Update personal best
                if distance < particle['best_distance']:
                    particle['best_distance'] = distance
                    particle['best_position'] = particle['position'].copy()

                # Update global best
                if distance < self.best_global_distance:
                    self.best_global_distance = distance
                    self.best_global_position = particle['position'].copy()

                # Update velocity and position
                for i in range(len(particle['position'])):
                    inertia = particle['velocity'][i]
                    cognitive = random.uniform(0, 1) * (particle['best_position'][i] - particle['position'][i])
                    social = random.uniform(0, 1) * (self.best_global_position[i] - particle['position'][i])
                    particle['velocity'][i] = inertia + cognitive + social

                    # Update position and ensure it's a valid city index
                    new_index = int(particle['position'][i] + particle['velocity'][i])
                    new_index = max(0, min(new_index, len(self.cities) - 1))  # Keep within bounds
                    particle['position'][i] = new_index  # Ensure indices are within the valid range

                # Ensure position represents a valid tour (permutation)
                particle['position'] = list(set(particle['position']))[:len(self.cities)]
                while len(particle['position']) < len(self.cities):
                    # Add random cities to ensure complete tour
                    random_city = random.choice([x for x in range(len(self.cities)) if x not in particle['position']])
                    particle['position'].append(random_city)

            print(f"Iteration {iteration + 1}/{self.max_iterations}, Best Distance: {self.best_global_distance:.2f}")

        # Once complete, display the best tour found by PSO
        self.tour = self.best_global_position
        self.display_current_tour()
        print(f"PSO Optimization complete. Final distance: {self.best_global_distance:.2f}")


if __name__ == "__main__":
    UI()
