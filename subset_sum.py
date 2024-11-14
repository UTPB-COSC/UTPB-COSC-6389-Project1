from typing import List, Optional


class SubsetSumSolver:
    def __init__(self, items: List[int], target_sum: int):
        """
        A class to solve the subset sum problem using dynamic programming.
        Given a list of items and a target sum, it determines if there is a
        subset of items tha adds up to the target sum.
        """
        self.items = items
        self.target_sum = target_sum
        self.dp = []

    def solve(self) -> Optional[List[int]]:
        """
        Solves the subset sum problem using dynamic programming.

        :return: List of subset elements that sum to target_sum if possible,
                 otherwise None if no such subset exists.
        """
        # Initialize the DP table with base cases
        self._initialize_dp_table()

        # Populate the DP table using the subset sum logic
        for i in range(1, len(self.items) + 1):
            for j in range(1, self.target_sum + 1):
                # Case 1: Exclude the current item if its value is greater than the current target sum(j)
                if j < self.items[i - 1]:
                    self.dp[i][j] = self.dp[i - 1][j]
                else:
                    # Case 2: Include the current item if it helps reach the target sum
                    # Check if we can reach the target sum with or without the current item
                    self.dp[i][j] = self.dp[i - 1][j] or self.dp[i - 1][j - self.items[i - 1]]

        # Check if there's a solution in the last cell of the DP table
        if not self.dp[len(self.items)][self.target_sum]:
            return None # No subset found that adds up to the target sum

        # Traceback to find the items included in the subset
        return self._find_solution_items()

    def _initialize_dp_table(self) -> None:
        """
        Initializes the DP table with base cases
        DP table dp[i][j] will be True if a subset of the first i items can sum to j, otherwise False.

        Base case:
        - dp[i][0] is True for all i because a sum of 0 can always be achieved with an empty subset.
        """
        n = len(self.items)
        target = self.target_sum
        # Create a DP table with dimensions (n+1) x (target+1), initialized to False
        self.dp = [[False] * (target + 1) for _ in range(n + 1)]

        # Base case: a sum of 0 is always possible (with an empy subset)
        for i in range(n + 1):
            self.dp[i][0] = True

    def _find_solution_items(self) -> List[int]:
        """
        Traces back through the DP table to find the items that make up the target sum.

        :return: List of items that add up to the target sum, in original order.
        """
        solution_items = [] # List to store the items in the subset
        i, j = len(self.items), self.target_sum # Start from the bottom-right of the DP table

        # Trace back from dp[len(items)][target_sum] to identify which items are part of the solution
        while i > 0 and j > 0:
            # Check if the current item is included in the subset by verifying if excluding it changes the result
            if self.dp[i][j] and not self.dp[i - 1][j]: # Current item is included
                solution_items.append(self.items[i - 1]) # Add item to the solution
                j -= self.items[i - 1] # Reduce the remaining sum by the item's value
            i -= 1 # Move to the previous item

        # Reverse the list to return items in the order they appear in the original list
        return solution_items[::-1]

def main ():
    """
    Main function to demonstrate the subset sum problem solver
    Initializes the items list and target sum, then uses SubsetSumSolver to find a solution
    """
    items = [3, 4, 5, 6] # List of available items
    target_sum = 9 # Desired target sum

    # Initialize solver with items and target sum
    solver = SubsetSumSolver(items, target_sum)
    solution = solver.solve() # Find a subset that adds up to target_sum

    # Display the result
    if solution:
        print(f"Subset found that sum to {target_sum}: {solution} with sum {sum(solution)}")
    else:
        print(f"No subset found that sums to {target_sum}.")

# Entry point for the program
if __name__ == "__main__":
    main()
