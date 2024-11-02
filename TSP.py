import math
import random
import tkinter as tk
from tkinter import *

num_cities = 25
num_roads = 100
city_scale = 5
road_width = 4
padding = 100
population_size = 100
mutation_rate = 0.01
generations = 500

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, canvas, color='black'):
        canvas.create_oval(self.x-city_scale, self.y-city_scale, self.x+city_scale, self.y+city_scale, fill=color)

class Edge:
    def __init__(self, a, b):
        self.city_a = a
        self.city_b = b
        self.length = math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    def draw(self, canvas, color='grey', style=(2, 4)):
        canvas.create_line(self.city_a.x,
                           self.city_a.y,
                           self.city_b.x,
                           self.city_b.y,
                           fill=color,
                           width=road_width,
                           dash=style)

class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # Set the title of the window
        self.title("Traveling Salesman")
        # Hide the minimize/maximize/close decorations at the top of the window frame
        #   (effectively making it act like a full-screen application)
        self.option_add("*tearOff", FALSE)
        # Get the screen width and height
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        # Set the window width and height to fill the screen
        self.geometry("%dx%d+0+0" % (width, height))
        # Set the window content to fill the width * height area
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=width, height=height)
        w = width-padding
        h = height-padding*2

        self.cities_list = []
        self.roads_list = []
        self.edge_list = []

        def add_city():
            x = random.randint(padding, w)
            y = random.randint(padding, h)
            node = Node(x, y)
            self.cities_list.append(node)

        def add_road():
            a = random.randint(0, len(self.cities_list)-1)
            b = random.randint(0, len(self.cities_list)-1)
            #road = f'{min(a, b)},{max(a, b)}'
            while a == b or f'{min(a, b)},{max(a, b)}' in self.roads_list:
                a = random.randint(0, len(self.cities_list)-1)
                b = random.randint(0, len(self.cities_list)-1)
                #road = f'{min(a, b)},{max(a, b)}'
            edge = Edge(self.cities_list[a], self.cities_list[b])
            self.roads_list.append(f'{min(a, b)},{max(a, b)}')
            self.edge_list.append(edge)

        # Nested function to generate cities and roads
        def generate_city():
            for c in range(num_cities):
                add_city()
            for r in range(num_roads):
                add_road()

        # Nested function to draw cities and roads
        def draw_city():
            try:
                self.canvas.delete("all")
                for e in self.edge_list:
                    e.draw(self.canvas)
                for n in self.cities_list:
                    n.draw(self.canvas)
            except tk.TclError:
                pass  # Handle error if canvas is no longer valid
        
        def distance(city_a, city_b):
            return math.sqrt((city_a.x - city_b.x) ** 2 + (city_a.y - city_b.y) ** 2)

        def total_distance(tour):
            return sum(distance(self.cities_list[tour[i]], self.cities_list[tour[(i + 1) % len(tour)]]) for i in range(len(tour)))

        def create_population():
            return [random.sample(range(len(self.cities_list)), len(self.cities_list)) for _ in range(population_size)]
        
        def select_parents(population):
            weighted_population = [(tour, total_distance(tour)) for tour in population]
            weighted_population.sort(key=lambda x: x[1])
            return [tour for tour, _ in weighted_population[:10]]  # Keep top 10
        
        def crossover(parent1, parent2): #crossover
            child = [None] * len(parent1)
            start, end = sorted(random.sample(range(len(parent1)), 2))
            child[start:end] = parent1[start:end]
            pointer = 0
            for i in range(len(parent2)):
                if child[i] is None:
                    while parent2[pointer] in child:
                        pointer += 1
                    child[i] = parent2[pointer]
            return child
        
        def mutate(tour): #mutation
            if random.random() < mutation_rate:
                i, j = random.sample(range(len(tour)), 2)
                tour[i], tour[j] = tour[j], tour[i]

        def evolve_population(population):
            parents = select_parents(population)
            next_generation = []

            while len(next_generation) < population_size:
                parent1, parent2 = random.sample(parents, 2)
                child = crossover(parent1, parent2)
                mutate(child)
                next_generation.append(child)
            return next_generation
        
        def run_ga():
            population = create_population()
            best_solution = None
            best_distance = float('inf')

            for generation in range(generations):
                population = evolve_population(population)
                current_best = select_parents(population)[0]
                current_distance = total_distance(current_best)

                if current_distance < best_distance:
                    best_distance = current_distance
                    best_solution = current_best
                # Draw the current best solution
                try:
                    self.canvas.delete("all")
                    draw_city()  # Redraw cities and roads
                    # Highlight the best solution
                    for i in range(len(current_best)):
                        start_city = self.cities_list[current_best[i]]
                        end_city = self.cities_list[current_best[(i + 1) % len(current_best)]]
                        self.canvas.create_line(start_city.x, start_city.y, end_city.x, end_city.y, fill='green', width=road_width)
                    self.update()
                    self.after(100)  # Delay for visualization
                except tk.TclError:
                    break  # Exit the loop if the canvas is no longer valid

            return best_solution, best_distance

        def generate():
            self.cities_list.clear()
            self.roads_list.clear()
            self.edge_list.clear()

            generate_city()
            draw_city()

            # Run the genetic algorithm and find the best solution
            best_solution, best_distance = run_ga()
            print(f"Best distance: {best_distance}")

        # We create a standard banner menu bar and attach it to the window
        menu_bar = Menu(self)
        self['menu'] = menu_bar

        # We have to individually create the "File", "Edit", etc. cascade menus, and this is the first
        menu_TS = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_TS, label='Salesman', underline=0)

        # The add_command function adds an item to a menu, as opposed to add_cascade which adds a sub-menu
        # Note that we use command=generate without the () - we're telling it which function to call,
        #   not actually calling the function as part of the add_command
        menu_TS.add_command(label="Generate", command=generate, underline=0)

        # We have to call self.mainloop() in our constructor (__init__) to start the UI loop and display the window
        self.mainloop()

# In python, we have this odd construct to catch the main thread and instantiate our Window class
if __name__ == '__main__':
    UI()
