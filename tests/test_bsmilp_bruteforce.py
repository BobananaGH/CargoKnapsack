import random

from models.cargo import Cargo
from algorithms.bsmilp import bsmilp


# ============================================================
# Brute-force reference solver
# ============================================================

def brute_force_rkp(cargo_list, capacity, gamma):
    """
    Solve the Robust Knapsack Problem by exhaustive search.

    This is used as the reference solution for validating
    BSMILP on small random instances.
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

                uncertainties.append(
                    cargo.uncertainty
                )

        # ----------------------------------------------------
        # Worst-case robust weight:
        #
        # nominal weight
        # +
        # Gamma largest uncertainties
        # ----------------------------------------------------

        uncertainties.sort(reverse=True)

        robust_weight = (
            nominal_weight
            + sum(uncertainties[:gamma])
        )

        # ----------------------------------------------------
        # Check feasibility.
        # ----------------------------------------------------

        if robust_weight > capacity:
            continue

        # ----------------------------------------------------
        # Keep best solution.
        # ----------------------------------------------------

        if profit > best_profit:

            best_profit = profit

            best_indices = selected_indices

    return best_profit, best_indices


# ============================================================
# Generate random test case
# ============================================================

def generate_random_case():

    # Small n because brute force checks 2^n subsets.
    n = random.randint(1, 8)

    capacity = random.randint(5, 50)

    gamma = random.randint(0, n)

    cargo_list = []

    for i in range(n):

        weight = random.randint(1, 15)

        uncertainty = random.randint(0, 8)

        max_weight = (
            weight + uncertainty
        )

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
    case_number
):

    expected_profit, expected_indices = (
        brute_force_rkp(
            cargo_list,
            capacity,
            gamma
        )
    )

    result = bsmilp(
        cargo_list,
        capacity,
        gamma
    )

    actual_profit = result["total_profit"]

    # --------------------------------------------------------
    # Check objective value.
    # --------------------------------------------------------

    if actual_profit != expected_profit:

        print()
        print("=" * 60)
        print("FAILED CASE")
        print("=" * 60)

        print(f"Case: {case_number}")
        print(f"Capacity: {capacity}")
        print(f"Gamma: {gamma}")

        print()
        print("Cargo:")

        for cargo in cargo_list:

            print(
                f"  {cargo.name}: "
                f"weight={cargo.weight}, "
                f"max_weight={cargo.max_weight}, "
                f"uncertainty={cargo.uncertainty}, "
                f"profit={cargo.profit}"
            )

        print()
        print(
            f"Expected profit: {expected_profit}"
        )

        print(
            f"Actual profit:   {actual_profit}"
        )

        print()
        print(
            "Expected selected indexes:",
            expected_indices
        )

        print(
            "BSMILP selected cargo:"
        )

        for cargo in result["selected_items"]:

            print(
                f"  {cargo.name}"
            )

        print()
        print(
            f"BSMILP nominal weight: "
            f"{result['nominal_weight']}"
        )

        print(
            f"BSMILP robust weight: "
            f"{result['robust_weight']}"
        )

        return False

    # --------------------------------------------------------
    # Check robust feasibility.
    # --------------------------------------------------------

    selected_items = result["selected_items"]

    nominal_weight = sum(
        cargo.weight
        for cargo in selected_items
    )

    uncertainties = sorted(
        (
            cargo.uncertainty
            for cargo in selected_items
        ),
        reverse=True
    )

    robust_weight = (
        nominal_weight
        + sum(uncertainties[:gamma])
    )

    if robust_weight > capacity:

        print()
        print("=" * 60)
        print("FAILED CASE - INFEASIBLE SOLUTION")
        print("=" * 60)

        print(f"Case: {case_number}")
        print(f"Capacity: {capacity}")
        print(f"Gamma: {gamma}")

        print(
            f"Nominal weight: {nominal_weight}"
        )

        print(
            f"Robust weight: {robust_weight}"
        )

        return False

    return True


# ============================================================
# Main test
# ============================================================

def main():

    random.seed(42)

    total_cases = 1000
    passed_cases = 0

    print(
        f"Running {total_cases} "
        "random brute-force cases..."
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
            "BSMILP matched the brute-force "
            "optimum in every case."
        )


if __name__ == "__main__":
    main()