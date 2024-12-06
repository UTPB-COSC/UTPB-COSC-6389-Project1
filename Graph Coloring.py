# Imported packages
import math
import random
import tkinter as tk
import threading

# Graph coloring parameters
NUM_NODES = 30  # Total number of nodes to generate
NUM_COLORS = 3  # Initial number of colors to use for the nodes
EDGE_PROB = 0.03  # Probability of a node having an additional edge

# User interface parameters
SCREEN_PADDING = 75  # Padding around the canvas
RADIUS = 2.25  # Size of the circular layout
NODE_SIZE = 10  # Size of the nodes
MIN_CONTRAST = 150  # Minimum level of contrast between colors
EDGE_WIDTH = 2  # Width of edges when drawn

# Running genetic algorithm parameters
NUM_GENERATIONS = 1000  # Maximum number of generations in the genetic algorithm, including gen 0
POP_SIZE = 50  # Population size in the genetic algorithm
SLEEP_TIME = 0.01  # Time between generations in seconds

# Parent selection parameters
ELITISM_COUNT = 10  # Number of top individuals to keep for the next generation
TOURNAMENT_SIZE = 3  # Number of participants in tournament selection

# Mutation parameters
MUTATION_POINTS = 2  # Number of points to mutate per genome during n-point mutation
BASE_MUTATION_RATE = 0.001  # Probability of mutation without stagnation
FINAL_MUTATION_RATE = 0.999  # Probability of mutation with maximum stagnation
MAX_STAGNATION = 75  # How long it takes to reach peak mutation and reset the population with an extra color


# Generates a random RGB color for the nodes
def random_rgb_color(existing_colors, contrast=MIN_CONTRAST):
    while True:
        # Generates a random color in RGB format
        new_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Checks that the new color is sufficiently different from all existing colors
        if all(color_distance(new_color, hex_to_rgb(existing)) >= contrast for existing in existing_colors):
            # Converts the RGB tuple back to a hex color string
            hex_color = '#{:02x}{:02x}{:02x}'.format(new_color[0], new_color[1], new_color[2])

            return hex_color

# Converts a hex color string to an RGB tuple
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')

    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Calculates the distance between two colors in RGB space
def color_distance(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2 = color2

    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


# Class to represent a node
class Node:
    # Initialization of node with coordinates
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.force_x = 0
        self.force_y = 0

    # Draws the node on the given canvas
    def draw(self, canvas, color='black'):
        canvas.create_oval(self.x - NODE_SIZE,
                           self.y - NODE_SIZE,
                           self.x + NODE_SIZE,
                           self.y + NODE_SIZE,
                           fill=color)


# Class to represent edges, lines drawn between nodes
class Edge:
    # Initialization of edges between nodes
    def __init__(self, a, b):
        self.node_a = a
        self.node_b = b

    # Draws the edge using the given parameters
    def draw(self, canvas, color='grey'):
        canvas.create_line(self.node_a.x,
                           self.node_a.y,
                           self.node_b.x,
                           self.node_b.y,
                           fill=color,
                           width=EDGE_WIDTH)


# Class for the user interface of the graph coloring problem
class UI(tk.Tk):
    # Initialization of the user interface
    def __init__(self):
        tk.Tk.__init__(self)

        # Creates empty lists and a default value
        self.nodes_list = []  # List to hold nodes
        self.neighbors_list = []  # List to hold neighbors (matched pairings of nodes)
        self.edges_list = []  # List to hold edges (lines between nodes)
        self.running = False  # Whether the algorithm is currently running

        # Window properties
        self.title("Graph Coloring")  # Window title
        self.option_add("*tearOff", False)  # Fake full screen
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()  # Gets dimensions
        self.geometry("%dx%d+0+0" % (self.width, self.height))  # Sets dimensions
        self.state("zoomed")  # Zooms in

        # Canvas for drawing the graph coloring problem
        self.canvas = tk.Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)

        # Canvas boundaries
        self.canvas_width = self.width - SCREEN_PADDING
        self.canvas_height = self.height - SCREEN_PADDING * 2

        # Menu bar setup for interacting with the graph coloring problem
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        menu_gc = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_gc, label='Menu', underline=0)

        # Adds menu commands for graph coloring actions
        menu_gc.add_command(label="New Instance", command=self.new, underline=0)
        menu_gc.add_command(label="Run Instance", command=self.start_thread, underline=0)
        menu_gc.add_command(label="Stop Instance", command=self.stop_thread, underline=0)

        # Starts the UI loop
        self.mainloop()

    # Resets the UI and starts a new instance of the graph coloring problem
    def new(self):
        # Cancels any currently running thread
        if self.running:
            self.running = False

        # Sets up the new thread
        self.generate_map()
        self.draw_map()
        self.start_thread()

    # Starts a new thread to run the genetic algorithm
    def start_thread(self):
        if not self.running:  # Prevents a duplicate instance
            # Sets up the new thread
            self.clear_canvas()
            self.running = True
            thread = threading.Thread(target=self.run_ga)
            thread.start()

    # Stops the current running instance of the algorithm
    def stop_thread(self):
        self.running = False
        print("Algorithm halted!")
        print()

    # Clears the canvas (removes all nodes and edges)
    def clear_canvas(self):
        self.canvas.delete("all")

    # Combines list of nodes and their neighbors to form a map
    def generate_map(self):
        if self.running:  # Prevents a duplicate instance
            self.running = False

        # Resets everything
        self.clear_canvas()
        self.nodes_list = []
        self.neighbors_list = []
        self.edges_list = []

        # Calculates the center of the canvas
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2

        # Sets the radius for the circular layout
        radius = min(self.canvas_width, self.canvas_height) / RADIUS

        # Adds nodes to the map in a circular layout
        for n in range(NUM_NODES):
            # Calculates the angle for each node
            angle = 2 * math.pi * n / NUM_NODES
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # Creates and adds a node at the calculated position
            node = Node(x, y)
            self.nodes_list.append(node)

        # Ensures each node has at least one edge and then adds additional edges with probability
        for i in range(NUM_NODES):
            self.add_neighbor(i)

    # Creates neighboring nodes ensuring each node has at least one edge
    def add_neighbor(self, a):
        # Random node to connect to
        b = random.randint(0, len(self.nodes_list) - 1)

        # Ensures we do not connect a node to itself
        while a == b:
            b = random.randint(0, len(self.nodes_list) - 1)

        # Adds the edge if it doesn't already exist
        neighbors = f'{min(a, b)},{max(a, b)}'
        if neighbors not in self.neighbors_list:
            edge = Edge(self.nodes_list[a], self.nodes_list[b])
            self.neighbors_list.append(neighbors)
            self.edges_list.append(edge)

        # Adds additional edges based on probability
        for j in range(len(self.nodes_list)):
            if a != j:
                if random.random() < EDGE_PROB:
                    neighbors = f'{min(a, j)},{max(a, j)}'
                    if neighbors not in self.neighbors_list:  # Ensures that we don't add duplicate edges
                        edge = Edge(self.nodes_list[a], self.nodes_list[j])
                        self.neighbors_list.append(neighbors)
                        self.edges_list.append(edge)

    # Draws the graph on the canvas
    def draw_map(self):
        # Draws all nodes
        for node in self.nodes_list:
            node.draw(self.canvas)

        # Draws all edges
        for edge in self.edges_list:
            edge.draw(self.canvas)

        # Displays the number of edges for the instance
        self.canvas.create_text(200, 25, text=f"Number of nodes: {len(self.nodes_list)}", font="Arial 14",
                                    fill="black")

        # Displays the number of edges for the instance
        self.canvas.create_text(200, 50, text=f"Number of edges: {len(self.edges_list)}", font="Arial 14", fill="black")

# Draws a visual representation of the current genome
    def draw_genome(self, genome, current_fitness, best_fitness, gen_num, mutation_rate, stag_count, num_colors):
        # Draws all edges
        for e in self.edges_list:
            e.draw(self.canvas)

        # Holds the randomized color for each node
        color_palette = []
        for _ in range(num_colors):
            color_palette.append(random_rgb_color(existing_colors=color_palette))

        # Determines the color of every node based on the genome
        for i in range(len(self.nodes_list)):
            color = color_palette[genome[i]]  # Gets the color based on the genome value for each node
            self.nodes_list[i].draw(self.canvas, color)  # Applies the color to the node

        # Displays the number of conflicts between neighbors
        self.canvas.create_text(self.canvas_width - 200, 25,
                                text=f"Conflicts remaining: {current_fitness} ({best_fitness})",
                                font="Arial 14", fill="black")

        # Displays the current generation number
        self.canvas.create_text(self.canvas_width - 200, 50,
                                text=f"Generation: {gen_num}/{NUM_GENERATIONS - 1}", font="Arial 14", fill="black")

        # Displays the current mutation rate
        self.canvas.create_text(self.canvas_width - 200, 75,
                                text=f'Mutation Rate: {mutation_rate:.3f}', font="Arial 14", fill="black")

        # Displays the current stagnation counter
        self.canvas.create_text(self.canvas_width - 200, 100,
                                text=f'Stagnation Count: {stag_count}/{MAX_STAGNATION}', font="Arial 14", fill="black")

        # Displays the current number of colors used for the nodes
        self.canvas.create_text(200, 75, text=f"Number of colors: {num_colors}", font="Arial 14", fill="black")

    # Runs the genetic algorithm
    def run_ga(self):
        # Generates a new population
        def get_population(num_colors):
            population = []

            # Builds a genome based on color of cities
            for _ in range(POP_SIZE):
                genome = [random.randint(0, num_colors - 1) for _ in range(NUM_NODES)]
                population.append(genome)

            return population

        # Helper function to calculate the number of coloring conflicts between neighbors
        def count_conflicts(color):
            conflicts = 0

            # Checks whether neighbors have the same color
            for neighbors in self.neighbors_list:
                n1, n2 = map(int, neighbors.split(','))
                if color[n1] == color[n2]:
                    conflicts += 1

            return conflicts

        # Selects a subset of genomes and returns the best one
        def tournament_selection(last_pop, fitnesses):
            tournament_indices = random.sample(list(enumerate(fitnesses)), TOURNAMENT_SIZE)
            best_index = min(tournament_indices, key=lambda x: x[1])[0]

            return last_pop[best_index]

        # Selects two best candidates from the tournament to be parents
        def select_parents(last_pop, fitnesses):
            parent1 = tournament_selection(last_pop, fitnesses)
            parent2 = tournament_selection(last_pop, fitnesses)

            # Ensures distinct parents
            while parent1 == parent2:
                parent2 = tournament_selection(last_pop, fitnesses)

            return parent1, parent2

        # Performs uniform crossover between the parent genomes
        def uniform_crossover(parent1, parent2, num_colors):
            # Initializes the child with -1 (indicating unfilled genes)
            child = [-1] * len(parent1)

            # Randomly chooses from parent1 or parent2
            for i in range(len(parent1)):
                if random.random() < 0.5:
                    child[i] = parent1[i]
                else:
                    child[i] = parent2[i]

            # Checks for conflicts and resolves them by reassigning a valid color
            for i in range(len(child)):
                for neighbors in self.neighbors_list:
                    n1, n2 = map(int, neighbors.split(','))
                    if n1 == i:
                        neighbor = n2
                    elif n2 == i:
                        neighbor = n1
                    else:
                        continue

                    # Fixes conflict if the child has the same color as a neighbor
                    if child[i] == child[neighbor]:
                        # Finds a color that doesn't conflict with the neighbor's color
                        available_colors = set(range(num_colors)) - {child[neighbor]}
                        child[i] = random.choice(list(available_colors))

            return child

        # Increases mutation rate gradually as stagnation count grows
        def adjust_mutation_rate(stag_count):
            mutation_rate = BASE_MUTATION_RATE + ((FINAL_MUTATION_RATE - BASE_MUTATION_RATE) *
                                                  min(1.0, stag_count / MAX_STAGNATION))
            if BASE_MUTATION_RATE < FINAL_MUTATION_RATE:
                return max(mutation_rate, BASE_MUTATION_RATE)
            else:
                return max(mutation_rate, FINAL_MUTATION_RATE)

        # Performs n-point mutation of the child genome
        def n_point_mutation(genome, num_colors):
            for _ in range(MUTATION_POINTS):
                point = random.randint(0, len(genome) - 1)
                current_color = genome[point]
                new_color = random.randint(0, num_colors - 1)

                # Ensures the new color is not the same as the current one
                while new_color == current_color:
                    new_color = random.randint(0, num_colors - 1)

                # Checking if the new color causes a conflict with any neighbors
                valid_color = True
                for neighbor_pair in self.neighbors_list:
                    neighbor_nodes = list(map(int, neighbor_pair.split(',')))
                    # Chooses a different color from the neighbor for the node
                    if point in neighbor_nodes:
                        neighbor = neighbor_nodes[0] if neighbor_nodes[1] == point else neighbor_nodes[1]
                        # Checks again to ensure neighbors are not the same color
                        if genome[neighbor] == new_color:
                            valid_color = False
                            break

                # Applies the new color only if it's valid
                if valid_color:
                    genome[point] = new_color

            return genome

        # Runs a generation step of the algorithm
        def generation_step(generation=0, pop=None, last_best_fitness=None, stag_count=0, num_colors=NUM_COLORS):
            # Recalculates mutation rate based on stagnation
            mutation_rate = adjust_mutation_rate(stag_count)

            # Stops after reaching max number of generations or if the algorithm is halted
            if generation >= NUM_GENERATIONS or not self.running:
                return

            # Initializes population if not provided
            if pop is None:
                pop = get_population(num_colors)

            # Resets the population if stagnation exceeds the limit
            if stag_count == MAX_STAGNATION:
                print(f"Stagnation threshold reached ({MAX_STAGNATION} generations without improvement). "
                        f"Resetting population.")
                stag_count = 0
                pop = get_population(num_colors)
                last_best_fitness = None
                num_colors += 1

            # Fitness calculations
            fitnesses = [(genome, count_conflicts(genome)) for genome in pop]
            fitnesses.sort(key=lambda x: x[1])
            best_of_gen = fitnesses[0][0]
            current_fitness = count_conflicts(best_of_gen)

            # Updates best fitness, if applicable
            if last_best_fitness is None or current_fitness < last_best_fitness:
                best_fitness = current_fitness
            else:
                best_fitness = last_best_fitness

            # Checks for stagnation (no improvement in fitness)
            if last_best_fitness is not None and best_fitness == last_best_fitness:
                stag_count += 1
            elif best_fitness != 0:
                stag_count = 0  # Resets stagnation count if fitness improved



            # Creates a new population, starting with elites
            new_pop = []
            elites = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i])[:ELITISM_COUNT]
            for e in elites:
                new_pop.append(pop[e])

            # Fills the rest with new individuals using crossover and mutation
            while len(new_pop) < POP_SIZE:
                parent1, parent2 = select_parents([genome for genome, _ in fitnesses],
                                                  [fitness for _, fitness in fitnesses])
                child = uniform_crossover(parent1, parent2, num_colors)
                if random.random() < mutation_rate:
                    child = n_point_mutation(child, num_colors)
                new_pop.append(child)

            # Updates UI with current data
            self.after(0, self.clear_canvas)  # noqa: specific-warning-code
            self.after(0, self.draw_map)  # noqa: specific-warning-code
            self.after(0, self.draw_genome,best_of_gen, current_fitness, best_fitness, generation,
                       mutation_rate, stag_count, num_colors)

            # Stops if the optimal solution is found or after a certain number of generations
            if current_fitness == 0 or generation == NUM_GENERATIONS:
                self.running = False
                print(f"Algorithm completed at generation {generation}.")
                print(f'Best genome: {best_of_gen}')
                return
            # Prints statistics until the generation limit is reached
            else:
                print(f'Number of conflicts in generation {generation}: {current_fitness}')
                print(f'Mutation rate: {mutation_rate}')
                print(f'Stagnation count: {stag_count}')
                print(f'Best genome: {best_of_gen}')
                print()

            # Schedules the next generation step
            if self.running and current_fitness != 0:
                self.after(int(SLEEP_TIME * 1000), generation_step,
                           generation + 1, new_pop, best_fitness, stag_count, num_colors)

        # Starts the evolutionary process
        generation_step()


# Catches the main thread and instantiates the window class
if __name__ == '__main__':
    UI()
