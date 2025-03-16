import math
import random
import tkinter as tk
from tkinter import *
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s]: %(message)s"
)
logger = logging.getLogger(__name__)

num_items = 100
frac_target = 0.7
min_value = 128
max_value = 2048

screen_padding = 25
item_padding = 5
stroke_width = 5

sleep_time = 0.1


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
        super().__init__()
        self.title("Knapsack")
        self.option_add("*tearOff", FALSE)
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.width, self.height))
        self.state("zoomed")

        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)

        self.items_list = []
        self.target = 0

        menu_bar = Menu(self)
        self["menu"] = menu_bar

        menu_K = Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_K, label="Knapsack", underline=0)

        def generate():
            logger.debug("Generating knapsack items...")
            self.generate_knapsack()
            self.draw_items()
            logger.debug("Knapsack generation completed.")

        menu_K.add_command(label="Generate", command=generate, underline=0)

        def set_target():
            if not self.items_list:
                logger.warning("No items available to set a target.")
                return
            logger.debug("Setting target...")
            target_set = []
            for x in range(int(num_items * frac_target)):
                item = self.items_list[random.randint(0, len(self.items_list) - 1)]
                while item in target_set:
                    item = self.items_list[random.randint(0, len(self.items_list) - 1)]
                target_set.append(item)
            total = sum(i.value for i in target_set)
            self.target = total
            self.draw_target()
            logger.debug(f"Target set to {self.target}")

        menu_K.add_command(label="Get Target", command=set_target, underline=0)

        def start_thread():
            if not self.items_list:
                logger.warning(
                    "No items to run the algorithm on. Please generate items first."
                )
                return
            if self.target == 0:
                logger.warning("Target not set. Please set a target first.")
                return
            logger.debug("Starting DP solver in a separate thread...")
            thread = threading.Thread(target=self.run, args=())
            thread.start()

        menu_K.add_command(label="Run", command=start_thread, underline=0)

    def get_rand_item(self):
        i1 = Item()
        # Ensuring uniqueness by value (although not strictly required)
        for i2 in self.items_list:
            if i1.value == i2.value:
                return None
        return i1

    def add_item(self):
        item = self.get_rand_item()
        while item is None:
            item = self.get_rand_item()
        self.items_list.append(item)
        logger.debug(f"Item added: Value={item.value}, Color={item.color}")

    def generate_knapsack(self):
        self.items_list.clear()
        logger.debug("Generating items...")
        for i in range(num_items):
            self.add_item()

        item_max = max(item.value for item in self.items_list)
        w = self.width - screen_padding
        h = self.height - screen_padding
        num_rows = math.ceil(num_items / 6)
        row_w = w / 8 - item_padding
        row_h = (h - 200) / num_rows

        logger.debug("Placing items on the canvas...")
        for x in range(0, 6):
            for y in range(0, num_rows):
                if x * num_rows + y >= num_items:
                    break
                item = self.items_list[x * num_rows + y]
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

    def draw_items(self, active_items=None):
        if active_items is None:
            active_items = []
        for i, item in enumerate(self.items_list):
            item.draw(self.canvas, i in active_items)

    def draw_target(self):
        x = (self.width - screen_padding) / 8 * 7
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        self.canvas.create_rectangle(x, y, x + w, y + h, fill="black")
        self.canvas.create_text(
            x + w // 2,
            y + h + screen_padding,
            text=f"{self.target}",
            font=("Arial", 18),
        )

    def draw_sum(self, item_sum, target):
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 2 - screen_padding
        h *= (item_sum / target) if target != 0 else 0
        self.canvas.create_rectangle(x, y, x + w, y + h, fill="black")
        diff = abs(item_sum - target)
        sign = "+" if item_sum > target else "-"
        self.canvas.create_text(
            x + w // 2,
            y + h + screen_padding,
            text=f"{item_sum} ({sign}{diff})",
            font=("Arial", 18),
        )

    def draw_result_text(self, sum_val):
        x = (self.width - screen_padding) / 8 * 6
        y = screen_padding
        w = (self.width - screen_padding) / 8 - screen_padding
        h = self.height / 4 * 3
        self.canvas.create_text(
            x + w,
            y + h + screen_padding * 2,
            text=f"Result sum: {sum_val}",
            font=("Arial", 18),
        )

    def run(self):
        # DP-based solver for a "closest subset sum" problem
        values = [item.value for item in self.items_list]
        target = self.target
        max_sum = sum(values)
        logger.debug(
            f"Starting DP computation. Target={target}, Max sum of all items={max_sum}"
        )

        dp = [[False] * (max_sum + 1) for _ in range(num_items + 1)]
        dp[0][0] = True

        # Fill the DP table
        for i in range(1, num_items + 1):
            val = values[i - 1]
            for s in range(max_sum + 1):
                if dp[i - 1][s]:
                    dp[i][s] = True
                    if s + val <= max_sum:
                        dp[i][s + val] = True

            logger.debug(f"After processing item {i} (value={val}), DP row completed.")

        # Find closest sum
        closest_sum = None
        for diff in range(max_sum + 1):
            if target - diff >= 0 and dp[num_items][target - diff]:
                closest_sum = target - diff
                break
            if target + diff <= max_sum and dp[num_items][target + diff]:
                closest_sum = target + diff
                break

        logger.debug(f"Closest sum to target found: {closest_sum}")

        # Backtrack to find chosen items
        chosen_indices = []
        s = closest_sum
        for i in range(num_items, 0, -1):
            val = values[i - 1]
            if s - val >= 0 and dp[i - 1][s - val]:
                chosen_indices.append(i - 1)
                s -= val

        chosen_indices.reverse()  # for readability
        chosen_values = [values[i] for i in chosen_indices]
        logger.debug(f"Chosen subset indices: {chosen_indices}")
        logger.debug(f"Chosen subset values: {chosen_values}")
        logger.debug(f"Chosen subset sum: {sum(chosen_values)}")

        self.after(0, self.clear_canvas)
        self.after(0, self.draw_target)
        self.after(0, self.draw_sum, closest_sum, target)
        self.after(0, self.draw_items, chosen_indices)
        self.after(0, self.draw_result_text, closest_sum)


if __name__ == "__main__":
    app = UI()
    app.mainloop()
