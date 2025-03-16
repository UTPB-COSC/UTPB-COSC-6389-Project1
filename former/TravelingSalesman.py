import math
import random
import tkinter as tk
from tkinter import *

num_cities = 25
num_roads = 100
city_scale = 5
road_width = 4
padding = 100


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

        cities_list = []
        roads_list = []
        edge_list = []

        def add_city():
            x = random.randint(padding, w)
            y = random.randint(padding, h)

            node = Node(x, y)
            cities_list.append(node)

        def add_road():
            a = random.randint(0, len(cities_list)-1)
            b = random.randint(0, len(cities_list)-1)

            road = f'{min(a, b)},{max(a, b)}'
            while a == b or road in roads_list:
                a = random.randint(0, len(cities_list)-1)
                b = random.randint(0, len(cities_list)-1)
                road = f'{min(a, b)},{max(a, b)}'

            edge = Edge(cities_list[a], cities_list[b])
            roads_list.append(road)
            edge_list.append(edge)

        def generate_city():
            for c in range(num_cities):
                add_city()
            for r in range(num_roads):
                add_road()

        def draw_city():
            #clear_canvas()
            for e in edge_list:
                e.draw(self.canvas)
            for n in cities_list:
                n.draw(self.canvas)

        def draw_genome(genome):
            #clear_canvas()
            for e in range(num_roads):
                edge = edge_list[e]
                color = 'grey'
                style = (2, 4)
                if genome[e]:
                    color = 'red'
                    style = (1, 0)
                edge.draw(self.canvas, color, style)
            for n in cities_list:
                n.draw(self.canvas, 'red')

        # We create a standard banner menu bar and attach it to the window
        menu_bar = Menu(self)
        self['menu'] = menu_bar

        # We have to individually create the "File", "Edit", etc. cascade menus, and this is the first
        menu_TS = Menu(menu_bar)
        # The underline=0 parameter doesn't actually do anything by itself,
        #   but if you also create an "accelerator" so that users can use the standard alt+key shortcuts
        #   for the menu, it will underline the appropriate key to indicate the shortcut
        menu_bar.add_cascade(menu=menu_TS, label='Salesman', underline=0)

        def generate():
            generate_city()
            draw_city()
        # The add_command function adds an item to a menu, as opposed to add_cascade which adds a sub-menu
        # Note that we use command=generate without the () - we're telling it which function to call,
        #   not actually calling the function as part of the add_command
        menu_TS.add_command(label="Generate", command=generate, underline=0)

        # We have to call self.mainloop() in our constructor (__init__) to start the UI loop and display the window
        self.mainloop()


# In python, we have this odd construct to catch the main thread and instantiate our Window class
if __name__ == '__main__':
    UI()
