import tkinter as tk
from tkinter import ttk, messagebox
import random
from typing import List, Optional


class SubsetSumSolver:
    """
        A class to solve the subset sum problem using dynamic programming.

        initialization method for SubsetSumSolver class

        :param items: List of integers to find the subset from
        :param target_sum: The target sum to achieve from the subset of items
    """

    def __init__(self, items: List[int], target_sum: int):
        self.items = items
        self.target_sum = target_sum
        self.dp_table = []

    def solve(self) -> Optional[List[int]]:
        self._initialize_dp_table()
        self._populate_dp_table()
        if not self.dp_table[len(self.items)][self.target_sum]:
            return None
        return self._find_solution_items()

    def _initialize_dp_table(self) -> None:
        num_items = len(self.items)
        target = self.target_sum
        self.dp_table = [[False] * (target + 1) for _ in range(num_items + 1)]
        for i in range(num_items + 1):
            self.dp_table[i][0] = True

    def _populate_dp_table(self) -> None:
        for i in range(1, len(self.items) + 1):
            for j in range(1, self.target_sum + 1):
                if j < self.items[i - 1]:
                    self.dp_table[i][j] = self.dp_table[i - 1][j]
                else:
                    self.dp_table[i][j] = self.dp_table[i - 1][j] or self.dp_table[i - 1][j - self.items[i - 1]]

    def _find_solution_items(self) -> List[int]:
        solution_items = []
        i, j = len(self.items), self.target_sum
        while i > 0 and j > 0:
            if self.dp_table[i][j] and not self.dp_table[i - 1][j]:
                solution_items.append(self.items[i - 1])
                j -= self.items[i - 1]
            i -= 1
        return solution_items[::-1]


def generate_numbers(count: int, max_value: int = 20) -> List[int]:
    """
    :param count: The number of random integers to generate.
    :param max_value: The upper bound for the random integers, inclusive. Default is 20.
    :return: A list of randomly generated integers.
    """
    return [random.randint(1, max_value) for _ in range(count)]


def solve_subset_sum():
    """
    :return: None
        This function attempts to solve the subset sum problem
        using the inputs provided in entry_num_count and entry_target_sum.
        It generates a list of numbers and uses the SubsetSumSolver to find
        a subset that sums to the target value. The result is then displayed
        in lbl_result. If the inputs are invalid, an error message is shown.
    """
    try:
        count = int(entry_num_count.get())
        target_sum = int(entry_target_sum.get())
        items = generate_numbers(count)
        solver = SubsetSumSolver(items, target_sum)
        solution = solver.solve()
        if solution:
            result_message = f"Subset found that sums to {target_sum}: {solution} with sum {sum(solution)}"
        else:
            result_message = f"No subset found that sums to {target_sum}."
        lbl_result.config(text=f"Generated Numbers: {items}\n{result_message}")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for count and target sum.")


# Set up the GUI
root = tk.Tk()
root.title("Subset Sum Solver")
root.geometry('500x300')

style = ttk.Style()
style.configure('TButton', font=('Arial', 10))
style.configure('TLabel', font=('Arial', 10))
style.configure('TEntry', font=('Arial', 10))
style.configure('TFrame', padding='10')

main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# User Input for Number Count
lbl_num_count = ttk.Label(main_frame, text="How many random numbers to generate:")
lbl_num_count.grid(column=0, row=0, sticky=tk.W, pady=5)
entry_num_count = ttk.Entry(main_frame)
entry_num_count.grid(column=1, row=0, pady=5, padx=10)

# User Input for Target Sum
lbl_target_sum = ttk.Label(main_frame, text="Enter the target sum:")
lbl_target_sum.grid(column=0, row=1, sticky=tk.W, pady=5)
entry_target_sum = ttk.Entry(main_frame)
entry_target_sum.grid(column=1, row=1, pady=5, padx=10)

# Button to Solve
btn_solve = ttk.Button(main_frame, text="Solve", command=solve_subset_sum)
btn_solve.grid(column=0, row=2, columnspan=2, pady=10)

# Label to Show Results
lbl_result = ttk.Label(main_frame, text="Generated Numbers and Result will appear here", wraplength=400)
lbl_result.grid(column=0, row=3, columnspan=2, pady=10)

# Start the GUI main loop
root.mainloop()
