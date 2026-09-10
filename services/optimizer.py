# services/optimizer.py

from algorithms.robust_dp import robust_knapsack


def optimize_cargo(cargo_list, capacity, gamma):
    """
    Run the Robust Knapsack optimization.
    """

    return robust_knapsack(
        cargo_list,
        capacity,
        gamma
    )