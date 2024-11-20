import math
import random
import tkinter as tk
from tkinter import *
import threading
import numpy as np
from multiprocessing.pool import ThreadPool

# Global Variables
num_items = 100
frac_target = 0.7
min_value = 128
max_value = 2048

screen_padding = 25
item_padding = 5
stroke_width = 5

num_generations = 500  # Reduced for quicker convergence
pop_size = 200         # Increased population size
elitism_count = 5      # Increased number of elites
mutation_rate = 0.05   # Adjusted mutation rate

sleep_time = 0.05      # Reduced sleep time for faster UI updates


def random_rgb_color():
    red = random.randint(0x10, 0xff)
    green = random.randint(0x10, 0xff)
    blue = random.randint(0x10, 0xff)
    hex_color = '#{:02x}{:02x}{:02x}'.format(red, green, blue)
    return hex_color


class Item:
    def __init__(self):
        self.value = random.randint(min_value, max_value)
        self.color = random_rgb_color()
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    def place(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self, canvas, active=False):
        canvas.create_text(
            self.x + self.w + item_padding + stroke_width * 2,
            self.y + self.h / 2,
            text=f'{self.value}'
        )
        if active:
            canvas.create_rectangle(
                self.x,
                self.y,
                self.x + self.w,
                self.y + self.h,
                fill=self.color,
                outline=self.color,
                width=stroke_width
            )
        else:
            canvas.create_rectangle(
                self.x,
                self.y,
                self.x + self.w,
                self.y + self.h,
                fill='',
                outline=self.color,
                width=stroke_width
            )


class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # Set the title of the window
        self.title("Knapsack Solver")
        # Hide the minimize/maximize/close decorations at the top of the window frame
        self.option_add("*tearOff", FALSE)
        # Get the screen width and height
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        # Set the window width and height to fill the screen
        self.geometry("%dx%d+0+0" % (self.width, self.height))
        # Set the window content to fill the width * height area
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)

        self.items_list = []

        # Create the menu bar
        menu_bar = Menu(self)
        self['menu'] = menu_bar

        # Knapsack menu
        menu_K = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_K, label='Knapsack', underline=0)

        def generate():
            self.generate_knapsack()
            self.draw_items()

        menu_K.add_command(label="Generate", command=generate, underline=0)

        self.target = 0

        def set_target():
            target_set = random.sample(self.items_list, int(num_items * frac_target))
            total = sum(item.value for item in target_set)
            self.target = total
            self.draw_target()

        menu_K.add_command(label="Get Target", command=set_target, underline=0)

        def start_thread():
            thread = threading.Thread(target=self.run, args=())
            thread.start()

        menu_K.add_command(label="Run", command=start_thread, underline=0)

        # Start the UI loop
        self.mainloop()

    def get_rand_item(self):
        i1 = Item()
        for i2 in self.items_list:
            if i1.value == i2.value:
                return None
        return i1

    def add_item(self):
        item = self.get_rand_item()
        while item is None:
            item = self.get_rand_item()
        self.items_list.append(item)

    def generate_knapsack(self):
        self.items_list = []  # Reset the items list
        for _ in range(num_items):
            self.add_item()

        item_max = max(item.value for item in self.items_list)
        w = self.width - screen_padding
        h = self.height - screen_padding
        num_rows = math.ceil(num_items / 6)
        row_w = w / 8 - item_padding
        row_h = (h - 200) / num_rows

        for x in range(0, 6):
            for y in range(0, num_rows):
                idx = x * num_rows + y
                if idx >= num_items:
                    break
                item = self.items_list[idx]
                item_w = row_w / 2
                item_h = max(item.value / item_max * row_h, 1)
                item.place(
                    screen_padding + x * row_w + x * item_padding,
                    screen_padding + y * row_h + y * item_padding,
                    item_w,
                    item_h
                )

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_items(self):
        for item in self.items_list:
            item.draw(self.canvas)

    def draw_target(self):
        x = (self.width - screen_padding) / 8 * 7
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='black')
        self.canvas.create_text(
            x + w // 2, y + h + screen_padding,
            text=f'Target: {self.target}', font=('Arial', 18)
        )

    def draw_sum(self, item_sum):
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h_total = self.height / 2 - screen_padding
        h = h_total * (item_sum / self.target) if self.target else 0
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='black')
        diff = item_sum - self.target
        sign = "+" if diff > 0 else ""
        self.canvas.create_text(
            x + w // 2, y + h + screen_padding,
            text=f'Sum: {item_sum} ({sign}{diff})', font=('Arial', 18)
        )

    def draw_genome(self, genome, gen_num):
        for i in range(num_items):
            item = self.items_list[i]
            active = genome[i]
            item.draw(self.canvas, active)
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 4 * 3
        self.canvas.create_text(
            x + w, y + h + screen_padding * 2,
            text=f'Generation {gen_num}', font=('Arial', 18)
        )

    def run(self):
        global pop_size
        global num_generations

        item_values = np.array([item.value for item in self.items_list])

        def gene_sum(genome):
            return np.dot(genome, item_values)

        def fitness(genome):
            total = gene_sum(genome)
            return abs(total - self.target)

        def get_population(last_pop=None, fitnesses=None):
            population = []

            if last_pop is None:
                # Initialize population randomly
                return np.random.choice(
                    [True, False], size=(pop_size, num_items)
                )
            else:
                # Convert lists to numpy arrays for efficient operations
                last_pop = np.array(last_pop)
                fitnesses = np.array(fitnesses)

                # Elitism - Keep the top individuals
                elite_indices = np.argsort(fitnesses)[:elitism_count]
                elites = last_pop[elite_indices]
                population.extend(elites)

                # Tournament selection parameters
                tournament_size = 5

                def select_parent():
                    participants = random.sample(range(len(last_pop)), tournament_size)
                    participant_fitnesses = fitnesses[participants]
                    winner_index = participants[np.argmin(participant_fitnesses)]
                    return last_pop[winner_index]

                # Generate new individuals
                while len(population) < pop_size:
                    parent1 = select_parent()
                    parent2 = select_parent()

                    # Single-point crossover
                    if random.random() < 0.9:  # Crossover probability
                        crossover_point = random.randint(1, num_items - 1)
                        child = np.concatenate(
                            (parent1[:crossover_point], parent2[crossover_point:])
                        )
                    else:
                        child = parent1.copy()

                    # Mutation
                    mutation_mask = np.random.rand(num_items) < mutation_rate
                    child = np.logical_xor(child, mutation_mask)

                    population.append(child)

                return np.array(population)

        def generation_step(generation=0, pop=None):
            if generation >= num_generations:
                return

            if pop is None:
                pop = get_population()
            else:
                pop = np.array(pop)

            # Evaluate fitness in parallel
            with ThreadPool() as pool:
                fitnesses = pool.map(fitness, pop)

            fitnesses = np.array(fitnesses)
            best_index = np.argmin(fitnesses)
            best_fitness = fitnesses[best_index]
            best_genome = pop[best_index]

            print(f'Generation {generation}: Best fitness = {best_fitness}')

            # Update UI every N generations
            if generation % 5 == 0 or best_fitness == 0:
                self.after(0, self.clear_canvas)
                self.after(0, self.draw_target)
                self.after(0, self.draw_sum, gene_sum(best_genome))
                self.after(0, self.draw_genome, best_genome, generation)

            # Stop if the optimal solution is found
            if best_fitness == 0:
                print("Optimal solution found!")
                return

            # Schedule next generation
            self.after(
                int(sleep_time * 1000),
                generation_step,
                generation + 1,
                get_population(pop, fitnesses)
            )

        # Start the evolutionary process
        generation_step()


if __name__ == '__main__':
    UI()
