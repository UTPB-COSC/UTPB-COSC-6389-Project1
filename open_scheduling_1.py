import tkinter as tk
from tkinter import messagebox
import random
import matplotlib.pyplot as plt
import random

def calculate_completion_time(schedule, processing_times):
    completion_times = [0] * len(processing_times[0])
    for task in schedule:
        for machine in range(len(processing_times[0])):
            completion_times[machine] += processing_times[task][machine]
    makespan = max(completion_times)
    return makespan, completion_times

def crossover(parent1, parent2):
    start, end = sorted(random.sample(range(len(parent1)), 2))
    child = [-1] * len(parent1)
    child[start:end] = parent1[start:end]
    pointer = end
    for task in parent2:
        if task not in child:
            if pointer == len(child):
                pointer = 0
            child[pointer] = task
            pointer += 1
    return child

def mutate(schedule):
    if random.random() < 0.5:
        start, end = sorted(random.sample(range(len(schedule)), 2))
        schedule[start:end+1] = reversed(schedule[start:end+1])
    else:
        random.shuffle(schedule)
    return schedule

def update_grid():

    for widget in inner_grid_frame.winfo_children():
        widget.destroy()

    global entry_vars
    entry_vars = [[tk.StringVar(value="0") for _ in range(machines)] for _ in range(tasks)]

    for i in range(tasks):
        tk.Label(inner_grid_frame, text=f"Task {i+1}").grid(row=i + 1, column=0, padx=5, pady=5)
        for j in range(machines):
            entry = tk.Entry(inner_grid_frame, textvariable=entry_vars[i][j], width=5)
            entry.grid(row=i + 1, column=j + 1, padx=5, pady=5)
    for j in range(machines):
        tk.Label(inner_grid_frame, text=f"Machine {j+1}").grid(row=0, column=j + 1, padx=5, pady=5)

    inner_grid_frame.update_idletasks()
    grid_canvas.config(scrollregion=grid_canvas.bbox("all"))

def update_dimensions():

    global tasks, machines
    try:
        tasks = int(task_var.get())
        machines = int(machine_var.get())
        update_grid()
    except ValueError:
        messagebox.showerror("Error", "Please enter valid integers for tasks and machines")

def generate_random_times_callback():
    try:
        num_tasks = int(task_var.get())
        num_machines = int(machine_var.get())
        pattern = pattern_var.get()
        processing_times = generate_processing_times(num_tasks, num_machines, pattern)

        for i in range(num_tasks):
            for j in range(num_machines):
                entry_vars[i][j].set(str(processing_times[i][j]))

    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for tasks and machines.")
      
def generate_processing_times(num_tasks, num_machines, pattern = "uniform"):
    if pattern == "biased":
        return [[random.randint(10, 50) if machine % 2 == 0 else random.randint(30, 70)
                 for machine in range(num_machines)] for task in range(num_tasks)]
    elif pattern == "hierarchical":
        return [[random.randint(50, 100) if task % 3 == 0 else random.randint(10, 40)
                 for machine in range(num_machines)] for task in range(num_tasks)]
    else:  # Default: uniform
        return [[random.randint(10, 100) for _ in range(num_machines)] for _ in range(num_tasks)]

def generate_biased_processing_times(num_tasks, num_machines):
    return [[random.randint(10, 50) if machine % 2 == 0 else random.randint(30, 70)
             for machine in range(num_machines)] for task in range(num_tasks)]

def generate_uniform_processing_times(num_tasks, num_machines):
    return [[random.randint(10, 100) for _ in range(num_machines)] for _ in range(num_tasks)]

def generate_hierarchical_processing_times(num_tasks, num_machines):
    return [[random.randint(50, 100) if task % 3 == 0 else random.randint(10, 40)
             for machine in range(num_machines)] for task in range(num_tasks)]

def initialize_population(num_tasks, population_size):
    population = []
    for _ in range(population_size):
        population.append(random.sample(range(num_tasks), num_tasks))
    return population

def genetic_algorithm_with_visualization(processing_times, population_size=20, generations=50):
    num_tasks = len(processing_times)
    population = initialize_population(num_tasks, population_size)
    best_fitness_per_generation = []

    for gen in range(generations):
        population = sorted(population, key=lambda x: calculate_completion_time(x, processing_times)[0])
        best_schedule = population[0]
        min_time, completion_times = calculate_completion_time(best_schedule, processing_times)
        best_fitness_per_generation.append(min_time)

        next_population = population[:5]
        while len(next_population) < population_size:
            parent1 = tournament_selection(population, processing_times)
            parent2 = tournament_selection(population, processing_times)
            child = crossover(parent1, parent2)
            if random.random() < 0.8:
                child = mutate(child)

            if len(set(child)) == num_tasks:
                next_population.append(child)

        population = next_population

        if gen > 10 and best_fitness_per_generation[-1] == best_fitness_per_generation[-10]:
            top_individuals = population[:5]
            new_individuals = [random.sample(range(num_tasks), num_tasks) for _ in range(population_size - len(top_individuals))]
            population = top_individuals + new_individuals

    return best_schedule, min_time, completion_times

def rank_selection(population, processing_times):
    ranked_population = sorted(population, key=lambda x: calculate_completion_time(x, processing_times))
    probabilities = [1 / (rank + 1) for rank in range(len(ranked_population))]
    total = sum(probabilities)
    probabilities = [p / total for p in probabilities]
    selected_idx = random.choices(range(len(ranked_population)), weights=probabilities, k=1)[0]
    return ranked_population[selected_idx]

def local_search(schedule, processing_times):
    best_schedule = schedule[:]
    best_fitness = calculate_completion_time(best_schedule, processing_times)
    for i in range(len(schedule)):
        for j in range(i + 1, len(schedule)):
            neighbor = best_schedule[:]
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            fitness = calculate_completion_time(neighbor, processing_times)
            if fitness < best_fitness:
                best_fitness = fitness
                best_schedule = neighbor
    return best_schedule

def tournament_selection(population, processing_times, k=3):
    tournament = random.sample(population, k)
    return min(tournament, key=lambda x: calculate_completion_time(x, processing_times))

def roulette_wheel_selection(population, processing_times):
    fitness_scores = [1 / calculate_completion_time(ind, processing_times)[0] for ind in population]
    total_fitness = sum(fitness_scores)
    probabilities = [score / total_fitness for score in fitness_scores]
    selected_idx = random.choices(range(len(population)), weights=probabilities, k=1)[0]
    return population[selected_idx]

def generate_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def draw_schedule(canvas, schedule, processing_times, min_time, completion_times):
    # Draw GA schedule on the canvas as a Gantt chart
    canvas.delete("all")

    selected_type = scheduling_type.get()
    time_unit = "minutes" if selected_type == "Manufacturing" else "seconds"

    num_machines = len(processing_times[0])
    task_height = 30
    machine_gap = 60
    time_scale = 5
    label_offset = 70

    max_time = max(completion_times)

    time_scale = max(800 / max_time, 5)
    canvas_height = num_machines * (task_height + machine_gap) + 100
    
    #canvas.config(height=canvas_height, width=800)
    canvas.config(scrollregion=(0, 0, max_time * time_scale + 150, canvas_height))

    # Random colors to each task
    task_colors = {task_idx: generate_random_color() for task_idx in range(len(processing_times))}

    result_text = (
        f"Best Schedule: {', '.join(f'T{task + 1}' for task in schedule)}\n"
        f"Minimum Completion Time (Makespan): {min_time} {time_unit}\n"
    )

    canvas.create_text(
        10, 10,
        anchor="nw",
        text=result_text,
        font=("Arial", 12, "bold"),
        fill="black",
    )

    # Draw each machine
    for machine_idx in range(num_machines):
        y_start = machine_idx * machine_gap + 100
        x_position = 0
        canvas.create_text(
            label_offset - 60,
            y_start + task_height / 2,
            text=f"Machine {machine_idx + 1}",
            anchor="w",
            font=("Arial", 10, "bold"),
        )

        # Draw tasks on each machine
        for task_idx in schedule:
            task_duration = processing_times[task_idx][machine_idx]
            color = task_colors[task_idx]

            # Rectangle for the task
            canvas.create_rectangle(
                100 + x_position * time_scale,
                y_start,
                100 + (x_position + task_duration) * time_scale,
                y_start + task_height,
                fill=color,
                outline="black",
            )

            # Label tarea
            canvas.create_text(
                100 + (x_position + task_duration / 2) * time_scale,
                y_start + task_height / 2,
                text=f"T{task_idx + 1}",
                fill="white",
                font=("Arial", 10, "bold"),
            )

            x_position += task_duration

    update_scroll_region()
    
def run_algorithm_with_gantt_chart():
    # Run GA and visualize the schedule on the canvas
    try:
        processing_times = []
        for i in range(tasks):
            row = []
            for j in range(machines):
                value = entry_vars[i][j].get().strip()
                if not value.isdigit():
                    raise ValueError(f"Invalid value in Task {i + 1}, Machine {j + 1}: '{value}'")
                row.append(int(value))
            processing_times.append(row)

        # Run GA
        best_schedule, min_time, completion_times = genetic_algorithm_with_visualization(
            processing_times, population_size=100, generations=100
        )

        # Convert schedule to 1-based indexing for user readability
        user_friendly_schedule = [task + 1 for task in best_schedule]

        # Gantt chart
        draw_schedule(canvas, best_schedule, processing_times, min_time, completion_times)

        result_text = (
            f"Best Schedule (1-based): {user_friendly_schedule}\n"
            f"Minimum Completion Time: {min_time}\n"
            f"Completion Times per Machine: {completion_times}"
        )
        #messagebox.showinfo("Results", result_text)

    except ValueError as ve:
        messagebox.showerror("Error", f"Input Error: {ve}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

def show_startup_message():
    messagebox.showinfo(
        "Welcome to Open-Shop Scheduling Solver",
        (
            "In this problem, there are multiple tasks that need to be processed on multiple machines\n"
            "Each task has a specific processing time for each machine.\n"
            "The goal is to find an optimal schedule that minimizes the total completion time.\n\n"
            "This problem has practical applications in manufacturing, computational workflows, and project management.\n\n"
            "This application uses a Genetic Algorithm to find a near-optimal solution efficiently.\n\n"
            "You can input the number of tasks and machines, specify processing times, "
            "and visualize the scheduling results and makespan."
        )
    )

def update_scroll_region():
    canvas.update_idletasks()  # Ensure the canvas is updated
    canvas.config(scrollregion=canvas.bbox("all"))  # Update scrollable region

# def plot_fitness_progress(fitness_per_generation):
#     plt.plot(fitness_per_generation, label="Best Fitness per Generation")
#     plt.xlabel("Generation")
#     plt.ylabel("Makespan")
#     plt.title("Genetic Algorithm Fitness Progress")
#     plt.legend()
#     plt.show()

root = tk.Tk()
root.title("Open-Shop Scheduling Solver")

tk.Label(root, text="Number of Tasks:").grid(row=0, column=0, sticky="e")
tk.Label(root, text="Number of Machines:").grid(row=1, column=0, sticky="e")

task_var = tk.StringVar(value="3")
machine_var = tk.StringVar(value="3")

tk.Entry(root, textvariable=task_var).grid(row=0, column=1)
tk.Entry(root, textvariable=machine_var).grid(row=1, column=1)
tk.Button(root, text="Update Grid", command=update_dimensions).grid(row=2, columnspan=2)

grid_frame = tk.Frame(root)
grid_frame.grid(row=3, columnspan=2, pady=10)

pattern_var = tk.StringVar(value="uniform")
tk.Label(root, text="Pattern for Random Times:").grid(row=4, column=0, sticky="e")
tk.OptionMenu(root, pattern_var, "uniform", "biased", "hierarchical").grid(row=4, column=1, sticky="w")

tk.Button(root, text="Generate Random Times", command=generate_random_times_callback).grid(row=5, columnspan=1, pady=10)

tk.Button(root, text="Run Algorithm", command=run_algorithm_with_gantt_chart).grid(row=5, columnspan=2, pady=10)

scheduling_type = tk.StringVar(value="Manufacturing")

tk.Label(root, text="Scheduling Type:").grid(row=0, column=0, sticky="w", padx=5)
tk.Radiobutton(root, text="Manufacturing", variable=scheduling_type, value="Manufacturing").grid(row=1, column=0, sticky="w", padx=5)
tk.Radiobutton(root, text="Computational", variable=scheduling_type, value="Computational").grid(row=2, column=0, sticky="w", padx=5)

scroll_frame = tk.Frame(root)
scroll_frame.grid(row=6, columnspan=2, pady=10)

canvas = tk.Canvas(scroll_frame, bg="white", height=300, width=800, scrollregion=(0, 0, 2000, 1000))

h_scrollbar = tk.Scrollbar(scroll_frame, orient="horizontal", command=canvas.xview)
v_scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)

canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
canvas.grid(row=0, column=0, sticky="nsew")
h_scrollbar.grid(row=1, column=0, sticky="ew")
v_scrollbar.grid(row=0, column=1, sticky="ns")

grid_canvas = tk.Canvas(grid_frame, height=200, width=400)
grid_scrollbar_y = tk.Scrollbar(grid_frame, orient="vertical", command=grid_canvas.yview)
grid_scrollbar_x = tk.Scrollbar(grid_frame, orient="horizontal", command=grid_canvas.xview)

inner_grid_frame = tk.Frame(grid_canvas)

grid_canvas.configure(yscrollcommand=grid_scrollbar_y.set, xscrollcommand=grid_scrollbar_x.set)

grid_scrollbar_y.pack(side="right", fill="y")
grid_scrollbar_x.pack(side="bottom", fill="x")
grid_canvas.pack(side="left", fill="both", expand=True)

grid_canvas.create_window((0, 0), window=inner_grid_frame, anchor="nw")

# Initialize grid
tasks = int(task_var.get())
machines = int(machine_var.get())
update_grid()

root.after(100, show_startup_message)
root.mainloop()
