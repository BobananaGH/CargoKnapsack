# tests/test_recursive_partitioning_bruteforce.py

"""
Brute-force validation for Recursive Partitioning.

The purpose of this test is to compare the Recursive
Partitioning implementation against the true optimal
solution obtained by exhaustive enumeration.

Only small instances are used because brute force
checks every possible subset.
"""

import random

from models.cargo import Cargo
from algorithms.recursive_partitioning import (
    recursive_partitioning
)


# ============================================================
# Brute-force RKP
# ============================================================

def brute_force_rkp(cargo_list, capacity, gamma):
    """
    Solve the Robust Knapsack Problem by checking
    every possible subset.

    This is used only as a correctness reference.

    Robust weight of a selected subset:

        nominal weight
        +
        sum of the Gamma largest uncertainties

    where:

        uncertainty = max_weight - weight
    """

    n = len(cargo_list)

    best_profit = 0
    best_items = []

    # There are 2^n possible subsets.
    for mask in range(1 << n):

        selected = []

        nominal_weight = 0
        total_profit = 0

        for i in range(n):

            if mask & (1 << i):

                cargo = cargo_list[i]

                selected.append(cargo)

                nominal_weight += cargo.weight
                total_profit += cargo.profit

        # Calculate uncertainties of selected items.
        uncertainties = sorted(
            (
                cargo.uncertainty
                for cargo in selected
            ),
            reverse=True
        )

        robust_weight = (
            nominal_weight
            + sum(uncertainties[:gamma])
        )

        # Check robust feasibility.
        if robust_weight <= capacity:

            if total_profit > best_profit:

                best_profit = total_profit
                best_items = selected

    return best_profit, best_items


# ============================================================
# Generate random cargo
# ============================================================

def generate_random_cargo(n):
    """
    Generate a small random cargo list.

    Small weights and profits keep the brute-force
    validation easy to run.
    """

    cargo_list = []

    for i in range(n):

        weight = random.randint(1, 15)

        uncertainty = random.randint(0, 8)

        max_weight = (
            weight + uncertainty
        )

        profit = random.randint(1, 50)

        cargo_list.append(
            Cargo(
                name=f"Item {i + 1}",
                weight=weight,
                max_weight=max_weight,
                profit=profit
            )
        )

    return cargo_list


# ============================================================
# Validate one case
# ============================================================

def validate_case(cargo_list, capacity, gamma):
    """
    Compare Recursive Partitioning with brute force.

    Returns True if both produce the same optimal profit.
    """

    brute_profit, brute_items = brute_force_rkp(
        cargo_list,
        capacity,
        gamma
    )

    result = recursive_partitioning(
        cargo_list,
        capacity,
        gamma
    )

    recursive_profit = result["total_profit"]

    # --------------------------------------------------------
    # Check optimal profit.
    # --------------------------------------------------------

    if recursive_profit != brute_profit:

        print("\nFAILED CASE")

        print("Capacity:", capacity)
        print("Gamma:", gamma)

        print("\nCargo:")

        for cargo in cargo_list:

            print(
                f"  {cargo.name}: "
                f"weight={cargo.weight}, "
                f"max_weight={cargo.max_weight}, "
                f"profit={cargo.profit}, "
                f"uncertainty={cargo.uncertainty}"
            )

        print(
            "\nBrute-force profit:",
            brute_profit
        )

        print(
            "Recursive Partitioning profit:",
            recursive_profit
        )

        print(
            "\nBrute-force selected:",
            brute_items
        )

        print(
            "Recursive selected:",
            result["selected_items"]
        )

        print(
            "\nRecursive nominal weight:",
            result["nominal_weight"]
        )

        print(
            "Recursive robust weight:",
            result["robust_weight"]
        )

        return False

    # --------------------------------------------------------
    # Also verify that the returned solution is actually
    # robust feasible.
    # --------------------------------------------------------

    if result["robust_weight"] > capacity:

        print("\nFAILED CASE")

        print(
            "Recursive solution is NOT robust feasible."
        )

        print("Capacity:", capacity)
        print("Gamma:", gamma)

        print(
            "Robust weight:",
            result["robust_weight"]
        )

        print(
            "Selected:",
            result["selected_items"]
        )

        return False

    return True


# ============================================================
# Main validation
# ============================================================

def main():

    random.seed(42)

    total_cases = 1000
    passed_cases = 0

    print(
        f"Running {total_cases} random brute-force cases..."
    )

    for case_number in range(
        1,
        total_cases + 1
    ):

        # Keep n small because brute force is O(2^n).
        n = random.randint(1, 8)

        cargo_list = generate_random_cargo(n)

        # Generate a capacity that is useful for
        # both feasible and infeasible cases.
        capacity = random.randint(5, 40)

        # Gamma can range from 0 to n.
        gamma = random.randint(0, n)

        passed = validate_case(
            cargo_list,
            capacity,
            gamma
        )

        if not passed:

            print(
                f"\nValidation stopped at case "
                f"{case_number}."
            )

            return

        passed_cases += 1

    print()
    print("========================================")
    print("Brute-force validation completed")
    print("========================================")
    print("Total cases:", total_cases)
    print("Passed cases:", passed_cases)

    if passed_cases == total_cases:

        print()
        print(
            "All cases passed."
        )

        print(
            "Recursive Partitioning matched "
            "the brute-force optimum in every case."
        )


if __name__ == "__main__":
    main()