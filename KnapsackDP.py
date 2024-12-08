import math
import random
import tkinter as tk
from tkinter import *
import threading
import numpy as np

# Constants
num_items = 100
frac_target = 0.75
min_value = 100
max_value = 2500

screen_padding = 25
item_padding = 5
stroke_width = 5

sleep_time = 0.05


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
        canvas.create_text(self.x + self.w + item_padding + stroke_width * 2, self.y + self.h / 2, text=f'{self.value}')
        if active:
            canvas.create_rectangle(self.x,
                                    self.y,
                                    self.x + self.w,
                                    self.y + self.h,
                                    fill=self.color,
                                    outline=self.color,
                                    width=stroke_width)
        else:
            canvas.create_rectangle(self.x,
                                    self.y,
                                    self.x + self.w,
                                    self.y + self.h,
                                    fill='',
                                    outline=self.color,
                                    width=stroke_width)


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

        menu_bar = Menu(self)
        self['menu'] = menu_bar
        menu_K = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_K, label='Knapsack', underline=0)

        def generate():
            self.generate_knapsack()
            self.draw_items()

        menu_K.add_command(label="Generate", command=generate, underline=0)

        self.target = 0

        def set_target():
            target_set = []
            for x in range(int(num_items * frac_target)):
                item = self.items_list[random.randint(0, len(self.items_list) - 1)]
                while item in target_set:
                    item = self.items_list[random.randint(0, len(self.items_list) - 1)]
                target_set.append(item)
            total = 0
            for item in target_set:
                total += item.value
            self.target = total
            self.draw_target()

        menu_K.add_command(label="Get Target", command=set_target, underline=0)

        def start_thread():
            thread = threading.Thread(target=self.run, args=())
            thread.start()

        menu_K.add_command(label="Run", command=start_thread, underline=0)

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
        for i in range(num_items):
            self.add_item()

        item_max = 0
        item_min = 9999
        for item in self.items_list:
            item_min = min(item_min, item.value)
            item_max = max(item_max, item.value)

        w = self.width - screen_padding
        h = self.height - screen_padding
        num_rows = math.ceil(num_items / 6)
        row_w = w / 8 - item_padding
        row_h = (h - 200) / num_rows

        for x in range(0, 6):
            for y in range(0, num_rows):
                if x * num_rows + y >= num_items:
                    break
                item = self.items_list[x * num_rows + y]
                item_w = row_w / 2
                item_h = max(item.value / item_max * row_h, 1)
                item.place(screen_padding + x * row_w + x * item_padding,
                           screen_padding + y * row_h + y * item_padding,
                           item_w,
                           item_h)

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
        self.canvas.create_text(x + w // 2, y + h + screen_padding, text=f'{self.target}', font=('Arial', 18))

    def draw_sum(self, item_sum, target):
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        h *= (item_sum / target)
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='black')
        self.canvas.create_text(x + w // 2, y + h + screen_padding,
                                text=f'{item_sum} ({"+" if item_sum > target else "-"}{abs(item_sum - target)})',
                                font=('Arial', 18))

    def draw_genome(self, genome):
        for i, is_active in enumerate(genome):
            self.items_list[i].draw(self.canvas, is_active)

    def run(self):
        # DP Algorithm
        capacity = self.target
        values = [item.value for item in self.items_list]
        n = len(values)

        dp = [[0] * (capacity + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for w in range(capacity + 1):
                if values[i - 1] <= w:
                    dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - values[i - 1]] + values[i - 1])
                else:
                    dp[i][w] = dp[i - 1][w]

        # Backtrack to find solution
        solution = [0] * n
        w = capacity
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                solution[i - 1] = 1
                w -= values[i - 1]

        self.after(0, self.clear_canvas)
        self.after(0, self.draw_target)
        self.after(0, self.draw_sum, sum(item.value for item, s in zip(self.items_list, solution) if s), self.target)
        self.after(0, self.draw_genome, solution)


if __name__ == '__main__':
    UI()
