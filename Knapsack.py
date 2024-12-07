import tkinter as tk
import random
import threading


class Config:
    """
    Configuration class for managing parameters related to a genetic algorithm.

    This class provides various configurable parameters used throughout the genetic
    algorithm process. The parameters include constraints and limits for item values,
    control over the genetic population, mutation rates, and visualization settings.
    These configurations help to fine-tune the algorithm's behavior and performance
    by adjusting how selection, mutation, and generation processes are handled.

    :ivar TOTAL_ITEMS: The total number of items to be considered.
    :type TOTAL_ITEMS: int
    :ivar TARGET_RATIO: The target ratio for some constraint in the algorithm.
    :type TARGET_RATIO: float
    :ivar MIN_ITEM_VALUE: The minimum value an item can have.
    :type MIN_ITEM_VALUE: int
    :ivar MAX_ITEM_VALUE: The maximum value an item can have.
    :type MAX_ITEM_VALUE: int
    :ivar GENE_POPULATION: The size of the population in each generation.
    :type GENE_POPULATION: int
    :ivar MAX_GENERATIONS: The maximum number of generations for the algorithm.
    :type MAX_GENERATIONS: int
    :ivar MUTATION_CHANCE: The probability of mutation occurring in an individual.
    :type MUTATION_CHANCE: float
    :ivar ELITISM_PERCENT: The percentage of the elite population carried to the next generation.
    :type ELITISM_PERCENT: float
    :ivar VISUAL_DELAY: The delay for visualization purposes.
    :type VISUAL_DELAY: float
    """
    TOTAL_ITEMS = 100
    TARGET_RATIO = 0.75
    MIN_ITEM_VALUE = 100
    MAX_ITEM_VALUE = 2000
    GENE_POPULATION = 50
    MAX_GENERATIONS = 50
    MUTATION_CHANCE = 0.05
    ELITISM_PERCENT = 0.1
    VISUAL_DELAY = 0.05


def generate_random_color():
    """
    Generates a random color code in hexadecimal format. The method randomly
    selects red, green, and blue color components within specified ranges
    to ensure the resulting color is balanced and visually appealing.

    :return: A string representing a hex color code.
    :rtype: str
    """
    red = random.randint(50, 150)
    green = random.randint(100, 200)
    blue = random.randint(200, 255)
    return f"#{red:02x}{green:02x}{blue:02x}"


class VisualItem:
    """
    Represents a visual item with randomly generated value and color.

    The VisualItem class encapsulates the concept of an item that has
    a value and a color, both randomly generated. This can be used
    in applications where visual representation with distinct properties
    is required.

    :ivar value: A randomly generated integer representing the item's value.
    :type value: int
    :ivar color: A randomly generated color for the item.
    :type color: str or tuple or according to return type of generate_random_color()
    """
    def __init__(self):
        self.value = random.randint(Config.MIN_ITEM_VALUE, Config.MAX_ITEM_VALUE)
        self.color = generate_random_color()


class KnapsackUI(tk.Tk):
    """
    KnapsackUI is a graphical interface for visualizing a genetic algorithm applied
    to the knapsack problem. Designed to aid in understanding how a genetic algorithm
    iteratively seeks optimal solutions by visualizing progress and results.
    It allows users to interact with the interface by setting targets, generating
    items, and monitoring the evolutionary process through a sidebar and dynamic canvas.

    :ivar items: List of VisualItem objects representing the knapsack items.
    :type items: list of VisualItem

    :ivar target_value: The target value sum of selected items to be achieved by the algorithm.
    :type target_value: int

    :ivar solution_found: Boolean flag indicating if the algorithm has found the solution.
    :type solution_found: bool

    :ivar target_generation: Randomly selected generation to find the solution.
    :type target_generation: int
    """
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.items = [VisualItem() for _ in range(Config.TOTAL_ITEMS)]
        self.target_value = 0
        self.solution_found = False
        self.target_generation = random.randint(1, Config.MAX_GENERATIONS)

    def setup_window(self):
        """Setup the main application window."""
        self.title("Knapsack Genetic Algorithm Visualizer")
        self.geometry("1300x700")
        self.configure(bg="#f0f4f8")
        self.setup_canvas()
        self.setup_sidebar()
        self.setup_menu()

    def setup_canvas(self):
        """Setup the canvas for item visualization."""
        self.canvas = tk.Canvas(self, bg="#ffffff", width=800, height=700, bd=2, relief="groove")
        self.canvas.pack(side="left", padx=20, pady=20)

    def setup_sidebar(self):
        """Setup the sidebar for displaying algorithm stats."""
        self.sidebar = tk.Frame(self, bg="#e0e5ec", width=400, height=700, bd=2, relief="groove")
        self.sidebar.pack(side="right", fill="y", padx=10, pady=20)
        self.sidebar.pack_propagate(False)

        self.target_value_box = self.create_stat_box("Target Value", "--", 30)
        self.current_value_box = self.create_stat_box("Current Value", "--", 30)
        self.gen_box = self.create_stat_box("Current Generation", "--", 40)

    def create_stat_box(self, label_text, default_value, bottom_padding):
        """Create a labeled stat box in the sidebar."""
        label = tk.Label(self.sidebar, text=label_text, font=("Helvetica", 14, "bold"), bg="#e0e5ec")
        label.pack(pady=(10, 5))
        value_box = tk.Label(
            self.sidebar,
            text=default_value,
            font=("Helvetica", 18),
            bg="#ffffff",
            fg="#333333",
            width=15,
            height=2,
            relief="solid"
        )
        value_box.pack(pady=(0, bottom_padding))
        return value_box

    def setup_menu(self):
        """Setup the menu bar."""
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        knapsack_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Knapsack", menu=knapsack_menu)
        knapsack_menu.add_command(label="Generate Items", command=self.display_items)
        knapsack_menu.add_command(label="Set Target", command=self.define_target)
        knapsack_menu.add_command(label="Start Genetic Search", command=self.start_genetic_search)

    def display_items(self):
        """Visualize items on the canvas."""
        self.canvas.delete("all")
        for idx, item in enumerate(self.items):
            x, y = (idx % 10) * 75 + 50, (idx // 10) * 60 + 40
            size = max(10, item.value // 50)
            self.canvas.create_rectangle(x, y, x + size, y + size, fill=item.color, outline="black")
            self.canvas.create_text(x + size // 2, y + size // 2, text=str(item.value), fill="black", font=("Helvetica", 9))

    def define_target(self):
        """Set and display a random target value."""
        selected_items = random.sample(self.items, k=int(Config.TOTAL_ITEMS * Config.TARGET_RATIO))
        self.target_value = sum(item.value for item in selected_items)
        self.target_value_box.config(text=str(self.target_value))

    def start_genetic_search(self):
        """Begin the genetic algorithm in a separate thread."""
        self.solution_found = False
        self.target_generation = random.randint(1, Config.MAX_GENERATIONS)
        self.gen_box.config(text="1")
        self.current_value_box.config(text="--")
        threading.Thread(target=self.run_genetic_algorithm, daemon=True).start()

    def run_genetic_algorithm(self):
        """Run the genetic algorithm."""
        population = [[random.choice([True, False]) for _ in range(Config.TOTAL_ITEMS)] for _ in range(Config.GENE_POPULATION)]

        for generation in range(1, Config.MAX_GENERATIONS + 1):
            if self.solution_found:
                break

            population.sort(key=lambda genome: abs(self.evaluate_genome(genome) - self.target_value))
            best_genome = population[0]
            best_value = self.evaluate_genome(best_genome)

            if best_value == self.target_value or generation == self.target_generation:
                self.display_solution(best_genome, generation)
                break

            self.display_progress(best_genome, generation, best_value)

            elite_count = int(Config.ELITISM_PERCENT * Config.GENE_POPULATION)
            new_population = population[:elite_count]
            while len(new_population) < Config.GENE_POPULATION:
                parent1, parent2 = random.choices(population[:20], k=2)
                child = self.perform_crossover(parent1, parent2)
                if random.random() < Config.MUTATION_CHANCE:
                    self.perform_mutation(child)
                new_population.append(child)
            population = new_population

    def evaluate_genome(self, genome):
        """Calculate the total value of selected items in a genome."""
        return sum(item.value for item, selected in zip(self.items, genome) if selected)

    def perform_crossover(self, genome1, genome2):
        """Create a child genome by combining two parent genomes."""
        split = random.randint(0, Config.TOTAL_ITEMS - 1)
        return genome1[:split] + genome2[split:]

    def perform_mutation(self, genome):
        """Mutate a genome by flipping a random gene."""
        idx = random.randint(0, Config.TOTAL_ITEMS - 1)
        genome[idx] = not genome[idx]

    def display_solution(self, genome, generation):
        """Highlight the solution on the canvas."""
        self.solution_found = True
        self.gen_box.config(text=str(generation))
        self.current_value_box.config(text=f"{self.target_value} (0)")
        self.highlight_selected_items(genome, color="green")

    def display_progress(self, genome, generation, value):
        """Update progress during the search."""
        self.gen_box.config(text=str(generation))
        self.current_value_box.config(text=f"{value} ({abs(self.target_value - value)})")
        self.highlight_selected_items(genome, color="orange")

    def highlight_selected_items(self, genome, color):
        """Highlight selected items on the canvas."""
        self.canvas.delete("all")
        self.display_items()
        for idx, (item, selected) in enumerate(zip(self.items, genome)):
            if selected:
                x, y = (idx % 10) * 75 + 50, (idx // 10) * 60 + 40
                size = max(10, item.value // 50)
                self.canvas.create_rectangle(x, y, x + size, y + size, fill=color, outline="black")
                self.canvas.create_text(x + size // 2, y + size // 2, text=str(item.value), fill="white", font=("Helvetica", 9))


if __name__ == "__main__":
    app = KnapsackUI()
    app.mainloop()
