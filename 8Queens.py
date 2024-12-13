import tkinter as tk
import random
from tkinter import messagebox, ttk
import time


class EightQueensGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Eight Queens Solver")
        self.board_size = 8
        self.cell_size = 50

        # Create Canvas for the Chess Board
        self.canvas = tk.Canvas(root, width=self.board_size * self.cell_size,
                                height=self.board_size * self.cell_size)
        self.canvas.pack(pady=10)

        # Frame for buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # Buttons for solving and clearing
        self.btn_backtracking = tk.Button(button_frame, text="Solve with Backtracking",
                                          command=self.solve_backtracking)
        self.btn_backtracking.grid(row=0, column=0, padx=5)

        self.btn_genetic = tk.Button(button_frame, text="Solve with Genetic Algorithm",
                                     command=self.solve_genetic_algorithm)
        self.btn_genetic.grid(row=0, column=1, padx=5)

        self.btn_clear = tk.Button(button_frame, text="Clear Board",
                                   command=self.clear_board)
        self.btn_clear.grid(row=0, column=2, padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = "white" if (row + col) % 2 == 0 else "lightgray"
                self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                             (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                                             fill=color, outline="gray")

    def display_solution(self, board):
        self.draw_board()
        for row, col in enumerate(board):
            self.canvas.create_text(col * self.cell_size + self.cell_size // 2,
                                    row * self.cell_size + self.cell_size // 2,
                                    text="♕", font=("Arial", 24), fill="black")

    def solve_backtracking(self):
        self.clear_board()
        board = [-1] * self.board_size
        start_time = time.time()
        if self.backtracking_helper(board, 0):
            end_time = time.time()
            self.display_solution(board)
            print(f"Backtracking solution found in {end_time - start_time:.4f} seconds")
            messagebox.showinfo("Success", "Solution found with backtracking!")
        else:
            messagebox.showinfo("No Solution", "No solution found with backtracking.")

    def is_safe(self, board, row, col):
        for i in range(row):
            if board[i] == col or abs(board[i] - col) == row - i:
                return False
        return True

    def backtracking_helper(self, board, row):
        if row == self.board_size:
            return True
        for col in range(self.board_size):
            if self.is_safe(board, row, col):
                board[row] = col
                print(f"Trying: Row {row}, Column {col}")
                if self.backtracking_helper(board, row + 1):
                    return True
                board[row] = -1
        return False

    def solve_genetic_algorithm(self):
        self.clear_board()
        population_size = 100
        mutation_rate = 0.1
        generations = 1000

        population = [self.random_chromosome() for _ in range(population_size)]

        start_time = time.time()
        for generation in range(generations):
            population = sorted(population, key=lambda x: self.fitness(x), reverse=True)
            best_fitness = self.fitness(population[0])

            print(f"Generation {generation + 1}: Best Fitness = {best_fitness}")

            self.progress['value'] = (generation / generations) * 100
            self.root.update_idletasks()

            if best_fitness == 28:
                end_time = time.time()
                self.display_solution(population[0])
                print(f"Solution found in generation {generation + 1}")
                print(f"Time taken: {end_time - start_time:.4f} seconds")
                messagebox.showinfo("Success", f"Solution found in generation {generation + 1}!")
                return

            next_generation = population[:10]
            for _ in range(population_size - 10):
                parent1, parent2 = random.sample(population[:50], 2)
                child = self.crossover(parent1, parent2)
                if random.random() < mutation_rate:
                    child = self.mutate(child)
                next_generation.append(child)

            population = next_generation

        end_time = time.time()
        self.display_solution(population[0])
        print(f"Best solution found: {self.fitness(population[0])} non-attacking pairs")
        print(f"Time taken: {end_time - start_time:.4f} seconds")
        messagebox.showinfo("Partial Solution",
                            f"Best solution found: {self.fitness(population[0])} non-attacking pairs")

    def random_chromosome(self):
        return random.sample(range(self.board_size), self.board_size)

    def fitness(self, chromosome):
        return sum(1 for i in range(len(chromosome))
                   for j in range(i + 1, len(chromosome))
                   if chromosome[i] != chromosome[j] and
                   abs(chromosome[i] - chromosome[j]) != j - i)

    def crossover(self, parent1, parent2):
        cross_point = random.randint(1, self.board_size - 1)
        child = parent1[:cross_point]
        child.extend(gene for gene in parent2 if gene not in child)
        return child

    def mutate(self, chromosome):
        i, j = random.sample(range(self.board_size), 2)
        chromosome[i], chromosome[j] = chromosome[j], chromosome[i]
        return chromosome

    def clear_board(self):
        self.draw_board()
        self.progress['value'] = 0


if __name__ == "__main__":
    root = tk.Tk()
    app = EightQueensGUI(root)
    root.mainloop()
