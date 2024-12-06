# Imported packages
import math
import random
import tkinter as tk
import threading

# User interface parameters
NUM_CITIES = 25  # Total number of cities to generate
SCREEN_PADDING = 125  # Padding around the canvas
CITY_SCALE = 5  # Scaling of city dimensions
ROAD_WIDTH = 4  # Width of roads when drawn

# Running genetic algorithm parameters
NUM_GENERATIONS = 1000  # Maximum number of generations in the genetic algorithm, including gen 0
POP_SIZE = 100  # Population size in the genetic algorithm
SLEEP_TIME = 0.01  # Time between generations in seconds

# Parent selection parameters
ELITISM_COUNT = 10  # Number of top individuals to keep for the next generation
TOURNAMENT_SIZE = 5  # Number of participants in tournament selection
CROSS_STAGNATION = 50  # How long before switching over to new crossover/ mutation methods

# Mutation parameters
MUTATION_POINTS = 2  # Number of points to mutate per genome during swap mutation
BASE_MUTATION_RATE = 0.05  # Probability of mutation without stagnation
FINAL_MUTATION_RATE = 0.99  # Probability of mutation with maximum stagnation
MUT_STAGNATION = 100  # How long it takes to reach the maximum mutation rate

# Running ant colony optimization parameters
NUM_ITERATIONS = 1000  # Number of iterations for ACO
ANT_COUNT = 50  # Number of ants
ALPHA = 1  # Influence of pheromones on decisions
BETA = 2  # Influence of visibility range on decisions
RHO = 0.5  # Pheromone evaporation rate
Q = 100  # Pheromone deposit amount


# Class to represent a city
class Node:
    # Initialization of city with coordinates
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Draws the city on the given canvas
    def draw(self, canvas, color='black'):
        canvas.create_oval(self.x - CITY_SCALE,
                           self.y - CITY_SCALE,
                           self.x + CITY_SCALE,
                           self.y + CITY_SCALE,
                           fill=color)


# Class to represent edges, lines drawn between pairs of cities
class Edge:
    # Initialization of edges and their distances between cities
    def __init__(self, a, b):
        self.city_a = a
        self.city_b = b
        self.length = math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    # Draws the edge using the given parameters
    def draw(self, canvas, color='grey', style=(2, 4)):
        canvas.create_line(self.city_a.x,
                           self.city_a.y,
                           self.city_b.x,
                           self.city_b.y,
                           fill=color,
                           width=ROAD_WIDTH,
                           dash=style)


# Class for the user interface of the TS problem
class UI(tk.Tk):
    # Initialization of the user interface
    def __init__(self):
        tk.Tk.__init__(self)

        # Creates empty lists
        self.cities_list = []  # List to hold cities
        self.roads_list = []  # List to hold roads (matched pairings of cities)
        self.edges_list = []  # List to hold edges (lines between cities)

        # Default status of the running algorithm
        self.running = False  # Whether the algorithm is currently running
        self.ga = None  # Whether "Genetic Algorithm" is selected
        self.aco = None  # Whether "Ant Colony Optimization" is selected

        # Window properties
        self.title("Traveling Salesman")  # Window title
        self.option_add("*tearOff", False)  # Fake full screen
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()  # Gets dimensions
        self.geometry("%dx%d+0+0" % (self.width, self.height))  # Sets dimensions
        self.state("zoomed")  # Zooms in

        # Canvas for drawing the TS problem
        self.canvas = tk.Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)

        # Canvas boundaries
        self.canvas_width = self.width - SCREEN_PADDING
        self.canvas_height = self.height - SCREEN_PADDING * 2

        # Menu bar setup for interacting with the TS
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        menu_ts = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_ts, label='Menu', underline=0)

        # Adds menu commands for TS actions
        menu_ts.add_command(label="New Instance", command=self.new, underline=0)
        menu_ts.add_command(label="Run Genetic Algorithm", command=self.start_ga_thread, underline=0)
        menu_ts.add_command(label="Run Ant Colony Optimization", command=self.start_aco_thread, underline=0)
        menu_ts.add_command(label="Stop Instance", command=self.stop_thread, underline=0)

        # Starts the UI loop
        self.mainloop()

    # Resets the UI and starts a new instance of the TS problem
    def new(self):
        # Cancels any currently running thread and retries creating a new one
        if self.running:
            self.running = False
            self.after(25, self.new)  # noqa: specific-warning-code

        # Sets up the new thread
        self.generate_map()
        self.draw_map()

    # Starts a new thread to run the genetic algorithm
    def start_ga_thread(self):
        if not self.running:  # Prevents a duplicate instance
            # Sets up the new thread
            self.clear_canvas()
            self.running = True
            self.ga = True  # Turns on the GA display
            self.aco = False  # Turns off the ACO display
            thread = threading.Thread(target=self.run_ga)
            thread.start()

    # Starts a new thread to run ant colony optimization
    def start_aco_thread(self):
        if not self.running:  # Prevents a duplicate instance
            # Sets up the new thread
            self.clear_canvas()
            self.running = True
            self.aco = True  # Turns on the ACO display
            self.ga = False  # Turns off the GA display
            thread = threading.Thread(target=self.run_aco)
            thread.start()

    # Stops the current running instance of the algorithm
    def stop_thread(self):
        self.running = False
        print("Algorithm halted!")
        print()

    # Clears the canvas (removes all cities and edges)
    def clear_canvas(self):
        self.canvas.delete("all")

    # Combines list of cities and roads to form a map
    def generate_map(self):
        if self.running:  # Prevents a duplicate instance
            self.running = False

        # Resets everything
        self.clear_canvas()
        self.cities_list = []
        self.roads_list = []
        self.edges_list = []

        # Adds cities to the map
        for c in range(NUM_CITIES):
            self.add_city()

        # Creates roads for all pairs of cities
        for i in range(len(self.cities_list)):
            for j in range(i + 1, len(self.cities_list)):
                self.add_road()

    # Adds a new city to the map
    def add_city(self):
        # Random coordinates
        x = random.randint(SCREEN_PADDING, self.canvas_width)
        y = random.randint(SCREEN_PADDING, self.canvas_height)

        # Places node at the coordinates
        node = Node(x, y)
        self.cities_list.append(node)

    # Adds a new road to the map
    def add_road(self):
        # Random city ends
        a = random.randint(0, len(self.cities_list) - 1)
        b = random.randint(0, len(self.cities_list) - 1)
        road = f'{min(a, b)},{max(a, b)}'

        # Ensures new roads connect between different cities
        while a == b or road in self.roads_list:
            a = random.randint(0, len(self.cities_list) - 1)
            b = random.randint(0, len(self.cities_list) - 1)
            road = f'{min(a, b)},{max(a, b)}'

        # Places edge between the road's cities
        edge = Edge(self.cities_list[a], self.cities_list[b])
        self.roads_list.append(road)
        self.edges_list.append(edge)

    # Draws all edges and cities on the map
    def draw_map(self):
        for e in self.edges_list:
            e.draw(self.canvas)
        for c in self.cities_list:
            c.draw(self.canvas)

    # Draws a visual representation of the current genome
    def draw_genome(self, genome, distance, gen_num, mutation_rate, stag_count):
        # Draws all edges
        for e in self.edges_list:
            e.draw(self.canvas)

        # Highlights the path of the genome (red)
        for i in range(len(genome) - 1):
            city1 = self.cities_list[genome[i]]
            city2 = self.cities_list[genome[i + 1]]
            self.canvas.create_line(city1.x, city1.y, city2.x, city2.y, fill='red', width=2)

        # Highlights the edge from the last city back to the first city
        city1 = self.cities_list[genome[-1]]
        city2 = self.cities_list[genome[0]]
        self.canvas.create_line(city1.x, city1.y, city2.x, city2.y, fill='red', width=2)

        # Changes the color of cities to red
        for city in self.cities_list:
            city.draw(self.canvas, 'red')

        # Displays the distance of the current best route
        self.canvas.create_text(100, 25,
                                text=f"Distance: {distance:.2f}", font="Arial 14", fill="black")

        # Checks whether the running thread is GA before showing statistics
        if self.ga:
            # Displays current generation number of the GA
            self.canvas.create_text(100, 50,
                                    text=f"Generation: {gen_num}/{NUM_GENERATIONS - 1}", font="Arial 14", fill="black")

            # Displays current mutation rate of the GA
            self.canvas.create_text(100, 75,
                                    text=f"Mutation Rate: {mutation_rate:.3f}", font="Arial 14", fill="black")

            # Displays current stagnation counter of the GA
            self.canvas.create_text(100, 100,
                                    text=f"Stagnation Count: {stag_count}", font="Arial 14", fill="black")

        # Checks whether the running thread is ACO before showing statistics
        if self.aco:
            # Displays current generation number based on ACO iterations
            self.canvas.create_text(100, 50,
                                    text=f"Generation: {gen_num}/{NUM_ITERATIONS - 1}", font="Arial 14", fill="black")

    # Runs the genetic algorithm
    def run_ga(self):
        # Generates a new population
        def get_population():
            population = []

            # Builds a genome based on list order of cities
            for _ in range(POP_SIZE):
                genome = list(range(len(self.cities_list)))
                random.shuffle(genome)  # Randomizes city list order
                genome.append(genome[0])  # Returns to start to create a cyclical route
                population.append(genome)

            return population

        # Helper function to calculate the total distance of the tour
        def calculate_distance(genome):
            total_distance = 0

            # Finds the sum of distances between all pairs of cities
            for i in range(len(genome) - 1):
                city1 = self.cities_list[genome[i]]
                city2 = self.cities_list[genome[i + 1]]
                total_distance += math.sqrt((city1.x - city2.x) ** 2 + (city1.y - city2.y) ** 2)

            return total_distance

        # Selects a subset of genomes and returns the best one
        def tournament_selection(last_pop, distances):
            tournament_indices = random.sample(range(len(last_pop)), TOURNAMENT_SIZE)
            best_index = min(tournament_indices, key=lambda i: distances[i])

            return last_pop[best_index]

        # Selects two best candidates from the tournament to be parents
        def select_parents(last_pop, distances):
            parent1 = tournament_selection(last_pop, distances)
            parent2 = tournament_selection(last_pop, distances)

            # Ensures distinct parents
            while parent1 == parent2:
                parent2 = tournament_selection(last_pop, distances)

            return parent1, parent2

        # Performs order crossover between parent genomes for exploring in early generations
        def order_crossover(parent1, parent2):
            # Selects two random indices to form a subsequence
            start, end = sorted(random.sample(range(len(parent1)), 2))

            # Copies the subsequence from parent1 to the child
            child = [-1] * len(parent1)
            child[start:end + 1] = parent1[start:end + 1]
            current_position = end + 1

            # Fills the rest of the child genome with parent2
            for gene in parent2:
                if gene not in child:
                    if current_position >= len(child):
                        current_position = 0
                    child[current_position] = gene
                    current_position += 1

            return child

        # Performs partially mapped crossover between parent genomes for fine-tuning solutions near convergence
        def partially_mapped_crossover(parent1, parent2):
            # Selects two random crossover points
            start, end = sorted(random.sample(range(1, len(parent1) - 1), 2))

            # Creates the child by copying the segment from parent1
            child = [-1] * len(parent1)
            child[start:end + 1] = parent1[start:end + 1]

            # Creates a mapping to maintain the order of cities
            mapping = {}
            for i in range(start, end + 1):
                mapping[parent1[i]] = parent2[i]

            # Fills the rest of the child with cities from parent2
            current_position = 0
            for gene in parent2:
                # Skips if the gene is already in the child's segment
                if gene in child:
                    continue
                # Maps the gene using the mapping if it exists, directly adds it otherwise
                while start <= current_position <= end:
                    current_position += 1
                # Moves down the rest of the genome
                child[current_position] = gene
                current_position += 1

            return child

        # Increases mutation rate gradually as stagnation count grows
        def adjust_mutation_rate(stag_count):
            mutation_rate = BASE_MUTATION_RATE + ((FINAL_MUTATION_RATE - BASE_MUTATION_RATE) *
                                                  min(1.0, stag_count / MUT_STAGNATION))
            if BASE_MUTATION_RATE < FINAL_MUTATION_RATE:
                return max(mutation_rate, BASE_MUTATION_RATE)
            else:
                return max(mutation_rate, FINAL_MUTATION_RATE)

        # Performs swap mutation of child genome for exploring in early generations
        def swap_mutation(genome):
            num_genes_to_mutate = MUTATION_POINTS  # Number of swaps to perform
            for _ in range(num_genes_to_mutate):
                idx1, idx2 = random.sample(range(len(genome)), 2)  # Randomly selects mutating genes
                genome[idx1], genome[idx2] = genome[idx2], genome[idx1]

            return genome

        # Performs inversion mutation of child genome for fine-tuning solutions near convergence
        def inversion_mutation(genome):
            # Selects two random indices to define a subsequence to invert
            start, end = sorted(random.sample(range(1, len(genome) - 1), 2))
            genome[start:end + 1] = reversed(genome[start:end + 1])

            return genome

        # Runs a generation step of the algorithm
        def generation_step(generation=0, pop=None, last_best_distance=None, stag_count=0):
            # Recalculates mutation rate based on stagnation
            mutation_rate = adjust_mutation_rate(stag_count)

            # Stops after reaching max number of generations or if the algorithm is halted
            if generation >= NUM_GENERATIONS or not self.running:
                return

            # Initializes population if not provided
            if pop is None:
                pop = get_population()

            # Distance calculations
            distances = [calculate_distance(genome) for genome in pop]
            best_of_gen = min(pop, key=lambda genome: calculate_distance(genome))
            current_distance = calculate_distance(best_of_gen)

            # Checks for stagnation (no improvement in distance)
            if last_best_distance is not None and current_distance == last_best_distance:
                stag_count += 1
            elif current_distance != 0:
                stag_count = 0  # Resets stagnation count if distance improved

            # Creates a new population, starting with elites
            new_pop = []
            elites = sorted(range(len(distances)), key=lambda i: distances[i])[:ELITISM_COUNT]
            for e in elites:
                new_pop.append(pop[e])

            # Fills the rest with new individuals using crossover and mutation
            while len(new_pop) < POP_SIZE:
                parent1, parent2 = select_parents(pop, distances)

                # Uses crossover and mutation that favor exploration
                if stag_count < CROSS_STAGNATION:
                    child = order_crossover(parent1, parent2)
                    if random.random() < mutation_rate:
                        child = swap_mutation(child)
                # Uses crossover and mutation that favor exploitation
                else:
                    child = partially_mapped_crossover(parent1, parent2)
                    if random.random() < mutation_rate:
                        child = inversion_mutation(child)
                # Adds the child to the new population
                new_pop.append(child)

            # Updates UI with current data
            self.after(0, self.clear_canvas)  # noqa: specific-warning-code
            self.after(0, self.draw_map)  # noqa: specific-warning-code
            self.after(0, self.draw_genome,
                       best_of_gen, current_distance, generation, mutation_rate, stag_count)

            # Stops after a certain number of generations
            if generation == NUM_GENERATIONS:
                self.running = False
                print(f"Algorithm completed at generation {generation}.")
                return
            # Prints statistics until the generation limit is reached
            else:
                print(f'Best distance of generation {generation}: {current_distance}')
                print(f'Mutation rate: {mutation_rate}')
                print(f'Stagnation count: {stag_count}')
                print()

            # Schedules the next generation step
            if self.running:
                self.after(int(SLEEP_TIME * 1000),
                           generation_step,
                           generation + 1,
                           new_pop,
                           current_distance,
                           stag_count)

        # Starts the evolutionary process
        generation_step()

    # Runs ant colony optimization
    def run_aco(self):
        # Initializes pheromone matrix
        def get_pheromone_matrix():
            pheromone_matrix = [[1.0 for _ in range(len(self.cities_list))] for _ in range(len(self.cities_list))]
            return pheromone_matrix

        # Initializes visibility matrix
        def get_visibility_matrix():
            visibility_matrix = [[0.0 for _ in range(len(self.cities_list))] for _ in range(len(self.cities_list))]

            # Calculates the matrix (1/distance between cities)
            for i in range(len(self.cities_list)):
                for j in range(len(self.cities_list)):
                    if i != j:
                        visibility_matrix[i][j] = 1 / calculate_distance(self.cities_list[i], self.cities_list[j])

            return visibility_matrix

        # Calculates the distance between a pair of cities
        def calculate_distance(city1, city2):
            return math.sqrt((city1.x - city2.x) ** 2 + (city1.y - city2.y) ** 2)

        # Calculates the total distance of the tour for a given ant's path
        def calculate_tour_distance(ant):
            total_distance = 0

            # Finds the sum of all distances between cities in the ant's path
            for i in range(len(ant) - 1):
                city1 = self.cities_list[ant[i]]
                city2 = self.cities_list[ant[i + 1]]
                total_distance += calculate_distance(city1, city2)

            return total_distance

        # Determines the next path of the ant
        def select_next_city(ant, pheromone_matrix, visibility_matrix):
            current_city = ant[-1]  # Last city in the ant's path

            # For calculating the probabilities of visiting all unvisited cities
            unvisited_cities = [i for i in range(len(self.cities_list)) if i not in ant]
            probabilities = []
            total_pheromone = 0

            # Calculates total pheromones and probabilities
            for city in unvisited_cities:
                # Multiplies the matrices
                pheromone = pheromone_matrix[current_city][city]
                visibility = visibility_matrix[current_city][city]
                pheromone_visibility = pheromone * visibility

                # Increases total pheromones and adds to list probabilities
                total_pheromone += pheromone_visibility
                probabilities.append(pheromone_visibility)

            # Normalizes probabilities to ensure they sum to 1
            if total_pheromone > 0:
                probabilities = [prob / total_pheromone for prob in probabilities]
            else:
                # Chooses uniformly without pheromones
                probabilities = [1.0 / len(unvisited_cities)] * len(unvisited_cities)

            # Selects the next city based on the probabilities
            next_city = random.choices(unvisited_cities, probabilities)[0]

            return next_city

        # Changes ant path pheromones
        def update_pheromone_matrix(pheromone_matrix, ants, evaporation_rate):
            # Applies pheromone evaporation
            for i in range(len(pheromone_matrix)):
                for j in range(len(pheromone_matrix)):
                    pheromone_matrix[i][j] *= (1 - evaporation_rate)

            # Deposits pheromone based on ants' paths
            for ant in ants:
                path_distance = calculate_tour_distance(ant)
                pheromone_deposit = Q / path_distance
                for i in range(len(ant) - 1):
                    pheromone_matrix[ant[i]][ant[i + 1]] += pheromone_deposit
                pheromone_matrix[ant[-1]][ant[0]] += pheromone_deposit  # Closes the loop

        # Defines the ACO process and its iterations
        def ant_colony_optimization():
            # Default matrices and values
            pheromone_matrix = get_pheromone_matrix()
            visibility_matrix = get_visibility_matrix()
            best_path = None
            best_distance = float('inf')

            # Updates the UI with the current iteration and best distance
            def update_iteration(iteration, current_distance, current_path):
                self.after(0, self.clear_canvas)  # noqa: specific-warning-code
                self.after(0, self.draw_map)  # noqa: specific-warning-code
                self.after(0, self.draw_genome, current_path, current_distance, iteration, 0, 0)

            # Runs the ACO algorithm
            def run_iteration(iteration):
                nonlocal best_distance, best_path
                ants = []

                # Causes ants to visit every city
                for _ in range(ANT_COUNT):
                    ant = [random.randint(0, len(self.cities_list) - 1)]  # Random starting city
                    while len(ant) < len(self.cities_list):
                        next_city = select_next_city(ant, pheromone_matrix, visibility_matrix)
                        ant.append(next_city)
                    ants.append(ant)

                # Updates pheromone matrix based on the ants' paths
                update_pheromone_matrix(pheromone_matrix, ants, RHO)

                # Checks for improvement across iterations
                improved = False

                # Evaluates the best path
                for ant in ants:
                    path_distance = calculate_tour_distance(ant)
                    if path_distance < best_distance:
                        best_distance = path_distance
                        best_path = ant
                        improved = True

                # Prints iterations where distance improves
                if improved:
                    print(f"Best distance of iteration {iteration + 1}: {best_distance}")

                # Updates UI after each iteration
                update_iteration(iteration, best_distance, best_path)

                # Schedules next iteration
                if iteration < NUM_ITERATIONS - 1 and self.running == True:
                    self.after(int(SLEEP_TIME * 1000), run_iteration, iteration + 1)

            # Starts the first iteration
            run_iteration(0)

        # Starts the ACO process
        ant_colony_optimization()


# Catches the main thread and instantiates the window class
if __name__ == '__main__':
    UI()
