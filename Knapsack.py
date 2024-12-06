# Imported packages
import math
import random
import tkinter as tk
import threading

# Knapsack parameters
NUM_ITEMS = 100  # Total number of items to generate
FRAC_TARGET = 0.7  # Fraction of items to target for the knapsack
MIN_VALUE = 128  # Minimum value of an item
MAX_VALUE = 2048  # Maximum value of an item

# User interface parameters
SCREEN_PADDING = 25  # Padding around the canvas
ITEM_PADDING = 5  # Padding between items
STROKE_WIDTH = 5  # Width of item borders when drawn

# Running algorithm parameters
NUM_GENERATIONS = 1000  # Maximum number of generations in the genetic algorithm, including gen 0
POP_SIZE = 50  # Population size in the genetic algorithm
SLEEP_TIME = 0.01  # Time between generations in seconds

# Parent selection parameters
ELITISM_COUNT = 5  # Number of top individuals to keep for the next generation
TOURNAMENT_SIZE = 5  # Number of participants in tournament selection
CROSSOVER_POINTS = 3  # Number of points to use during n_point crossover
CROSS_STAGNATION = 10  # How long before switching over to new crossover/ mutation methods

# Mutation parameters
MUTATION_POINTS = 3  # Number of points to mutate per genome during swap mutation
BASE_MUTATION_RATE = 0.001  # Probability of mutation without stagnation
FINAL_MUTATION_RATE = 0.999  # Probability of mutation with maximum stagnation
MUT_STAGNATION = 50  # How long it takes to reach the maximum mutation rate

# Other parameters
SHARING_RADIUS = 0.75  # Distance threshold for similarity (genetic distance between genomes)
SHARING_PENALTY = 5  # Penalty for individuals that are too similar
FIT_STAGNATION = 10  # How often fitness sharing is applied
IMM_STAGNATION = 15  # How often immigration is applied
CROWD_STAGNATION = 30  # How often crowding selection is applied


# Generates a random RGB color for items
def random_rgb_color():
    red = random.randint(0x10, 0xff)
    green = random.randint(0x10, 0xff)
    blue = random.randint(0x10, 0xff)
    hex_color = '#{:02x}{:02x}{:02x}'.format(red, green, blue)

    return hex_color


# Class to represent an item that can go into the knapsack
class Item:
    # Initialization of item with random value and color
    def __init__(self):
        self.value = random.randint(MIN_VALUE, MAX_VALUE)
        self.color = random_rgb_color()

        # Default item position and dimensions
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    # Sets position and dimensions of item on the canvas
    def place(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    # Draws the item on the given canvas using the given parameters
    def draw(self, canvas, active=False):
        # Draws item value as text next to the item's rectangle
        canvas.create_text(self.x + self.w + ITEM_PADDING + STROKE_WIDTH * 2,
                           self.y + self.h / 2,
                           text=f'{self.value}')

        # Fills item's rectangle with color if active, otherwise leaves it blank
        fill_color = self.color if active else ''
        canvas.create_rectangle(self.x,
                                self.y,
                                self.x + self.w,
                                self.y + self.h,
                                fill=fill_color,
                                outline=self.color,
                                width=STROKE_WIDTH)


# Class for the user interface of the knapsack problem
class UI(tk.Tk):
    # Initialization of the user interface
    def __init__(self):
        tk.Tk.__init__(self)

        # Creates empty list and default values
        self.items_list = []  # List to hold items
        self.target = 0  # Target value for the knapsack
        self.running = False  # Whether the algorithm is currently running

        # Window properties
        self.title("Knapsack")  # Window title
        self.option_add("*tearOff", False)  # Fake full screen
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()  # Gets dimensions
        self.geometry("%dx%d+0+0" % (self.width, self.height))  # Sets dimensions
        self.state("zoomed")  # Zooms in

        # Canvas for drawing the knapsack problem
        self.canvas = tk.Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)

        # Menu bar setup for interacting with the knapsack
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        menu_k = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_k, label='Menu', underline=0)

        # Adds menu commands for knapsack actions
        menu_k.add_command(label="New Instance", command=self.new, underline=0)
        menu_k.add_command(label="Run Instance", command=self.start_thread, underline=0)
        menu_k.add_command(label="Stop Instance", command=self.stop_thread, underline=0)

        # Starts the UI loop
        self.mainloop()

    # Resets the UI and starts a new instance of the knapsack problem
    def new(self):
        # Cancels any currently running thread
        if self.running:
            self.running = False

        # Sets up the new thread
        self.generate_knapsack()
        self.set_target()
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

    # Clears the canvas (removes all items and drawings)
    def clear_canvas(self):
        self.canvas.delete("all")

    # Generates a new set of items for the knapsack
    def generate_knapsack(self):
        if self.running:  # Prevents a duplicate instance
            self.running = False

        # Resets everything
        self.clear_canvas()
        self.items_list = []

        # Generates a list of items
        while len(self.items_list) < NUM_ITEMS:
            item = self.get_rand_item()
            if item is not None:
                self.items_list.append(item)

        # For adjusting item value ratios
        item_max = max(item.value for item in self.items_list)

        # Item dimensions based on the screen size
        w = self.width - SCREEN_PADDING
        h = self.height - SCREEN_PADDING

        # Calculates row count and dimensions
        num_rows = math.ceil(NUM_ITEMS / 6)
        row_w = w / 8 - ITEM_PADDING
        row_h = (h - 200) / num_rows

        # Places items in a grid layout
        for x in range(0, 6):
            for y in range(0, num_rows):
                if x * num_rows + y >= NUM_ITEMS:
                    break
                item = self.items_list[x * num_rows + y]
                item_w = row_w / 2
                item_h = max(item.value / item_max * row_h, 1)
                item.place(SCREEN_PADDING + x * row_w + x * ITEM_PADDING,
                           SCREEN_PADDING + y * row_h + y * ITEM_PADDING,
                           item_w,
                           item_h)

        # Draws all items on the canvas
        self.draw_items()

    # Sets the target value for the knapsack problem
    def set_target(self):
        if self.running:  # Prevents a duplicate instance
            self.running = False

        # Resets everything
        self.clear_canvas()
        target_set = []

        # Selects a random subset of items to target
        for x in range(int(NUM_ITEMS * FRAC_TARGET)):
            item = self.items_list[random.randint(0, len(self.items_list) - 1)]
            while item in target_set:  # Ensures unique selection
                item = self.items_list[random.randint(0, len(self.items_list) - 1)]
            target_set.append(item)

        # Calculates total target value
        total = sum(item.value for item in target_set)
        self.target = total
        self.draw_target()

    # Randomly generates a new item
    def get_rand_item(self):
        i1 = Item()

        # Ensures each item has a unique value
        for i2 in self.items_list:
            if i1.value == i2.value:
                return None

        return i1

    # Draws every item on the canvas
    def draw_items(self):
        for item in self.items_list:
            item.draw(self.canvas)

    # Draws a rectangle representing the target value size
    def draw_target(self):
        # Position and dimensions
        x = (self.width - SCREEN_PADDING) / 8 * 7
        y = SCREEN_PADDING
        w = (self.width - SCREEN_PADDING) / 8 - SCREEN_PADDING
        h = self.height / 2 - SCREEN_PADDING

        # Draws the target value as a rectangle with a fixed size
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='black')
        self.canvas.create_text(x + w // 2,
                                y + h + SCREEN_PADDING,
                                text=f'{self.target}',
                                font=('Arial', 18))

    # Draws a rectangle representing the current sum of selected items
    def draw_sum(self, item_sum, target):
        # Position and dimensions
        x = (self.width - SCREEN_PADDING) / 8 * 6
        y = SCREEN_PADDING
        w = (self.width - SCREEN_PADDING) / 8 - SCREEN_PADDING
        h = self.height / 2 - SCREEN_PADDING
        h *= item_sum / target

        # Draws the current sum as a rectangle with a dynamically changing size
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='red')
        self.canvas.create_text(x + w // 2,
                                y + h + SCREEN_PADDING,
                                text=f'{item_sum}'
                                     f'({"+" if item_sum > target else "-"}{abs(item_sum - target)})',
                                font=('Arial', 18))

    # Draws a visual representation of the current genome
    def draw_genome(self, genome, gen_num, mutation_rate, stag_count):
        # Draws all items
        for i in range(NUM_ITEMS):
            item = self.items_list[i]
            item.draw(self.canvas, genome[i])  # Highlights active items in the genome

        # Position and dimensions
        x = (self.width - SCREEN_PADDING) / 8 * 6
        y = SCREEN_PADDING
        w = (self.width - SCREEN_PADDING) / 8 - SCREEN_PADDING
        h = self.height / 4 * 2.5

        # Displays the current generation number
        self.canvas.create_text(x + w,
                                y + h + SCREEN_PADDING * 2,
                                text=f'Generation: {gen_num}/{NUM_GENERATIONS - 1}',
                                font=('Arial', 18))

        # Displays the current mutation rate
        self.canvas.create_text(x + w,
                                y + h + SCREEN_PADDING * 4,
                                text=f'Mutation Rate: {mutation_rate:.3f}',
                                font=('Arial', 18))

        # Displays the current stagnation counter
        self.canvas.create_text(x + w,
                                y + h + SCREEN_PADDING * 6,
                                text=f'Stagnation Count: {stag_count}',
                                font=('Arial', 18))

    # Runs the genetic algorithm
    def run_ga(self):
        # Generates a new population
        def get_population(last_pop=None, fitnesses=None):
            population = []
            existing_genomes = set()  # Set to check for duplicate genomes

            # Preserves the elites from the previous generation
            if last_pop and fitnesses:
                elites = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i])[:ELITISM_COUNT]
                for e in elites:
                    genome_tuple = tuple(last_pop[e])
                    if genome_tuple not in existing_genomes:
                        population.append(last_pop[e])
                        existing_genomes.add(genome_tuple)

            # Fills the remaining population with new genomes
            while len(population) < POP_SIZE:
                genome = [random.choice([0, 1]) for _ in range(NUM_ITEMS)]
                genome_tuple = tuple(genome)
                if genome_tuple not in existing_genomes:
                    population.append(genome)
                    existing_genomes.add(genome_tuple)

            return population

        # Helper function to calculate the sum of item values for a genome
        def calculate_gene_sum(genome):
            return sum(self.items_list[i].value for i in range(len(genome)) if genome[i])

        # Calculates the fitness based on the absolute difference from the target
        def calculate_fitness(genome):
            total_value = calculate_gene_sum(genome)
            return abs(total_value - self.target)

        # Helper function to calculate Hamming distance (similarity) between two genomes
        def hamming_distance(genome1, genome2):
            return sum(1 for a, b in zip(genome1, genome2) if a != b)

        # Applies fitness sharing to penalize similar individuals
        def apply_fitness_sharing(pop, fitnesses):
            adjusted_fitnesses = []

            # Creates adjusted fitness values for all genomes in the population
            for i, genome in enumerate(pop):
                penalty = 1
                # Calculates the sharing penalty for this genome
                for j, other_genome in enumerate(pop):
                    if i != j:
                        distance = hamming_distance(genome, other_genome)
                        if distance < SHARING_RADIUS:
                            # Applies sharing penalty based on the similarity of genomes
                            penalty += SHARING_PENALTY * (1 - distance / SHARING_RADIUS)
                # Adjusts fitness by dividing by the sharing penalty
                adjusted_fitness = fitnesses[i] / penalty
                adjusted_fitnesses.append(adjusted_fitness)

            return adjusted_fitnesses

        # Adds strong immigrants to the current population when stagnation is detected
        def add_immigrants(num_immigrants, pop, fitnesses):
            worst_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:num_immigrants]
            best_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i])[:5]

            # Picks a random best individual for mutation to base an immigrant on
            for idx in worst_indices:
                parent = random.choice(best_indices)
                child = swap_mutation(pop[parent])
                pop[idx] = child

            return pop

        # Replaces similar genomes with offspring when stagnation is detected
        def crowding_selection(pop, fitnesses, offspring):
            for i, offspring_genome in enumerate(offspring):
                # Finds a similar individual in the population to compete with
                most_similar_index = -1
                most_similar_distance = float('inf')

                # Calculates the Hamming distance between the offspring and each individual
                for j, genome in enumerate(pop):
                    distance = hamming_distance(offspring_genome, genome)
                    if distance < most_similar_distance:
                        most_similar_distance = distance
                        most_similar_index = j

                # If the offspring is better than the most similar individual, replaces it
                if fitnesses[most_similar_index] > fitnesses[i]:
                    pop[most_similar_index] = offspring_genome

            return pop

        # Selects a subset of genomes and returns the best one
        def tournament_selection(last_pop, fitnesses):
            tournament_indices = random.sample(range(len(last_pop)), TOURNAMENT_SIZE)
            best_index = min(tournament_indices, key=lambda i: fitnesses[i])

            return last_pop[best_index]

        # Selects two best candidates from the tournament to be parents
        def select_parents(last_pop, fitnesses):
            parent1 = tournament_selection(last_pop, fitnesses)
            parent2 = tournament_selection(last_pop, fitnesses)

            # Ensures distinct parents
            while parent1 == parent2:
                parent2 = tournament_selection(last_pop, fitnesses)

            return parent1, parent2

        # Performs uniform crossover between parent genomes for exploring in early generations
        def uniform_crossover(parent1, parent2):
            return [random.choice([p1, p2]) for p1, p2 in zip(parent1, parent2)]

        # Performs n-point crossover between parent genomes for fine-tuning solutions near convergence
        def n_point_crossover(parent1, parent2, n_points=CROSSOVER_POINTS):
            length = len(parent1)
            crossover_points = sorted(random.sample(range(1, length), n_points))
            offspring_chromosome = []
            swap = False
            prev_point = 0

            # Performs the crossover between n points
            for point in crossover_points + [length]:
                if swap:
                    offspring_chromosome += parent2[prev_point:point]
                else:
                    offspring_chromosome += parent1[prev_point:point]
                swap = not swap
                prev_point = point

            return offspring_chromosome

        # Increases mutation rate gradually as stagnation count grows
        def adjust_mutation_rate(stag_count):
            mutation_rate = BASE_MUTATION_RATE + ((FINAL_MUTATION_RATE - BASE_MUTATION_RATE) *
                                                  min(1.0, stag_count / MUT_STAGNATION))
            if BASE_MUTATION_RATE < FINAL_MUTATION_RATE:
                return max(mutation_rate, BASE_MUTATION_RATE)
            else:
                return max(mutation_rate, FINAL_MUTATION_RATE)

        # Performs bit-flip mutation of child genome for exploring in early generations
        def bit_flip_mutation(g_in):
            x = random.randint(0, len(g_in) - 1)  # Randomly selects genes to flip

            return [not g_in[i] if i == x else g_in[i] for i in range(len(g_in))]

        # Performs swap mutation of child genome for fine-tuning solutions near convergence
        def swap_mutation(genome):
            num_genes_to_mutate = MUTATION_POINTS  # Number of swaps to perform
            for _ in range(num_genes_to_mutate):
                idx1, idx2 = random.sample(range(len(genome)), 2)  # Randomly selects mutating genes
                genome[idx1], genome[idx2] = genome[idx2], genome[idx1]

            return genome

        # Runs a generation step of the algorithm
        def generation_step(generation=0, pop=None, last_best_fitness=None, stag_count=0):
            # Recalculates mutation rate based on stagnation
            mutation_rate = adjust_mutation_rate(stag_count)

            # Stops after reaching max number of generations or if the algorithm is halted
            if generation >= NUM_GENERATIONS or not self.running:
                return

            # Initializes population if not provided
            if pop is None:
                pop = get_population()

            # Fitness calculations
            fitnesses = [calculate_fitness(genome) for genome in pop]
            best_of_gen = min(pop, key=lambda genome: calculate_fitness(genome))
            current_fitness = calculate_fitness(best_of_gen)

            # Checks for stagnation (no improvement in fitness)
            if last_best_fitness is not None and current_fitness == last_best_fitness:
                stag_count += 1
            elif current_fitness != 0:
                stag_count = 0  # Resets stagnation count if fitness improved

            # Creates a new population, starting with elites
            new_pop = []
            elites = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i])[:ELITISM_COUNT]
            for e in elites:
                new_pop.append(pop[e])

            # Fills the rest with new individuals using crossover and mutation
            while len(new_pop) < POP_SIZE:
                parent1, parent2 = select_parents(pop, fitnesses)

                # Uses crossover and mutation that favor exploration
                if stag_count < CROSS_STAGNATION:
                    child = uniform_crossover(parent1, parent2)
                    if random.random() < mutation_rate:
                        child = bit_flip_mutation(child)
                # Uses crossover and mutation that favor exploitation
                else:
                    child = n_point_crossover(parent1, parent2)
                    if random.random() < mutation_rate:
                        child = swap_mutation(child)
                # Adds the child to the new population
                new_pop.append(child)

            # Updates UI with current data
            self.after(0, self.clear_canvas)  # noqa: specific-warning-code
            self.after(0, self.draw_target)  # noqa: specific-warning-code
            self.after(0, self.draw_sum, calculate_gene_sum(best_of_gen), self.target)
            self.after(0, self.draw_genome, best_of_gen, generation, mutation_rate, stag_count)

            # Stops if the optimal solution is found or after a certain number of generations
            if current_fitness == 0 or generation == NUM_GENERATIONS:
                self.running = False
                print(f"Algorithm completed at generation {generation}.")
                print(f'Best genome:')
                print(f"[{''.join(['1' if gene else '0' for gene in best_of_gen])}]")
                return
            # Prints statistics until the solution is found or the generation limit is reached
            else:
                print(f'Best fitness of generation {generation}: {current_fitness}')
                print(f'Mutation rate: {mutation_rate}')
                print(f'Stagnation count: {stag_count}')
                print(f'Best genome:')
                print(f"[{''.join(['1' if gene else '0' for gene in best_of_gen])}]")
                print()

            # Applies stagnation measures unless fitness threshold of 1 is reached
            if current_fitness > 1:
                # Applies fitness sharing if stagnation is detected
                if stag_count % FIT_STAGNATION == 0 < stag_count:
                    print(f"Stagnation detected! Penalizing cases of fitness sharing.")
                    fitnesses = apply_fitness_sharing(new_pop, fitnesses)

                # Introduces random immigrants if stagnation is detected
                if stag_count % IMM_STAGNATION == 0 < stag_count:
                    num_immigrants = POP_SIZE // 10
                    print(f"Stagnation detected! Replacing {num_immigrants} worst genomes with random immigrants.")
                    new_pop = add_immigrants(num_immigrants, new_pop, fitnesses)

                # Applies crowding selection and resets counter if stagnation is detected
                if stag_count % CROWD_STAGNATION == 0 < stag_count:
                    print(f"Stagnation detected! Applying crowding selection.")
                    new_pop = crowding_selection(get_population(), fitnesses, new_pop)
                    stag_count = 0

            # Schedules the next generation step
            if self.running and min(fitnesses) != 0:
                self.after(int(SLEEP_TIME * 1000),
                           generation_step,
                           generation + 1,
                           new_pop,
                           current_fitness,
                           stag_count)

        # Starts the evolutionary process
        generation_step()


# Catches the main thread and instantiates the window class
if __name__ == '__main__':
    UI()
