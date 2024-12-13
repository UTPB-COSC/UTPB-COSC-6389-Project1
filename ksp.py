import math
import random
import tkinter as tk
from tkinter import Menu, Canvas, FALSE
import threading

# ---------------------------
# Configuration Parameters
# ---------------------------
CONFIG = {
    "num_items": 100,
    "target_fraction": 0.7,
    "min_value": 128,
    "max_value": 2048,
    "screen_padding": 25,
    "item_padding": 5,
    "stroke_width": 5,
    "num_generations": 1000,
    "pop_size": 50,
    "elitism_count": 2,
    "tournament_size": 3,
    "initial_mutation_rate": 0.1,
    "min_mutation_rate": 0.01,
    "sleep_time": 0.1,
    "cols": 6
}


def get_random_color():
    """Generate a random RGB color in hex format."""
    r = random.randint(0x10, 0xff)
    g = random.randint(0x10, 0xff)
    b = random.randint(0x10, 0xff)
    return f'#{r:02x}{g:02x}{b:02x}'


class KnapsackItem:
    """Represents an individual knapsack item with a value and a visual representation."""
    def __init__(self, min_val, max_val, item_pad, stroke_w):
        self.value = random.randint(min_val, max_val)
        self.color = get_random_color()
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.item_padding = item_pad
        self.stroke_width = stroke_w

    def place_item(self, x, y, w, h):
        """Sets the position and size of the item on the canvas."""
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self, canvas, selected=False):
        """Draws the item. If selected is True, fill the rectangle."""
        text_x = self.x + self.w + self.item_padding + (self.stroke_width * 2)
        text_y = self.y + self.h / 2
        canvas.create_text(text_x, text_y, text=f'{self.value}')

        rect_fill = self.color if selected else ''
        rect_outline = self.color

        canvas.create_rectangle(
            self.x, self.y,
            self.x + self.w, self.y + self.h,
            fill=rect_fill,
            outline=rect_outline,
            width=self.stroke_width
        )


class KnapsackGUI(tk.Tk):
    """GUI application that sets up and runs a genetic algorithm-based knapsack solver."""
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

        self.title("Knapsack Solver")
        self.option_add("*tearOff", FALSE)
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.width, self.height))
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)

        self.items = []
        self.target = 0

        # Menu Bar
        menu_bar = Menu(self)
        self.config(menu=menu_bar)

        knap_menu = Menu(menu_bar)
        menu_bar.add_cascade(menu=knap_menu, label='Knapsack')

        knap_menu.add_command(label="Generate", command=self.cmd_generate_items)
        knap_menu.add_command(label="Set Target", command=self.cmd_set_target)
        knap_menu.add_command(label="Run", command=self.cmd_run_thread)

    def cmd_generate_items(self):
        """Generates the items and draws them on the canvas."""
        self.items.clear()
        self.generate_items()
        self.draw_all_items()

    def cmd_set_target(self):
        """Selects a subset of items as a target and computes their total value."""
        self.define_target_sum()
        self.draw_target()

    def cmd_run_thread(self):
        """Starts the genetic algorithm in a separate thread."""
        th = threading.Thread(target=self.execute_ga, args=())
        th.start()

    def generate_items(self):
        """Generates a unique set of items and places them on the canvas."""
        # Ensure unique values by regenerating if duplicated
        values_set = set()
        while len(self.items) < self.cfg["num_items"]:
            new_item = KnapsackItem(self.cfg["min_value"], self.cfg["max_value"],
                                    self.cfg["item_padding"], self.cfg["stroke_width"])
            if new_item.value not in values_set:
                values_set.add(new_item.value)
                self.items.append(new_item)

        # Compute layout parameters
        item_count = self.cfg["num_items"]
        cols = self.cfg["cols"]
        rows = math.ceil(item_count / cols)

        max_val = max(item.value for item in self.items)
        w = self.width - self.cfg["screen_padding"]
        h = self.height - self.cfg["screen_padding"]
        row_w = w / (cols + 2) - self.cfg["item_padding"]
        row_h = (h - 200) / rows

        # Place each item in a grid-like fashion
        idx = 0
        for c in range(cols):
            for r in range(rows):
                if idx >= item_count:
                    break
                itm = self.items[idx]
                item_w = row_w / 2
                # Ensure each item height is at least 1
                item_h = max((itm.value / max_val) * row_h, 1)
                x_pos = self.cfg["screen_padding"] + c * (row_w + self.cfg["item_padding"])
                y_pos = self.cfg["screen_padding"] + r * (row_h + self.cfg["item_padding"])
                itm.place_item(x_pos, y_pos, item_w, item_h)
                idx += 1

    def define_target_sum(self):
        """Randomly selects a fraction of items and sets the target sum as their total."""
        subset_size = int(self.cfg["num_items"] * self.cfg["target_fraction"])
        chosen = set()
        while len(chosen) < subset_size:
            chosen.add(random.choice(self.items))
        self.target = sum(itm.value for itm in chosen)

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_all_items(self, genome=None):
        """Draws all items. Highlights those selected if a genome is provided."""
        for i, itm in enumerate(self.items):
            active = (genome[i] if genome is not None else False)
            itm.draw(self.canvas, active)

    def draw_target(self):
        """Displays the target value as a separate bar."""
        x = (self.width - self.cfg["screen_padding"]) / 8 * 7
        y = self.cfg["screen_padding"]
        w = (self.width - self.cfg["screen_padding"]) / 8 - self.cfg["screen_padding"]
        h = self.height / 2 - self.cfg["screen_padding"]
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='black')
        self.canvas.create_text(x + w // 2, y + h + self.cfg["screen_padding"], 
                                text=f'Target: {self.target}', font=('Arial', 18))

    def draw_sum_bar(self, current_sum):
        """Draws a bar representing the current genome sum compared to the target."""
        x = (self.width - self.cfg["screen_padding"]) / 8 * 6
        y = self.cfg["screen_padding"]
        w = (self.width - self.cfg["screen_padding"]) / 8 - self.cfg["screen_padding"]
        max_h = self.height / 2 - self.cfg["screen_padding"]
        scaled_h = max_h * (current_sum / self.target) if self.target != 0 else 0

        diff = current_sum - self.target
        sign = '+' if diff > 0 else '-'
        self.canvas.create_rectangle(x, y, x + w, y + scaled_h, fill='black')
        self.canvas.create_text(x + w // 2, y + scaled_h + self.cfg["screen_padding"],
                                text=f'{current_sum} ({sign}{abs(diff)})',
                                font=('Arial', 18))

    def draw_generation_info(self, gen_num):
        """Displays the current generation number."""
        x = (self.width - self.cfg["screen_padding"]) / 8 * 6
        y = self.cfg["screen_padding"]
        w = (self.width - self.cfg["screen_padding"]) / 8 - self.cfg["screen_padding"]
        h = self.height / 4 * 3
        self.canvas.create_text(x + w, y + h + self.cfg["screen_padding"] * 2,
                                text=f'Generation {gen_num}', font=('Arial', 18))

    # ---------------------------
    # Genetic Algorithm
    # ---------------------------
    def compute_sum(self, genome):
        """Compute the sum of values included in the genome."""
        total = sum(itm.value for i, itm in enumerate(self.items) if genome[i])
        return total

    def fitness(self, genome):
        """Calculate the fitness of a genome based on its closeness to the target."""
        total = self.compute_sum(genome)
        diff = abs(total - self.target)

        # Penalize solutions far from the target more
        if diff > self.target * 0.5:
            return 1 / ((diff ** 2) + 1)
        return 1 / (diff + 1)

    def tournament_selection(self, population):
        """Select a parent using tournament selection."""
        contenders = random.sample(population, self.cfg["tournament_size"])
        return max(contenders, key=lambda g: self.fitness(g))

    def crossover(self, p1, p2):
        """Uniform crossover to create a child genome."""
        return [p1[i] if random.random() < 0.5 else p2[i] for i in range(len(p1))]

    def adaptive_mutation(self, genome, generation):
        """Adaptive mutation rate decreases over time."""
        max_gens = self.cfg["num_generations"]
        init_rate = self.cfg["initial_mutation_rate"]
        min_rate = self.cfg["min_mutation_rate"]
        cur_mut_rate = max(min_rate, init_rate * (1 - generation / max_gens))

        mutated = genome[:]
        for i in range(len(mutated)):
            if random.random() < cur_mut_rate:
                mutated[i] = not mutated[i]
        return mutated

    def create_initial_population(self):
        """Generates the initial population."""
        return [
            [random.random() < self.cfg["target_fraction"] for _ in range(self.cfg["num_items"])]
            for _ in range(self.cfg["pop_size"])
        ]

    def evolve_population(self, old_pop, generation):
        """Generate a new population from the old one using elitism, selection, crossover, and mutation."""
        sorted_pop = sorted(old_pop, key=lambda g: self.fitness(g), reverse=True)
        new_pop = sorted_pop[:self.cfg["elitism_count"]]

        # Fill the rest of the population
        while len(new_pop) < self.cfg["pop_size"]:
            p1 = self.tournament_selection(old_pop)
            p2 = self.tournament_selection(old_pop)
            child = self.crossover(p1, p2)
            child = self.adaptive_mutation(child, generation)
            new_pop.append(child)

        return new_pop

    def ga_step(self, generation=0, population=None):
        """One step of the GA. Updates the UI and schedules the next step unless solution found or max gen reached."""
        if population is None:
            population = self.create_initial_population()

        best = max(population, key=lambda g: self.fitness(g))
        best_fitness = self.fitness(best)
        best_sum = self.compute_sum(best)

        # Update UI
        self.after(0, self.clear_canvas)
        self.after(0, self.draw_target)
        self.after(0, self.draw_sum_bar, best_sum)
        self.after(0, self.draw_all_items, best)
        self.after(0, self.draw_generation_info, generation)

        # Print info to console
        print(f'Generation {generation}: Best Fitness: {best_fitness:.6f}, Best Sum: {best_sum}')

        # If not perfect solution, proceed to next generation
        if abs(best_sum - self.target) > 0 and generation < self.cfg["num_generations"]:
            new_population = self.evolve_population(population, generation)
            self.after(int(self.cfg["sleep_time"] * 1000), self.ga_step, generation + 1, new_population)

    def execute_ga(self):
        """Runs the genetic algorithm from the start."""
        self.ga_step()


def main():
    app = KnapsackGUI(CONFIG)
    app.mainloop()


if __name__ == '__main__':
    main()