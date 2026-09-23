# services/optimizer.py

import time

from algorithms.robust_dp import robust_knapsack
from algorithms.recursive_partitioning import recursive_partitioning
from algorithms.bsmilp import bsmilp
from algorithms.llpp import llpp
from algorithms.branch_and_cut import branch_and_cut
from algorithms.fptas import fptas
from algorithms.dominance_lifting_2026 import (
    dominance_list_knapsack,
)


def optimize_cargo(
    cargo_list,
    capacity,
    gamma,
    algorithm="Robust DP",
    epsilon=0.2
):
    """
    Run one of the cargo optimization algorithms.
    """

    start_time = time.perf_counter()

    if algorithm == "Robust DP":

        result = robust_knapsack(
            cargo_list,
            capacity,
            gamma
        )

    elif algorithm == "Recursive Partitioning":

        result = recursive_partitioning(
            cargo_list,
            capacity,
            gamma
        )

    elif algorithm == "BSMILP":

        result = bsmilp(
            cargo_list,
            capacity,
            gamma
        )

    elif algorithm == "LLPP":

        result = llpp(
            cargo_list,
            capacity,
            gamma
        )

    elif algorithm == "Branch-and-Cut":

        result = branch_and_cut(
            cargo_list,
            capacity,
            gamma
        )

    elif algorithm == "FPTAS 2013":

        result = fptas(
            cargo_list,
            capacity,
            gamma,
            epsilon
        )

    elif algorithm == "Dominance-List DP 2026":

        weights = [
            cargo.weight
            for cargo in cargo_list
        ]

        profits = [
            cargo.profit
            for cargo in cargo_list
        ]

        result = dominance_list_knapsack(
            weights=weights,
            profits=profits,
            capacity=capacity
        )

        # Convert the selected item indices
        # into the original Cargo objects.
        result["selected_items"] = [
            cargo_list[index]
            for index in result["selected_indices"]
        ]

    else:

        raise ValueError(
            f"Unknown cargo optimization algorithm: {algorithm}"
        )

    end_time = time.perf_counter()

    result["runtime"] = (
        end_time - start_time
    )

    return result