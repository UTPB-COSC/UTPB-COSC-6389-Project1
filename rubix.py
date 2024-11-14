import tkinter as tk
import random
import copy
import math

CUBE_SIZE = 3  # 3x3 for standard Rubik's cube face


def generate_scrambled_face():
    colors = ["W", "R", "G", "B", "O", "Y"]
    return [[random.choice(colors) for _ in range(CUBE_SIZE)] for _ in range(CUBE_SIZE)]


def count_mismatched_tiles(face):
    target_color = face[0][0]
    return sum(tile != target_color for row in face for tile in row)


def mutate(face):
    new_face = copy.deepcopy(face)
    x, y = random.randint(0, CUBE_SIZE - 1), random.randint(0, CUBE_SIZE - 1)
    new_face[x][y] = random.choice(["W", "R", "G", "B", "O", "Y"])
    return new_face


def simulated_annealing(face, max_iterations=1000, initial_temp=1000, cooling_rate=0.99):
    best_face = copy.deepcopy(face)
    best_score = count_mismatched_tiles(best_face)
    temp = initial_temp

    for i in range(max_iterations):
        new_face = mutate(face)
        new_score = count_mismatched_tiles(new_face)

        if new_score < best_score or random.random() < math.exp((best_score - new_score) / temp):
            best_face, best_score = new_face, new_score

        temp *= cooling_rate
        print(f"SA Iteration {i + 1} | Temperature: {temp:.2f} | Best Fitness: {best_score}")

        if best_score == 0:
            break

    return best_face


def genetic_algorithm(face, population_size=10, generations=50):
    population = [mutate(face) for _ in range(population_size)]
    for generation in range(generations):
        scored_population = sorted([(count_mismatched_tiles(f), f) for f in population], key=lambda x: x[0])
        best_face = scored_population[0][1]
        best_score = scored_population[0][0]

        print(f"GA Generation {generation + 1} | Best Fitness: {best_score}")

        if best_score == 0:
            return best_face

        new_population = [scored_population[i][1] for i in range(population_size // 2)]
        while len(new_population) < population_size:
            parent1, parent2 = random.choices(new_population, k=2)
            child = mutate(crossover(parent1, parent2))
            new_population.append(child)

        population = new_population
    return best_face


def crossover(parent1, parent2):
    child = copy.deepcopy(parent1)
    for i in range(CUBE_SIZE):
        for j in range(CUBE_SIZE):
            if random.random() < 0.5:
                child[i][j] = parent2[i][j]
    return child


class CubeSolverApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rubik's Cube Solver - GA and SA")
        self.geometry("400x550")

        self.face = generate_scrambled_face()

        self.canvas = tk.Canvas(self, width=300, height=300, bg="black")
        self.canvas.pack(pady=20)
        self.info_label = tk.Label(self, text="Generate a new puzzle or choose an algorithm to solve", font=("Arial", 12))
        self.info_label.pack(pady=10)

        # Generate button
        self.generate_button = tk.Button(self, text="Generate New Puzzle", command=self.generate_new_puzzle)
        self.generate_button.pack(pady=5)

        # Buttons for Simulated Annealing and Genetic Algorithm
        self.sa_button = tk.Button(self, text="Solve with Simulated Annealing", command=self.solve_with_sa)
        self.sa_button.pack(pady=5)
        self.ga_button = tk.Button(self, text="Solve with Genetic Algorithm", command=self.solve_with_ga)
        self.ga_button.pack(pady=5)

        self.draw_face(self.face)

    def draw_face(self, face):
        self.canvas.delete("all")
        colors = {"W": "white", "R": "red", "G": "green", "B": "blue", "O": "orange", "Y": "yellow"}
        size = 300 // CUBE_SIZE
        for i in range(CUBE_SIZE):
            for j in range(CUBE_SIZE):
                color = colors.get(face[i][j], "gray")
                x1, y1 = j * size, i * size
                x2, y2 = x1 + size, y1 + size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def generate_new_puzzle(self):
        self.face = generate_scrambled_face()
        self.draw_face(self.face)
        self.info_label.config(text="New puzzle generated. Choose an algorithm to solve.")

    def solve_with_sa(self):
        self.info_label.config(text="Solving with Simulated Annealing...")
        self.update()
        self.face = simulated_annealing(self.face)
        self.info_label.config(text="Simulated Annealing Solution Complete!")
        self.draw_face(self.face)

    def solve_with_ga(self):
        self.info_label.config(text="Solving with Genetic Algorithm...")
        self.update()
        self.face = genetic_algorithm(self.face)
        self.info_label.config(text="Genetic Algorithm Solution Complete!")
        self.draw_face(self.face)


if __name__ == "__main__":
    app = CubeSolverApp()
    app.mainloop()
