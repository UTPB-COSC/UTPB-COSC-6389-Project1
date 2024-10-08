import random
import math
from collections import deque


class Candidate:
    def __init__(self, chromosome, fitness=0.0):
        """
        Initialize a Candidate object.

        :param chromosome: A list of integers representing a candidate solution.
        """
        self.chromosome = chromosome  # List of integers representing the solution
        self.fitness = fitness

    def calculate_fitness(self, fitness_function):
        """
        Calculates and updates the fitness value for this candidate.

        :param fitness_function: A function that takes a chromosome and returns a fitness value.
        """
        self.fitness = fitness_function(self.chromosome)


def get_random_population(pop_size=20, gene_size=50):
    # Generate a list of pop_size candidates
    population = []

    for _ in range(pop_size):
        # Generate a chromosome with gene_size random integers between 0 and 100
        chromosome = [random.randint(0, 100) for _ in range(gene_size)]
        # Create a Candidate object with the random chromosome and random fitness in the range (0.0, 1.0)
        candidate = Candidate(chromosome, random.uniform(0.0, 1.0))
        # Add to the list of candidates
        population.append(candidate)

    # Print out each candidate's chromosome and fitness
    for idx, candidate in enumerate(population):
        print(f"Candidate {idx + 1}: Chromosome = {candidate.chromosome[:5]}..., Fitness = {candidate.fitness:.4f}")


def hill_climb(candidate, fitness_function, max_iterations=1000):
    """
    Performs Hill Climbing on the given Candidate object.

    :param candidate: The initial Candidate object.
    :param fitness_function: A function that evaluates and returns the fitness of a chromosome.
    :param max_iterations: The maximum number of iterations to perform.
    :return: The best Candidate found.

    Explanation:
        Initial Evaluation:
            The fitness of the initial candidate is calculated using the provided fitness function.
        Neighbor Generation:
            At each iteration, the algorithm creates a neighbor by modifying one random element in the chromosome.
        Fitness Comparison:
            If the new neighbor has a better fitness than the current candidate, the algorithm moves to the neighbor (i.e., updates the candidate).
        Termination:
            The function performs a specified number of iterations (max_iterations) or until no better solutions can be found.
        Return:
            After reaching the maximum iterations, it returns the best candidate found.
    """
    # Evaluate the initial candidate's fitness
    candidate.calculate_fitness(fitness_function)

    for iteration in range(max_iterations):
        # Create a neighbor by modifying one element in the chromosome
        neighbor_chromosome = candidate.chromosome[:]
        index_to_modify = random.randint(0, len(neighbor_chromosome) - 1)

        # Change the selected gene (in this case by a small random value for the sake of simplicity)
        neighbor_chromosome[index_to_modify] = random.randint(0, 100)

        # Create a new candidate from the modified chromosome
        neighbor = Candidate(neighbor_chromosome)
        neighbor.calculate_fitness(fitness_function)

        # If the neighbor has better fitness, move to the neighbor
        if neighbor.fitness > candidate.fitness:
            candidate = neighbor

    return candidate


def test_HC():
    def example_fitness_function(chromosome):
        return sum(chromosome)

    # Initial candidate with a random chromosome
    initial_candidate = Candidate([random.randint(0, 100) for _ in range(50)])

    # Perform Hill Climbing on the initial candidate
    best_candidate = hill_climb(initial_candidate, example_fitness_function)

    # Output the best candidate's chromosome and fitness
    print(f"Best Chromosome: {best_candidate.chromosome}")
    print(f"Best Fitness: {best_candidate.fitness}")


def simulated_annealing(candidate, fitness_function, initial_temperature=1000, cooling_rate=0.003,
                        min_temperature=1e-5):
    """
    Performs Simulated Annealing on a given Candidate object.

    :param candidate: The initial Candidate object.
    :param fitness_function: A function that evaluates and returns the fitness of a chromosome.
    :param initial_temperature: Starting temperature for the annealing process.
    :param cooling_rate: Rate at which the temperature cools (typically a small positive value).
    :param min_temperature: The stopping temperature threshold for the process.
    :return: The best Candidate found.

    Explanation:
        Initial Setup:
            The function starts by calculating the fitness of the initial candidate and sets the temperature to initial_temperature.
        Neighbor Creation:
            In each iteration, a neighbor is generated by randomly modifying one gene in the chromosome (just like Hill Climbing).
        Acceptance Criteria:
            If the new candidate has a better fitness, it is accepted.
            If the new candidate has a worse fitness, it is accepted with a probability based on the current temperature. This is the key difference from Hill Climbing and helps avoid local maxima.
            The probability of accepting worse solutions decreases as the temperature decreases.
        Cooling Schedule:
            After each iteration, the temperature is reduced by multiplying it by (1 - cooling_rate), slowly "cooling" the system.
        Termination:
            The process stops when the temperature falls below min_temperature, returning the best solution found.
    """
    # Calculate the initial candidate's fitness
    candidate.calculate_fitness(fitness_function)
    current_temperature = initial_temperature

    # Keep track of the best solution found
    best_candidate = candidate

    while current_temperature > min_temperature:
        # Create a neighbor by modifying one element in the chromosome
        neighbor_chromosome = candidate.chromosome[:]
        index_to_modify = random.randint(0, len(neighbor_chromosome) - 1)

        # Change the selected gene by a small random value
        neighbor_chromosome[index_to_modify] = random.randint(0, 100)

        # Create a new Candidate from the modified chromosome
        neighbor = Candidate(neighbor_chromosome)
        neighbor.calculate_fitness(fitness_function)

        # Calculate the difference in fitness
        fitness_diff = neighbor.fitness - candidate.fitness

        # Decide whether to move to the new candidate
        if fitness_diff > 0 or random.random() < math.exp(fitness_diff / current_temperature):
            candidate = neighbor

            # Update the best candidate found if this one is better
            if neighbor.fitness > best_candidate.fitness:
                best_candidate = neighbor

        # Cool the system
        current_temperature *= (1 - cooling_rate)

    return best_candidate


def test_SA():
    # Example fitness function: sum of chromosome values
    def example_fitness_function(chromosome):
        return sum(chromosome)

    # Initial candidate with a random chromosome
    initial_candidate = Candidate([random.randint(0, 100) for _ in range(50)])

    # Perform Simulated Annealing on the initial candidate
    best_candidate = simulated_annealing(initial_candidate, example_fitness_function)

    # Output the best candidate's chromosome and fitness
    print(f"Best Chromosome: {best_candidate.chromosome}")
    print(f"Best Fitness: {best_candidate.fitness}")


def tabu_search(initial_candidate, fitness_function, tabu_list_size=10, max_iterations=100, neighborhood_size=10):
    """
    Performs Tabu Search on a given Candidate object.

    :param initial_candidate: The initial Candidate object.
    :param fitness_function: A function that evaluates and returns the fitness of a chromosome.
    :param tabu_list_size: The maximum size of the Tabu List.
    :param max_iterations: The maximum number of iterations to perform.
    :param neighborhood_size: The number of neighbors to explore in each iteration.
    :return: The best Candidate found.

    Explanation:
        Initial Setup:
            The fitness of the initial candidate is calculated using the provided fitness_function.
            The initial candidate is set as both the current_candidate and best_candidate.
            A Tabu List is initialized using deque with a maximum size (tabu_list_size), ensuring that old solutions are removed as new ones are added.
        Neighborhood Generation:
            In each iteration, a neighborhood of candidates is generated by randomly modifying one gene in the chromosome.
            Each neighbor's fitness is calculated, and they are added to the neighborhood list.
        Tabu List and Aspiration Criteria:
            The best candidate from the neighborhood that is not in the Tabu List (or meets the aspiration criteria by having a fitness better than the best overall solution) is selected as the best_neighbor.
            This allows Tabu Search to avoid revisiting recently explored solutions while considering moving to better ones.
        Update:
            If the best_neighbor is better than the current candidate, it replaces the current candidate.
            If it also improves upon the best candidate found so far, it is updated as the best_candidate.
            The chromosome of the current candidate is added to the Tabu List.
        Termination:
            The search stops after a given number of iterations (max_iterations), and the best candidate found is returned.
    """
    # Calculate the fitness of the initial candidate
    initial_candidate.calculate_fitness(fitness_function)

    # Initialize the current candidate and best candidate as the initial candidate
    current_candidate = initial_candidate
    best_candidate = initial_candidate

    # Initialize an empty Tabu List
    tabu_list = deque(maxlen=tabu_list_size)

    # Add the initial candidate's chromosome to the Tabu List
    tabu_list.append(tuple(current_candidate.chromosome))

    # Iterate through the search process
    for iteration in range(max_iterations):
        # Generate a neighborhood of candidates
        neighborhood = []
        for _ in range(neighborhood_size):
            # Create a neighbor by modifying one random gene in the chromosome
            neighbor_chromosome = current_candidate.chromosome[:]
            index_to_modify = random.randint(0, len(neighbor_chromosome) - 1)
            neighbor_chromosome[index_to_modify] = random.randint(0, 100)

            # Create a new candidate from the modified chromosome
            neighbor = Candidate(neighbor_chromosome)
            neighbor.calculate_fitness(fitness_function)

            # Add the neighbor to the neighborhood
            neighborhood.append(neighbor)

        # Find the best neighbor that is not in the Tabu List or meets aspiration criteria
        best_neighbor = None
        for neighbor in neighborhood:
            if tuple(neighbor.chromosome) not in tabu_list or neighbor.fitness > best_candidate.fitness:
                if best_neighbor is None or neighbor.fitness > best_neighbor.fitness:
                    best_neighbor = neighbor

        # If a better solution is found, update the current and best candidates
        if best_neighbor and best_neighbor.fitness > current_candidate.fitness:
            current_candidate = best_neighbor
            if best_neighbor.fitness > best_candidate.fitness:
                best_candidate = best_neighbor

        # Add the current candidate's chromosome to the Tabu List
        tabu_list.append(tuple(current_candidate.chromosome))

    return best_candidate


def test_TS():
    # Example fitness function: sum of chromosome values
    def example_fitness_function(chromosome):
        return sum(chromosome)

    # Initial candidate with a random chromosome
    initial_candidate = Candidate([random.randint(0, 100) for _ in range(50)])

    # Perform Tabu Search on the initial candidate
    best_candidate = tabu_search(initial_candidate, example_fitness_function)

    # Output the best candidate's chromosome and fitness
    print(f"Best Chromosome: {best_candidate.chromosome}")
    print(f"Best Fitness: {best_candidate.fitness}")


def roulette_wheel_selection(generation):
    """
    Perform Roulette Wheel Selection.

    :param generation: List of Candidate objects.
    :return: A tuple of two selected parents.
    """
    # Calculate the total fitness of the generation
    total_fitness = sum(candidate.fitness for candidate in generation)

    # Create a helper function to perform roulette wheel selection once
    def select_one():
        pick = random.uniform(0, total_fitness)
        current = 0
        for candidate in generation:
            current += candidate.fitness
            if current > pick:
                return candidate

    # Select two parents
    parent1 = select_one()
    parent2 = select_one()
    while parent2 == parent1:
        parent2 = select_one()

    return parent1, parent2


def rank_based_selection(generation):
    """
    Perform Rank-Based Selection.

    :param generation: List of Candidate objects.
    :return: A tuple of two selected parents.
    """
    # Rank the generation by fitness
    ranked_generation = sorted(generation, key=lambda c: c.fitness)

    # Assign selection probabilities based on rank
    total_ranks = sum(range(1, len(ranked_generation) + 1))

    def select_one():
        pick = random.uniform(0, total_ranks)
        current = 0
        for i, candidate in enumerate(ranked_generation):
            current += (i + 1)  # rank is 1-based
            if current > pick:
                return candidate

    # Select two parents
    parent1 = select_one()
    parent2 = select_one()

    return parent1, parent2


def tournament_selection(generation, tournament_size=3):
    """
    Perform Tournament Selection.

    :param generation: List of Candidate objects.
    :param tournament_size: Size of the tournament.
    :return: A tuple of two selected parents.
    """

    def select_one():
        # Randomly select k candidates for the tournament
        tournament = random.sample(generation, tournament_size)
        # Return the best candidate from the tournament
        return max(tournament, key=lambda candidate: candidate.fitness)

    # Select two parents
    parent1 = select_one()
    parent2 = select_one()

    return parent1, parent2


def stochastic_universal_sampling(generation, num_parents=2):
    """
    Perform Stochastic Universal Sampling.

    :param generation: List of Candidate objects.
    :param num_parents: Number of parents to select.
    :return: A tuple of two selected parents.
    """
    total_fitness = sum(candidate.fitness for candidate in generation)
    pointer_spacing = total_fitness / num_parents
    start_point = random.uniform(0, pointer_spacing)

    parents = []
    current_point = start_point
    cumulative_fitness = 0

    for candidate in generation:
        cumulative_fitness += candidate.fitness
        while cumulative_fitness > current_point and len(parents) < num_parents:
            parents.append(candidate)
            current_point += pointer_spacing

    return parents[0], parents[1] #random.sample(parents, 2)


def truncation_selection(generation, truncation_percentage=0.5):
    """
    Perform Truncation Selection.

    :param generation: List of Candidate objects.
    :param truncation_percentage: Fraction of top candidates to select from.
    :return: A tuple of two selected parents.
    """
    # Sort the generation by fitness
    sorted_generation = sorted(generation, key=lambda c: c.fitness, reverse=True)

    # Select the top percentage
    truncation_size = int(truncation_percentage * len(generation))
    truncated_generation = sorted_generation[:truncation_size]

    # Randomly select two parents from the truncated group
    parent1 = random.choice(truncated_generation)
    parent2 = random.choice(truncated_generation)
    while parent2 == parent1:
        parent2 = random.choice(truncated_generation)

    return parent1, parent2


def elitism_selection(generation, elite_fraction=0.1):
    """
    Perform Elitism Selection, carrying over the best individuals to the next generation.

    :param generation: List of Candidate objects.
    :param elite_fraction: Fraction of top candidates to retain.
    :return: A tuple of two selected elite parents.
    """
    # Sort the generation by fitness
    sorted_generation = sorted(generation, key=lambda c: c.fitness, reverse=True)

    # Select the top elite_fraction of candidates
    elite_size = max(1, int(elite_fraction * len(generation)))
    elite_candidates = sorted_generation[:elite_size]

    # Randomly select two parents from the elite candidates
    parent1 = random.choice(elite_candidates)
    parent2 = random.choice(elite_candidates)

    return parent1, parent2


def n_point_crossover(parent1, parent2, n_points=2):
    """
    Perform N-point Crossover.

    :param parent1: First parent (Candidate object).
    :param parent2: Second parent (Candidate object).
    :param n_points: Number of crossover points.
    :return: A new Candidate (offspring).
    """
    length = len(parent1.chromosome)
    crossover_points = sorted(random.sample(range(1, length), n_points))

    offspring_chromosome = []
    swap = False

    # Perform the crossover between points
    prev_point = 0
    for point in crossover_points + [length]:
        if swap:
            offspring_chromosome += parent2.chromosome[prev_point:point]
        else:
            offspring_chromosome += parent1.chromosome[prev_point:point]
        swap = not swap
        prev_point = point

    return Candidate(offspring_chromosome)


def uniform_crossover(parent1, parent2):
    """
    Perform Uniform Crossover.

    :param parent1: First parent (Candidate object).
    :param parent2: Second parent (Candidate object).
    :return: A new Candidate (offspring).
    """
    offspring_chromosome = [
        random.choice([gene1, gene2]) for gene1, gene2 in zip(parent1.chromosome, parent2.chromosome)
    ]
    return Candidate(offspring_chromosome)


def arithmetic_crossover(parent1, parent2, alpha=0.5):
    """
    Perform Arithmetic Crossover.

    :param parent1: First parent (Candidate object).
    :param parent2: Second parent (Candidate object).
    :param alpha: Weighting factor for averaging parent genes.
    :return: A new Candidate (offspring).
    """
    offspring_chromosome = [
        alpha * gene1 + (1 - alpha) * gene2 for gene1, gene2 in zip(parent1.chromosome, parent2.chromosome)
    ]
    return Candidate(offspring_chromosome)


def blend_crossover(parent1, parent2, alpha=0.5):
    """
    Perform Blend Crossover (BLX-α).

    :param parent1: First parent (Candidate object).
    :param parent2: Second parent (Candidate object).
    :param alpha: Alpha parameter controlling the range of exploration.
    :return: A new Candidate (offspring).
    """
    offspring_chromosome = []
    for gene1, gene2 in zip(parent1.chromosome, parent2.chromosome):
        d = abs(gene1 - gene2)
        lower_bound = min(gene1, gene2) - alpha * d
        upper_bound = max(gene1, gene2) + alpha * d
        offspring_chromosome.append(random.uniform(lower_bound, upper_bound))

    return Candidate(offspring_chromosome)


def cut_and_splice_crossover(parent1, parent2):
    """
    Perform Cut-and-Splice Crossover.

    :param parent1: First parent (Candidate object).
    :param parent2: Second parent (Candidate object).
    :return: A new Candidate (offspring) of variable length.
    """
    cut_point1 = random.randint(0, len(parent1.chromosome) - 1)
    cut_point2 = random.randint(0, len(parent2.chromosome) - 1)

    offspring_chromosome = parent1.chromosome[:cut_point1] + parent2.chromosome[cut_point2:]

    return Candidate(offspring_chromosome)


def order_crossover(parent1, parent2):
    """
    Perform Order Crossover (OX).

    :param parent1: First parent (Candidate object).
    :param parent2: Second parent (Candidate object).
    :return: A new Candidate (offspring) preserving the order.
    """
    length = len(parent1.chromosome)

    # Select a random segment from Parent 1
    start, end = sorted(random.sample(range(length), 2))
    offspring_chromosome = [None] * length
    offspring_chromosome[start:end] = parent1.chromosome[start:end]

    # Fill the remaining positions with Parent 2's genes in the same order
    parent2_genes = [gene for gene in parent2.chromosome if gene not in offspring_chromosome]

    idx = 0
    for i in range(length):
        if offspring_chromosome[i] is None:
            offspring_chromosome[i] = parent2_genes[idx]
            idx += 1

    return Candidate(offspring_chromosome)


def uniform_mutation(candidate, mutation_probability):
    """
    Perform Uniform Mutation on a Candidate.

    :param candidate: Candidate object whose chromosome will be mutated.
    :param mutation_probability: The probability that each gene will be mutated.
    :return: A new Candidate object after mutation.
    """
    offspring_chromosome = []

    for gene in candidate.chromosome:
        if random.random() < mutation_probability:
            # Mutate the gene (assuming genes are integers, this could be customized)
            new_gene = random.randint(0, 100)  # Adjust the range based on the problem
        else:
            new_gene = gene
        offspring_chromosome.append(new_gene)

    return Candidate(offspring_chromosome)


def multi_point_mutation(candidate, num_points=1):
    """
    Perform Multi-Point Mutation on a Candidate.

    :param candidate: Candidate object whose chromosome will be mutated.
    :param num_points: The number of genes to be mutated.
    :return: A new Candidate object after mutation.
    """
    offspring_chromosome = candidate.chromosome[:]

    # Select num_points unique genes for mutation
    mutation_indices = random.sample(range(len(offspring_chromosome)), num_points)

    for index in mutation_indices:
        # Mutate the selected gene (assuming genes are integers, this could be customized)
        offspring_chromosome[index] = random.randint(0, 100)  # Adjust the range based on the problem

    return Candidate(offspring_chromosome)


def gaussian_mutation(candidate, mean=0, stddev=1):
    """
    Perform Gaussian Mutation on a Candidate object.

    :param candidate: Candidate object whose chromosome will be mutated.
    :param mean: Mean of the Gaussian distribution.
    :param stddev: Standard deviation of the Gaussian distribution.
    :return: A new Candidate after mutation.
    """
    offspring_chromosome = [
        gene + random.gauss(mean, stddev) for gene in candidate.chromosome
    ]
    return Candidate(offspring_chromosome)


def boundary_mutation(candidate, lower_bound, upper_bound):
    """
    Perform Boundary Mutation by replacing a random gene with its upper or lower boundary.

    :param candidate: Candidate object whose chromosome will be mutated.
    :param lower_bound: Lower boundary for mutation.
    :param upper_bound: Upper boundary for mutation.
    :return: A new Candidate after mutation.
    """
    offspring_chromosome = candidate.chromosome[:]
    mutation_index = random.randint(0, len(offspring_chromosome) - 1)

    # Randomly set to lower or upper boundary
    if random.random() < 0.5:
        offspring_chromosome[mutation_index] = lower_bound
    else:
        offspring_chromosome[mutation_index] = upper_bound

    return Candidate(offspring_chromosome)


def swap_mutation(candidate):
    """
    Perform Swap Mutation by swapping two random genes in the chromosome.

    :param candidate: Candidate object whose chromosome will be mutated.
    :return: A new Candidate after mutation.
    """
    offspring_chromosome = candidate.chromosome[:]
    idx1, idx2 = random.sample(range(len(offspring_chromosome)), 2)

    # Swap the two genes
    offspring_chromosome[idx1], offspring_chromosome[idx2] = offspring_chromosome[idx2], offspring_chromosome[idx1]

    return Candidate(offspring_chromosome)


def scramble_mutation(candidate):
    """
    Perform Scramble Mutation by shuffling a random subset of the chromosome.

    :param candidate: Candidate object whose chromosome will be mutated.
    :return: A new Candidate after mutation.
    """
    offspring_chromosome = candidate.chromosome[:]

    # Select a random range to scramble
    start, end = sorted(random.sample(range(len(offspring_chromosome)), 2))
    scrambled_part = offspring_chromosome[start:end]

    random.shuffle(scrambled_part)

    offspring_chromosome[start:end] = scrambled_part

    return Candidate(offspring_chromosome)


def inversion_mutation(candidate):
    """
    Perform Inversion Mutation by reversing the order of a random subset of the chromosome.

    :param candidate: Candidate object whose chromosome will be mutated.
    :return: A new Candidate after mutation.
    """
    offspring_chromosome = candidate.chromosome[:]

    # Select a random range to invert
    start, end = sorted(random.sample(range(len(offspring_chromosome)), 2))

    # Invert the selected range
    offspring_chromosome[start:end] = offspring_chromosome[start:end][::-1]

    return Candidate(offspring_chromosome)


def non_uniform_mutation(candidate, generation, max_generations, mutation_probability=0.1):
    """
    Perform Non-Uniform Mutation where the mutation effect decreases over time.

    :param candidate: Candidate object whose chromosome will be mutated.
    :param generation: Current generation (used to control mutation size).
    :param max_generations: Total number of generations (for scaling mutation).
    :param mutation_probability: Probability of mutation for each gene.
    :return: A new Candidate after mutation.
    """
    offspring_chromosome = []
    for gene in candidate.chromosome:
        if random.random() < mutation_probability:
            # Mutation magnitude decreases as generation increases
            delta = random.uniform(0, 1) * (1 - generation / max_generations)
            # Apply random positive or negative mutation
            new_gene = gene + random.choice([-1, 1]) * delta
            offspring_chromosome.append(new_gene)
        else:
            offspring_chromosome.append(gene)

    return Candidate(offspring_chromosome)


def adaptive_mutation(candidate, population, improvement_threshold=0.1, mutation_probability=0.1):
    """
    Perform Adaptive Mutation where the mutation probability is adjusted based on population stagnation.

    :param candidate: Candidate object whose chromosome will be mutated.
    :param population: Current population of candidates.
    :param improvement_threshold: Threshold for triggering increased mutation rate.
    :param mutation_probability: Base mutation probability.
    :return: A new Candidate after mutation.
    """
    # Calculate the average fitness of the population
    avg_fitness = sum([ind.fitness for ind in population]) / len(population)

    # If candidate fitness hasn't improved enough, increase mutation probability
    if candidate.fitness < avg_fitness * (1 + improvement_threshold):
        mutation_probability *= 2  # Increase mutation rate if no significant improvement

    offspring_chromosome = []
    for gene in candidate.chromosome:
        if random.random() < mutation_probability:
            # Mutate the gene
            new_gene = random.randint(0, 100)  # Assuming integer genes for now
        else:
            new_gene = gene
        offspring_chromosome.append(new_gene)

    return Candidate(offspring_chromosome)
