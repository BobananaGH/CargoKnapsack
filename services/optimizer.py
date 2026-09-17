# services/optimizer.py

import time

from algorithms.robust_dp import robust_knapsack
from algorithms.recursive_partitioning import recursive_partitioning
from algorithms.bsmilp import bsmilp
from algorithms.llpp import llpp
from algorithms.branch_and_cut import branch_and_cut
from algorithms.fptas import fptas


def optimize_cargo(
    cargo_list,
    capacity,
    gamma,
    algorithm="Robust DP",
    epsilon=0.2
):
    """
    Run the selected Robust Knapsack optimization algorithm
    and measure its execution time.
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

    elif algorithm == "FPTAS":
        result = fptas(
            cargo_list,
            capacity,
            gamma,
            epsilon
        )

    else:
        raise ValueError(
            f"Unknown algorithm: {algorithm}"
        )

    end_time = time.perf_counter()

    runtime = end_time - start_time

    result["runtime"] = runtime

    return result