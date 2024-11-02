import tkinter as tk
from tkinter import messagebox
import random

def calculate_completion_time(schedule, processing_times): # calculate the completion time of a given schedule
    completion_times = [0] * len(processing_times[0]) # initialize completion times for each machine
    for task in schedule:
        for machine in range(len(processing_times[0])):
            completion_times[machine] += processing_times[task][machine] # accumulate processing times for each machine based on the schedule
    return max(completion_times), completion_times

def is_valid_schedule(schedule):
    return len(schedule) == len(set(schedule))  # valid schedule should have unique tasks

def mutate(schedule): # Mutate schedule by swapping two tasks
    while True:
        new_schedule = schedule[:]  
        idx1, idx2 = random.sample(range(len(schedule)), 2)
        new_schedule[idx1], new_schedule[idx2] = new_schedule[idx2], new_schedule[idx1]  # swap tasks
        if is_valid_schedule(new_schedule):
            return new_schedule  # Return valid schedule

def crossover(schedule1, schedule2): #crossover two schedules to get a new one
    while True:
        cut = random.randint(1, len(schedule1) - 1) 
        new_schedule = schedule1[:cut] + schedule2[cut:]  # combine parts of both schedules
        if is_valid_schedule(new_schedule):
            return new_schedule

def g_a(processing_times, population_size=100, generations=100): #genetic algorithm to optimize scheduling
    population = [random.sample(range(len(processing_times)), len(processing_times)) for _ in range(population_size)] #random schedules
    
    for _ in range(generations):
        population.sort(key=lambda x: calculate_completion_time(x, processing_times)[0])
        new_population = population[:10]

        while len(new_population) < population_size: #new population from crossover and mutation
            if random.random() < 0.7: # 70% chance to crossover
                parent1, parent2 = random.sample(population[:50], 2)  # select two parents from the top 50
                child = crossover(parent1, parent2)
            else:
                child = random.choice(population)

            if random.random() < 0.1: # 10% chance to mutate the child
                child = mutate(child)
            
            new_population.append(child)

        population = new_population

    best_schedule = min(population, key=lambda x: calculate_completion_time(x, processing_times)[0])
    if not is_valid_schedule(best_schedule):
        raise ValueError("The best schedule is invalid.")
    min_time, completion_times = calculate_completion_time(best_schedule, processing_times)
    
    return best_schedule, min_time, completion_times

def run_algorithm():
    processing_times = [
        [int(entry_vars[i][j].get()) for j in range(3)] for i in range(3)] # read processing times from user input

    best_schedule, min_time, completion_times = g_a(processing_times) #execute genetic algorithm

    result_text = f"Best schedule: {best_schedule}\nMinimum completion time: {min_time}\nCompletion times per machine: {completion_times}"
    messagebox.showinfo("Result", result_text)

# Create GUI
root = tk.Tk()
root.title("Open-Shop Scheduling")

tk.Label(root, text="Processing times (3 tasks, 3 machines):").grid(row=0, column=0, columnspan=3)

entry_vars = [[tk.StringVar() for _ in range(3)] for _ in range(3)] # input fields for processing times
for i in range(3):
    for j in range(3):
        entry = tk.Entry(root, textvariable=entry_vars[i][j]) # create an entry for each time
        entry.grid(row=i + 1, column=j)

tk.Button(root, text="Run", command=run_algorithm).grid(row=4, columnspan=3)

root.mainloop()
