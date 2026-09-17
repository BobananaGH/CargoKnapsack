import random

from models.cargo import Cargo
from algorithms.fptas import fptas


# ============================================================
# Brute-force reference solver
# ============================================================

def brute_force_rkp(cargo_list, capacity, gamma):
    """
    Solve the Robust Knapsack Problem by exhaustive search.
    Used as the exact reference solution.
    """

    n = len(cargo_list)

    best_profit = 0
    best_indices = []

    for mask in range(1 << n):

        selected_indices = []
        nominal_weight = 0
        profit = 0
        uncertainties = []

        for i in range(n):

            if mask & (1 << i):

                cargo = cargo_list[i]

                selected_indices.append(i)
                nominal_weight += cargo.weight
                profit += cargo.profit
                uncertainties.append(cargo.uncertainty)

        uncertainties.sort(reverse=True)

        robust_weight = (
            nominal_weight
            + sum(uncertainties[:gamma])
        )

        if robust_weight > capacity:
            continue

        if profit > best_profit:

            best_profit = profit
            best_indices = selected_indices

    return best_profit, best_indices


# ============================================================
# Generate random test case
# ============================================================

def generate_random_case():

    n = random.randint(1, 8)

    capacity = random.randint(5, 50)

    gamma = random.randint(0, n)

    cargo_list = []

    for i in range(n):

        weight = random.randint(1, 15)

        uncertainty = random.randint(0, 8)

        max_weight = weight + uncertainty

        profit = random.randint(1, 100)

        cargo_list.append(
            Cargo(
                name=f"Item {i + 1}",
                weight=weight,
                max_weight=max_weight,
                profit=profit,
            )
        )

    return cargo_list, capacity, gamma


# ============================================================
# Validate one case
# ============================================================

def validate_case(
    cargo_list,
    capacity,
    gamma,
    epsilon,
    case_number
):

    expected_profit, expected_indices = (
        brute_force_rkp(
            cargo_list,
            capacity,
            gamma
        )
    )

    result = fptas(
        cargo_list,
        capacity,
        gamma,
        epsilon
    )

    actual_profit = result["total_profit"]

    # --------------------------------------------------------
    # Check robust feasibility
    # --------------------------------------------------------

    if result["robust_weight"] > capacity:

        print()
        print("=" * 60)
        print("FAILED CASE - INFEASIBLE FPTAS SOLUTION")
        print("=" * 60)

        print(f"Case: {case_number}")
        print(f"Capacity: {capacity}")
        print(f"Gamma: {gamma}")
        print(f"Epsilon: {epsilon}")

        print(
            f"Robust weight: {result['robust_weight']}"
        )

        print(
            f"Capacity: {capacity}"
        )

        return False

    # --------------------------------------------------------
    # Check approximation guarantee
    # --------------------------------------------------------

    required_profit = (
        (1 - epsilon)
        * expected_profit
    )

    if actual_profit < required_profit:

        if expected_profit > 0:
            approximation_ratio = (
                actual_profit
                / expected_profit
            )
        else:
            approximation_ratio = 1.0

        print()
        print("=" * 60)
        print("FAILED CASE - APPROXIMATION GUARANTEE")
        print("=" * 60)

        print(f"Case: {case_number}")
        print(f"Capacity: {capacity}")
        print(f"Gamma: {gamma}")
        print(f"Epsilon: {epsilon}")

        print()
        print(
            f"Optimal profit:      {expected_profit}"
        )

        print(
            f"FPTAS profit:        {actual_profit}"
        )

        print(
            f"Required minimum:    {required_profit}"
        )

        print(
            f"Approximation ratio: "
            f"{approximation_ratio:.4f}"
        )

        print()
        print(
            "Expected selected indexes:",
            expected_indices
        )

        print(
            "FPTAS selected cargo:"
        )

        for cargo in result["selected_items"]:

            print(
                f"  {cargo.name}"
            )

        return False

    return True


# ============================================================
# Main
# ============================================================

def main():

    random.seed(42)

    total_cases = 1000
    passed_cases = 0

    epsilon = 0.2

    print(
        f"Running {total_cases} "
        "random brute-force cases..."
    )

    print(
        f"Epsilon: {epsilon}"
    )

    for case_number in range(
        1,
        total_cases + 1
    ):

        cargo_list, capacity, gamma = (
            generate_random_case()
        )

        passed = validate_case(
            cargo_list,
            capacity,
            gamma,
            epsilon,
            case_number
        )

        if not passed:

            print()
            print(
                "Validation stopped because "
                "a counterexample was found."
            )

            return

        passed_cases += 1

    print()
    print("=" * 40)
    print(
        "Brute-force validation completed"
    )
    print("=" * 40)

    print(
        f"Total cases: {total_cases}"
    )

    print(
        f"Passed cases: {passed_cases}"
    )

    if passed_cases == total_cases:

        print()
        print("All cases passed.")

        print(
            "FPTAS satisfied the approximation "
            "guarantee and robust feasibility "
            "in every case."
        )


if __name__ == "__main__":
    main()