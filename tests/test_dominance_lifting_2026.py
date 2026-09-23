import random
from fractions import Fraction

from algorithms.dominance_lifting_2026 import (
    dominance_list_knapsack,
)


# ============================================================
# Independent brute-force reference
# ============================================================

def brute_force_knapsack(
    weights,
    profits,
    capacity,
):
    """
    Independent brute-force solution for the ordinary
    0/1 knapsack problem.

    maximize:
        sum(p_i * x_i)

    subject to:
        sum(w_i * x_i) <= capacity

        x_i in {0, 1}

    This function intentionally does NOT use the
    dominance-list DP.
    """

    weights = [
        Fraction(value)
        for value in weights
    ]

    profits = [
        Fraction(value)
        for value in profits
    ]

    capacity = Fraction(capacity)

    n = len(weights)

    best_profit = Fraction(0)
    best_weight = Fraction(0)

    for mask in range(1 << n):

        total_weight = Fraction(0)
        total_profit = Fraction(0)

        for i in range(n):

            if mask & (1 << i):

                total_weight += weights[i]
                total_profit += profits[i]

        if total_weight <= capacity:

            if total_profit > best_profit:

                best_profit = total_profit
                best_weight = total_weight

            elif (
                total_profit == best_profit
                and total_weight < best_weight
            ):

                best_weight = total_weight

    return {
        "total_profit": best_profit,
        "total_weight": best_weight,
    }


# ============================================================
# Verify dominance-list structure
# ============================================================

def verify_dominance_list(
    dominance_list,
):
    """
    Verify the defining property of a dominance list.

    States must be strictly increasing in:

        weight

    and

        profit

    This follows the dominance-list structure used by
    the 2026 paper.
    """

    for i in range(
        1,
        len(dominance_list),
    ):

        previous_weight, previous_profit = (
            dominance_list[i - 1]
        )

        current_weight, current_profit = (
            dominance_list[i]
        )

        assert previous_weight < current_weight, (
            "\nDominance-list weight order violated.\n"
            f"Previous: {dominance_list[i - 1]}\n"
            f"Current:  {dominance_list[i]}"
        )

        assert previous_profit < current_profit, (
            "\nDominance-list profit order violated.\n"
            f"Previous: {dominance_list[i - 1]}\n"
            f"Current:  {dominance_list[i]}"
        )


# ============================================================
# Test one instance
# ============================================================

def test_case(
    weights,
    profits,
    capacity,
    case_name="",
):
    """
    Compare the 2026 dominance-list DP against an
    independent brute-force solution.
    """

    expected = brute_force_knapsack(
        weights=weights,
        profits=profits,
        capacity=capacity,
    )

    actual = dominance_list_knapsack(
        weights=weights,
        profits=profits,
        capacity=capacity,
    )

    # --------------------------------------------------------
    # Verify objective value.
    # --------------------------------------------------------

    assert actual["total_profit"] == (
        expected["total_profit"]
    ), (
        "\nDominance-list DP profit mismatch.\n"
        f"Case: {case_name}\n"
        f"Weights: {weights}\n"
        f"Profits: {profits}\n"
        f"Capacity: {capacity}\n"
        f"Expected profit: {expected['total_profit']}\n"
        f"Actual profit:   {actual['total_profit']}\n"
    )

    # --------------------------------------------------------
    # Verify returned weight.
    #
    # For an optimal profit, the implementation should return
    # the corresponding minimum-weight state because the
    # dominance list contains only non-dominated states.
    # --------------------------------------------------------

    assert actual["total_weight"] == (
        expected["total_weight"]
    ), (
        "\nDominance-list DP weight mismatch.\n"
        f"Case: {case_name}\n"
        f"Weights: {weights}\n"
        f"Profits: {profits}\n"
        f"Capacity: {capacity}\n"
        f"Expected weight: {expected['total_weight']}\n"
        f"Actual weight:   {actual['total_weight']}\n"
    )

    # --------------------------------------------------------
    # Verify feasibility.
    # --------------------------------------------------------

    assert actual["total_weight"] <= Fraction(
        capacity
    ), (
        "\nReturned state is infeasible.\n"
        f"Case: {case_name}\n"
        f"Weight: {actual['total_weight']}\n"
        f"Capacity: {capacity}\n"
    )

    # --------------------------------------------------------
    # Verify dominance-list structure.
    # --------------------------------------------------------

    verify_dominance_list(
        actual["dominance_list"]
    )

    # --------------------------------------------------------
    # The final state must be the optimal state because the
    # dominance list is increasing in profit.
    # --------------------------------------------------------

    final_weight, final_profit = (
        actual["dominance_list"][-1]
    )

    assert final_profit == actual["total_profit"], (
        "\nFinal dominance-list state does not match "
        "the reported total profit.\n"
        f"Case: {case_name}\n"
        f"Final state: {actual['dominance_list'][-1]}\n"
        f"Reported profit: {actual['total_profit']}"
    )

    assert final_weight == actual["total_weight"], (
        "\nFinal dominance-list state does not match "
        "the reported total weight.\n"
        f"Case: {case_name}\n"
        f"Final state: {actual['dominance_list'][-1]}\n"
        f"Reported weight: {actual['total_weight']}"
    )


# ============================================================
# Basic deterministic tests
# ============================================================

def test_basic_cases():
    """
    Small hand-checkable 0/1 knapsack instances.
    """

    test_case(
        weights=[
            10,
            20,
            30,
        ],
        profits=[
            60,
            100,
            120,
        ],
        capacity=50,
        case_name="Classic knapsack",
    )

    test_case(
        weights=[
            2,
            3,
            4,
        ],
        profits=[
            3,
            4,
            5,
        ],
        capacity=5,
        case_name="Small knapsack",
    )

    test_case(
        weights=[
            5,
            4,
            6,
            3,
        ],
        profits=[
            10,
            40,
            30,
            50,
        ],
        capacity=10,
        case_name="Mixed values",
    )


# ============================================================
# Test capacity smaller than every item
# ============================================================

def test_no_item_fits():
    """
    If no item fits, the optimal solution is the empty set.
    """

    test_case(
        weights=[
            5,
            6,
            7,
        ],
        profits=[
            10,
            20,
            30,
        ],
        capacity=4,
        case_name="No item fits",
    )


# ============================================================
# Test capacity large enough for everything
# ============================================================

def test_all_items_fit():
    """
    If all items fit, the optimal solution contains every item.
    """

    weights = [
        2,
        3,
        4,
        5,
    ]

    profits = [
        10,
        20,
        30,
        40,
    ]

    capacity = 100

    test_case(
        weights=weights,
        profits=profits,
        capacity=capacity,
        case_name="All items fit",
    )


# ============================================================
# Test equal profits
# ============================================================

def test_equal_profits():
    """
    Multiple items can have identical profits.

    The dominance-list implementation must still maintain
    a valid strictly increasing profit sequence.
    """

    test_case(
        weights=[
            2,
            3,
            4,
            5,
        ],
        profits=[
            10,
            10,
            10,
            10,
        ],
        capacity=7,
        case_name="Equal profits",
    )


# ============================================================
# Test fractional values
# ============================================================

def test_fractional_values():
    """
    The implementation uses Fraction internally, so test
    non-integer weights and profits as well.
    """

    test_case(
        weights=[
            Fraction(3, 2),
            Fraction(5, 2),
            Fraction(4),
        ],
        profits=[
            Fraction(7, 2),
            Fraction(9, 2),
            Fraction(6),
        ],
        capacity=Fraction(5),
        case_name="Fractional values",
    )


# ============================================================
# Random instance generator
# ============================================================

def generate_random_case():
    """
    Generate a small random instance suitable for exhaustive
    brute-force validation.
    """

    n = random.randint(
        1,
        12,
    )

    weights = [
        random.randint(
            1,
            20,
        )
        for _ in range(n)
    ]

    profits = [
        random.randint(
            0,
            50,
        )
        for _ in range(n)
    ]

    capacity = random.randint(
        1,
        40,
    )

    return (
        weights,
        profits,
        capacity,
    )


# ============================================================
# Random brute-force validation
# ============================================================

def test_random_cases():
    """
    Compare the 2026 dominance-list DP against brute force
    on many randomly generated instances.

    The brute-force solver is completely independent from
    the dominance-list implementation.
    """

    random.seed(42)

    total_cases = 1000

    for case_number in range(
        1,
        total_cases + 1,
    ):

        (
            weights,
            profits,
            capacity,
        ) = generate_random_case()

        test_case(
            weights=weights,
            profits=profits,
            capacity=capacity,
            case_name=f"Random case {case_number}",
        )


# ============================================================
# Paper-style Example 4 DP check
# ============================================================

def test_paper_example_4_dp():
    """
    Use the numerical data from Example 4 of the 2026 paper,
    but test ONLY the dominance-list DP.

    This deliberately does NOT test sequential lifting.

    We use the final coefficients:

        [1, 1, 1, 1, 1, 0, 2]

    as the DP objective coefficients.

    The resulting DP is an ordinary 0/1 knapsack over the
    same weights.
    """

    weights = [
        3,
        4,
        5,
        4,
        2,
        3,
        6,
    ]

    coefficients = [
        1,
        1,
        1,
        1,
        1,
        0,
        2,
    ]

    capacity = 18

    test_case(
        weights=weights,
        profits=coefficients,
        capacity=capacity,
        case_name="2026 paper Example 4",
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    Run all dominance-list DP tests.
    """

    print(
        "Testing 2026 dominance-list DP..."
    )

    print()
    print(
        "Testing deterministic cases..."
    )

    test_basic_cases()
    test_no_item_fits()
    test_all_items_fit()
    test_equal_profits()
    test_fractional_values()

    print(
        "Deterministic cases passed."
    )

    print()
    print(
        "Testing 2026 paper Example 4..."
    )

    test_paper_example_4_dp()

    print(
        "Paper Example 4 DP test passed."
    )

    print()
    print(
        "Running 1000 random brute-force cases..."
    )

    test_random_cases()

    print()
    print("=" * 60)
    print(
        "Dominance-list DP validation completed"
    )
    print("=" * 60)

    print(
        "Deterministic cases: passed"
    )

    print(
        "Paper Example 4: passed"
    )

    print(
        "Random cases: 1000 / 1000 passed"
    )

    print()
    print(
        "The 2026 dominance-list DP matched the "
        "independent brute-force 0/1 knapsack solution "
        "for every tested instance."
    )

    print()
    print(
        "The dominance-list structure was also verified "
        "to remain strictly increasing in weight and profit."
    )


if __name__ == "__main__":
    main()