import math
import random
import numpy as np
import tkinter as tk
from tkinter import *
import threading

num_items = 100
frac_target = 0.7
min_value = 128
max_value = 2048

screen_padding = 25
item_padding = 5
stroke_width = 5

num_generations = 2000  # Increased number of generations
pop_size = 100  # Population size
elitism_count = 5  # Number of elites to carry over
mutation_rate = 0.05  # Increased mutation rate

sleep_time = 0.01  # Reduced sleep time for faster iterations


def random_rgb_color():
    red = random.randint(0x10, 0xFF)
    green = random.randint(0x10, 0xFF)
    blue = random.randint(0x10, 0xFF)
    hex_color = "#{:02x}{:02x}{:02x}".format(red, green, blue)
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
            text=f"{self.value}",
        )
        if active:
            canvas.create_rectangle(
                self.x,
                self.y,
                self.x + self.w,
                self.y + self.h,
                fill=self.color,
                outline=self.color,
                width=stroke_width,
            )
        else:
            canvas.create_rectangle(
                self.x,
                self.y,
                self.x + self.w,
                self.y + self.h,
                fill="",
                outline=self.color,
                width=stroke_width,
            )


class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Knapsack")
        self.option_add("*tearOff", FALSE)
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.width, self.height))
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)

        self.items_list = []
        self.item_values = None  # Will store item values as a NumPy array

        # Create a label to display the current generation and best fitness
        self.status_label = tk.Label(self, text="", font=("Arial", 16))
        self.status_label.place(x=screen_padding, y=screen_padding)

        # Create menu
        menu_bar = Menu(self)
        self["menu"] = menu_bar

        menu_K = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_K, label="Knapsack", underline=0)

        def generate():
            self.generate_knapsack()
            self.draw_items()

        menu_K.add_command(label="Generate", command=generate, underline=0)

        self.target = 0

        def set_target():
            if not self.items_list:
                tk.messagebox.showerror("Error", "Please generate items first.")
                return
            target_set = random.sample(self.items_list, int(num_items * frac_target))
            total = sum(item.value for item in target_set)
            self.target = total
            self.draw_target()

        menu_K.add_command(label="Get Target", command=set_target, underline=0)

        def start_thread():
            if not self.items_list or self.target == 0:
                tk.messagebox.showerror(
                    "Error", "Please generate items and set target first."
                )
                return
            thread = threading.Thread(target=self.run, args=())
            thread.start()

        menu_K.add_command(label="Run", command=start_thread, underline=0)

        self.mainloop()

    def get_rand_item(self):
        while True:
            i1 = Item()
            if i1.value not in [item.value for item in self.items_list]:
                return i1

    def add_item(self):
        item = self.get_rand_item()
        self.items_list.append(item)

    def generate_knapsack(self):
        self.canvas.delete("all")
        self.items_list.clear()
        self.target = 0
        self.status_label.config(text="")
        for _ in range(num_items):
            self.add_item()

        self.item_values = np.array([item.value for item in self.items_list])

        item_max = self.item_values.max()

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
                    item_h,
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
        self.canvas.create_rectangle(x, y, x + w, y + h, fill="black")
        self.canvas.create_text(
            x + w // 2,
            y + h + screen_padding,
            text=f"Target: {self.target}",
            font=("Arial", 18),
        )

    def draw_sum(self, item_sum):
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        h *= min(item_sum / self.target, 1)  # Cap the height at the target
        self.canvas.create_rectangle(x, y, x + w, y + h, fill="black")
        diff = item_sum - self.target
        sign = "+" if diff > 0 else "-"
        self.canvas.create_text(
            x + w // 2,
            y + h + screen_padding,
            text=f"Sum: {item_sum} ({sign}{abs(diff)})",
            font=("Arial", 18),
        )

    def draw_genome(self, genome):
        for i in range(num_items):
            item = self.items_list[i]
            active = genome[i]
            item.draw(self.canvas, active)
        # Draw items again to ensure proper layering
        # self.draw_items()

    def run(self):
        def fitness(population):
            total_values = np.dot(population, self.item_values)
            fitness_scores = np.empty(pop_size)
            over_target = total_values > self.target
            # Apply severe penalty for exceeding the target
            fitness_scores[over_target] = (
                total_values[over_target] - self.target
            ) + 1000
            # Fitness is the difference to target for under-target solutions
            fitness_scores[~over_target] = self.target - total_values[~over_target]
            return fitness_scores

        def select_parents(population, fitness_scores, tournament_size=5):
            parents = []
            for _ in range(2):
                participants_idx = np.random.choice(
                    pop_size, tournament_size, replace=False
                )
                participants = population[participants_idx]
                participants_fitness = fitness_scores[participants_idx]
                winner_idx = np.argmin(participants_fitness)
                winner = participants[winner_idx]
                parents.append(winner)
            return parents[0], parents[1]

        def crossover(parent1, parent2):
            crossover_point = np.random.randint(1, num_items - 1)
            child = np.concatenate(
                (parent1[:crossover_point], parent2[crossover_point:])
            )
            return child

        def mutate(genome):
            mutation_indices = np.random.rand(num_items) < mutation_rate
            genome[mutation_indices] = 1 - genome[mutation_indices]  # Flip bits
            return genome

        # Initialize population
        population = np.random.randint(2, size=(pop_size, num_items))
        best_fitness = float("inf")
        best_genome = None

        for generation in range(num_generations):
            fitness_scores = fitness(population)
            min_fitness_idx = np.argmin(fitness_scores)
            min_fitness = fitness_scores[min_fitness_idx]
            best_genome_gen = population[min_fitness_idx]

            # Update best solution found
            if min_fitness < best_fitness:
                best_fitness = min_fitness
                best_genome = best_genome_gen.copy()

            # Update UI
            self.after(0, self.clear_canvas)
            self.after(0, self.draw_target)
            self.after(0, self.draw_sum, np.dot(best_genome, self.item_values))
            self.after(0, self.draw_genome, best_genome)
            self.status_label.config(
                text=f"Generation: {generation}, Best Fitness: {best_fitness}"
            )
            self.update_idletasks()

            if best_fitness == 0:
                print("Optimal solution found!")
                break

            # Elitism: keep the best genomes
            sorted_indices = np.argsort(fitness_scores)
            elites = population[sorted_indices[:elitism_count]]

            # Generate new population
            new_population = elites.copy()
            while len(new_population) < pop_size:
                parent1, parent2 = select_parents(population, fitness_scores)
                child = crossover(parent1, parent2)
                child = mutate(child)
                new_population = np.vstack([new_population, child])

            population = new_population[:pop_size]  # Ensure population size

            # Sleep to control iteration speed
            threading.Event().wait(sleep_time)

        # Final update
        self.after(0, self.clear_canvas)
        self.after(0, self.draw_target)
        self.after(0, self.draw_sum, np.dot(best_genome, self.item_values))
        self.after(0, self.draw_genome, best_genome)
        self.status_label.config(
            text=f"Final Generation: {generation}, Best Fitness: {best_fitness}"
        )
        self.update_idletasks()


if __name__ == "__main__":
    UI()
