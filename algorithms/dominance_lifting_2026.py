"""
Dominance-list dynamic programming based on:

X. Wang, L. Chen, Y.-H. Dai,
"Efficient exact sequential lifting algorithm for binary knapsack set",
arXiv:2602.22640, 2026.

This file contains ONLY the dominance-list DP logic from Section 3
of the paper.

Implemented ideas:
    - Definition 1: DP states (weight, profit)
    - Definition 2: dominance
    - Definition 3: dominance list
    - Theorem 1: dominance list represents F_k(z)
    - Section 3.2 / Algorithm 1: dominance-list iteration and merging

The sequential-lifting procedure from Algorithm 3 is intentionally
NOT implemented here.

For comparison with the 2013 Robust DP, this implementation can be
used on the ordinary 0/1 knapsack problem by setting Gamma = 0 in
the 2013 Robust DP.
"""

from fractions import Fraction


def _to_fraction(value):
    """
    Convert an input value to Fraction.

    Using Fraction keeps the dominance-list DP exact and allows
    non-integer weights/capacities.
    """

    if isinstance(value, Fraction):
        return value

    if isinstance(value, int):
        return Fraction(value, 1)

    if isinstance(value, float):
        return Fraction(str(value))

    return Fraction(value)


def _validate_inputs(weights, profits, capacity):
    """
    Validate the ordinary 0/1 knapsack input.

    The 2026 paper assumes strictly positive item weights and
    non-negative capacity.
    """

    if len(weights) != len(profits):
        raise ValueError(
            "weights and profits must have the same length"
        )

    capacity = _to_fraction(capacity)

    if capacity < 0:
        raise ValueError(
            "capacity must be non-negative"
        )

    converted_weights = []
    converted_profits = []

    for i, (weight, profit) in enumerate(
        zip(weights, profits)
    ):

        weight = _to_fraction(weight)
        profit = _to_fraction(profit)

        if weight <= 0:
            raise ValueError(
                f"weight of item {i} must be greater than 0"
            )

        if profit < 0:
            raise ValueError(
                f"profit of item {i} must be non-negative"
            )

        converted_weights.append(weight)
        converted_profits.append(profit)

    return (
        converted_weights,
        converted_profits,
        capacity
    )


def _validate_dominance_list(dominance_list):
    """
    Verify the structural property of a dominance list.

    States in a dominance list must be strictly increasing
    in both weight and profit.
    """

    for i in range(
        1,
        len(dominance_list)
    ):

        previous_weight, previous_profit = (
            dominance_list[i - 1]
        )

        current_weight, current_profit = (
            dominance_list[i]
        )

        if not previous_weight < current_weight:
            raise ValueError(
                "Dominance list weights must be strictly increasing."
            )

        if not previous_profit < current_profit:
            raise ValueError(
                "Dominance list profits must be strictly increasing."
            )


def _merge_dominance_lists(
    dominance_list,
    item_weight,
    item_profit,
    capacity,
):
    """
    Algorithm 1 from the 2026 paper.

    Given L_(k-1), construct the shifted list

        L_(k-1) + (a_k, alpha_k)

    and merge it with L_(k-1) while removing dominated states.

    The implementation follows the two-pointer structure of
    Algorithm 1 rather than constructing and sorting all
    possible states.
    """

    if item_weight <= 0:
        raise ValueError(
            "item_weight must be positive"
        )

    if item_profit < 0:
        raise ValueError(
            "item_profit must be non-negative"
        )

    if not dominance_list:
        return []

    m = len(dominance_list)

    # Current position in the original list.
    i = 0

    # Current position in the shifted list.
    j = 0

    # Output dominance list.
    result = []

    # --------------------------------------------------------------
    # Algorithm 1:
    #
    # L_(k-1)
    #
    # and
    #
    # L_(k-1) + (a_k, alpha_k)
    #
    # are already sorted by weight.
    # --------------------------------------------------------------

    while i < m and j < m:

        original_weight, original_profit = (
            dominance_list[i]
        )

        shifted_weight = (
            dominance_list[j][0]
            + item_weight
        )

        shifted_profit = (
            dominance_list[j][1]
            + item_profit
        )

        # The paper processes whichever candidate
        # has smaller weight.
        if original_weight <= shifted_weight:

            candidate_weight = original_weight
            candidate_profit = original_profit

            i += 1

        else:

            candidate_weight = shifted_weight
            candidate_profit = shifted_profit

            j += 1

        if candidate_weight > capacity:
            continue

        # ----------------------------------------------------------
        # Dominance check.
        #
        # Because result is already ordered, only the most recent
        # non-dominated state needs to be checked.
        # ----------------------------------------------------------

        if not result:

            result.append(
                (
                    candidate_weight,
                    candidate_profit
                )
            )

            continue

        last_weight, last_profit = result[-1]

        # Candidate is dominated or identical.
        if candidate_profit <= last_profit:
            continue

        # Same weight but better profit.
        if candidate_weight == last_weight:

            result[-1] = (
                candidate_weight,
                candidate_profit,
            )

            continue

        # Candidate has greater weight and greater profit.
        result.append(
            (
                candidate_weight,
                candidate_profit
            )
        )

    # --------------------------------------------------------------
    # Remaining states from the original list.
    # --------------------------------------------------------------

    while i < m:

        candidate_weight, candidate_profit = (
            dominance_list[i]
        )

        i += 1

        if candidate_weight > capacity:
            break

        if not result:

            result.append(
                (
                    candidate_weight,
                    candidate_profit
                )
            )

            continue

        last_weight, last_profit = result[-1]

        if candidate_profit <= last_profit:
            continue

        if candidate_weight == last_weight:

            result[-1] = (
                candidate_weight,
                candidate_profit,
            )

        else:

            result.append(
                (
                    candidate_weight,
                    candidate_profit
                )
            )

    # --------------------------------------------------------------
    # Remaining states from the shifted list.
    # --------------------------------------------------------------

    while j < m:

        candidate_weight = (
            dominance_list[j][0]
            + item_weight
        )

        candidate_profit = (
            dominance_list[j][1]
            + item_profit
        )

        j += 1

        if candidate_weight > capacity:
            break

        if not result:

            result.append(
                (
                    candidate_weight,
                    candidate_profit
                )
            )

            continue

        last_weight, last_profit = result[-1]

        if candidate_profit <= last_profit:
            continue

        if candidate_weight == last_weight:

            result[-1] = (
                candidate_weight,
                candidate_profit,
            )

        else:

            result.append(
                (
                    candidate_weight,
                    candidate_profit
                )
            )

    _validate_dominance_list(result)

    return result


def _reconstruct_selected_indices(
    weights,
    profits,
    target_weight,
    target_profit,
):
    """
    Reconstruct one optimal subset that produces the
    final dominance-list state.

    This is a separate reconstruction step performed
    after the dominance-list DP.

    It does not change the dominance-list states or
    the merge algorithm.
    """

    current_states = {
        (
            Fraction(0),
            Fraction(0)
        ): ()
    }

    for index, (
        item_weight,
        item_profit
    ) in enumerate(
        zip(weights, profits)
    ):

        next_states = dict(
            current_states
        )

        for (
            current_weight,
            current_profit
        ), selected_indices in current_states.items():

            new_weight = (
                current_weight
                + item_weight
            )

            new_profit = (
                current_profit
                + item_profit
            )

            # States above capacity cannot be part
            # of a feasible solution.
            if new_weight > target_weight:
                continue

            state = (
                new_weight,
                new_profit
            )

            if state not in next_states:

                next_states[state] = (
                    selected_indices
                    + (index,)
                )

        current_states = next_states

    target_state = (
        target_weight,
        target_profit
    )

    if target_state not in current_states:
        raise RuntimeError(
            "Could not reconstruct the optimal solution."
        )

    return list(
        current_states[target_state]
    )


def dominance_list_knapsack(
    weights,
    profits,
    capacity
):
    """
    Solve an ordinary 0/1 knapsack problem using the
    dominance-list dynamic programming structure from
    the 2026 paper.

    Mathematical problem:

        maximize
            sum(p_i x_i)

        subject to
            sum(w_i x_i) <= capacity

            x_i in {0, 1}

    DP state:

        (weight, profit)

    Initial dominance list:

        L_0 = {(0, 0)}

    For each item k:

        L'_k = L_(k-1) + (w_k, p_k)

        L_k = merge(L_(k-1), L'_k)

    Only non-dominated states are retained.

    Returns
    -------
    dict
        {
            "total_profit": Fraction,
            "total_weight": Fraction,
            "dominance_list": list,
            "selected_indices": list
        }

    Notes
    -----
    This function intentionally does not implement sequential lifting.

    The selected_indices field is reconstructed after the
    dominance-list DP so that the GUI can identify the original
    cargo items without changing the DP state representation.
    """

    weights, profits, capacity = _validate_inputs(
        weights,
        profits,
        capacity,
    )

    # --------------------------------------------------------------
    # Paper Section 3.2:
    #
    # Initialize:
    #
    # L_0 = {(0, 0)}
    # --------------------------------------------------------------

    dominance_list = [
        (
            Fraction(0),
            Fraction(0)
        )
    ]

    # --------------------------------------------------------------
    # Generate L_1, L_2, ..., L_n.
    # --------------------------------------------------------------

    for weight, profit in zip(
        weights,
        profits
    ):

        dominance_list = _merge_dominance_lists(
            dominance_list=dominance_list,
            item_weight=weight,
            item_profit=profit,
            capacity=capacity,
        )

    # --------------------------------------------------------------
    # The final state with maximum profit gives F_n(capacity).
    #
    # Because the dominance list is strictly increasing in profit,
    # the final state has the largest profit.
    # --------------------------------------------------------------

    best_weight, best_profit = (
        dominance_list[-1]
    )

    # --------------------------------------------------------------
    # Reconstruct the original item indices corresponding
    # to the optimal state.
    #
    # This is separate from the dominance-list DP itself.
    # --------------------------------------------------------------

    selected_indices = _reconstruct_selected_indices(
        weights=weights,
        profits=profits,
        target_weight=best_weight,
        target_profit=best_profit,
    )

    return {
        "total_profit": best_profit,
        "total_weight": best_weight,
        "dominance_list": dominance_list,
        "selected_indices": selected_indices,
    }