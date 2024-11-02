import math
import random
import tkinter as tk
from tkinter import *

#Traveling salesman problem using ant colony optimization algorithm

num_cities = 25
city_scale = 5
road_width = 4
padding = 100
num_ants = 50
alpha = 1  # Importance of pheromone
beta = 2   # Importance of heuristic (distance)
evaporation_rate = 0.5
iterations = 100

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
        self.title("Traveling Salesman - ACO")
        self.option_add("*tearOff", FALSE)
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (width, height))
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=width, height=height)
        w = width - padding
        h = height - padding * 2

        self.cities_list = []
        self.edges = []
        self.pheromones = {}

        def add_city():
            x = random.randint(padding, w)
            y = random.randint(padding, h)
            node = Node(x, y)
            self.cities_list.append(node)

        def generate_cities():
            for _ in range(num_cities):
                add_city()
            for i in range(len(self.cities_list)):
                for j in range(i + 1, len(self.cities_list)):
                    edge = Edge(self.cities_list[i], self.cities_list[j])
                    self.edges.append(edge)
                    self.pheromones[(i, j)] = 1.0  # Initial pheromone level

        def distance(city_a, city_b):
            return math.sqrt((city_a.x - city_b.x) ** 2 + (city_a.y - city_b.y) ** 2)

        def total_distance(tour):
            return sum(distance(self.cities_list[tour[i]], self.cities_list[tour[(i + 1) % len(tour)]]) for i in range(len(tour)))

        def probability(current_city, unvisited):
            denom = sum((self.pheromones[(min(current_city, i), max(current_city, i))] ** alpha) *
                         ((1 / distance(self.cities_list[current_city], self.cities_list[i])) ** beta) for i in unvisited)
            probs = []
            for i in unvisited:
                prob = (self.pheromones[(min(current_city, i), max(current_city, i))] ** alpha) * \
                        ((1 / distance(self.cities_list[current_city], self.cities_list[i])) ** beta) / denom
                probs.append(prob)
            return probs

        def update_pheromones(best_tour, best_distance): # Evaporate pheromones
            for key in self.pheromones:
                self.pheromones[key] *= (1 - evaporation_rate)
            
            # Add new pheromones based on the best tour
            for i in range(len(best_tour)):
                start_city = best_tour[i]
                end_city = best_tour[(i + 1) % len(best_tour)]
                edge_key = (min(start_city, end_city), max(start_city, end_city))
                self.pheromones[edge_key] += 1.0 / best_distance

        def aco_algorithm(): #ant-colony algorithm
            best_tour = None
            best_distance = float('inf')

            for _ in range(iterations):
                all_tours = []
                for _ in range(num_ants):
                    tour = [random.randint(0, num_cities - 1)]
                    unvisited = set(range(num_cities)) - {tour[0]}

                    while unvisited:
                        current_city = tour[-1]
                        probs = probability(current_city, unvisited)
                        next_city = random.choices(list(unvisited), weights=probs)[0]
                        tour.append(next_city)
                        unvisited.remove(next_city)

                    all_tours.append(tour)
                    tour_distance = total_distance(tour)

                    if tour_distance < best_distance:
                        best_distance = tour_distance
                        best_tour = tour

                update_pheromones(best_tour, best_distance) # Update pheromones after all ants have moved

                # Draw the current best solution
                try:
                    self.canvas.delete("all")
                    for edge in self.edges:
                        edge.draw(self.canvas)
                    for node in self.cities_list:
                        node.draw(self.canvas)

                    # Highlight the best solution
                    for i in range(len(best_tour)):
                        start_city = self.cities_list[best_tour[i]]
                        end_city = self.cities_list[best_tour[(i + 1) % len(best_tour)]]
                        self.canvas.create_line(start_city.x, start_city.y, end_city.x, end_city.y, fill='red', width=road_width)

                    self.update()
                    self.after(100)  # Delay for visualization
                except tk.TclError:
                    break #exit the loop if the canvas is no longer valid

            return best_tour, best_distance

        def generate():
            self.cities_list.clear()
            self.edges.clear()
            self.pheromones.clear()

            generate_cities()
            self.canvas.delete("all")
            for edge in self.edges:
                edge.draw(self.canvas)
            for node in self.cities_list:
                node.draw(self.canvas)

            # Run ACO algorithm
            best_tour, best_distance = aco_algorithm()
            print(f"Best distance: {best_distance}")

        menu_bar = Menu(self)
        self['menu'] = menu_bar

        menu_TS = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_TS, label='Salesman', underline=0)

        menu_TS.add_command(label="Generate", command=generate, underline=0)

        self.mainloop()

if __name__ == '__main__':
    UI()
