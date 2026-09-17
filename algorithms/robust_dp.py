"""
Exact Dynamic Programming algorithm for the Robust Knapsack Problem.

Based on Section 2 of:

"Exact solution of the robust knapsack problem"

M. Monaci, U. Pferschy, P. Serafini

The implementation follows Figure 2 of the paper.

Items are sorted by non-increasing uncertainty:

    uncertainty_j = max_weight_j - weight_j

The DP state is:

    z[d][s]

where:

    d = current capacity
    s = number of items currently assumed to take
        their upper weight

When s == Gamma:
    additional items may be inserted using nominal weight.

When s < Gamma:
    an inserted item must use its upper weight.

Complexity:

    Time:  O(Gamma * n * C)
    Space: O(Gamma * C)

The implementation stores the selected item indexes for
solution reconstruction.
"""


NEG_INF = float("-inf")


def robust_knapsack(cargo_list, capacity, gamma):
    """
    Solve the Robust Knapsack Problem exactly using Dynamic
    Programming.

    Parameters:
        cargo_list:
            List of Cargo objects.

        capacity:
            Maximum capacity.

        gamma:
            Maximum number of selected items that may reach
            their upper weights.

    Returns:
        Dictionary containing:

            selected_items
            total_profit
            nominal_weight
            robust_weight
    """

    n = len(cargo_list)

    # --------------------------------------------------------
    # Empty input.
    # --------------------------------------------------------

    if n == 0 or capacity <= 0:
        return {
            "selected_items": [],
            "total_profit": 0,
            "nominal_weight": 0,
            "robust_weight": 0,
        }

    # --------------------------------------------------------
    # Normalize Gamma.
    # --------------------------------------------------------

    gamma = min(
        max(gamma, 0),
        n
    )

    # --------------------------------------------------------
    # Sort items by non-increasing uncertainty.
    #
    # uncertainty = max_weight - weight
    #
    # This ordering is required by Lemma 1.
    # --------------------------------------------------------

    items = sorted(
        cargo_list,
        key=lambda cargo: cargo.uncertainty,
        reverse=True
    )

    # ========================================================
    # DP ARRAYS
    # ========================================================
    #
    # z[d][s]
    #
    # d = total current weight
    # s = number of items using upper weight
    #
    # Each entry stores:
    #
    #     best profit
    #
    # and
    #
    #     tuple of selected item indexes
    #
    # for reconstruction.
    # ========================================================

    dp = [
        [NEG_INF] * (capacity + 1)
        for _ in range(gamma + 1)
    ]

    choices = [
        [None] * (capacity + 1)
        for _ in range(gamma + 1)
    ]

    # --------------------------------------------------------
    # Initialization:
    #
    # z(0,0) = 0
    #
    # All other states are initially unreachable.
    # --------------------------------------------------------

    dp[0][0] = 0
    choices[0][0] = ()

    # ========================================================
    # MAIN DP
    # ========================================================
    #
    # This follows Figure 2 of the paper:
    #
    # For each item:
    #
    #   1. Possibly pack item using nominal weight
    #      if Gamma heavy items have already been selected.
    #
    #   2. Possibly pack item using upper weight.
    #
    # The order is important.
    # ========================================================

    for j in range(n):

        cargo = items[j]

        # ----------------------------------------------------
        # STEP 1
        #
        # Possibly pack item j using nominal weight.
        #
        # This is only possible in stage Gamma.
        #
        # Paper:
        #
        # for d := c down to w_j do
        #     if z(d-w_j,Gamma) + p_j > z(d,Gamma)
        # ----------------------------------------------------

        if cargo.weight <= capacity:

            for d in range(
                capacity,
                cargo.weight - 1,
                -1
            ):

                previous = dp[
                    gamma
                ][
                    d - cargo.weight
                ]

                if previous == NEG_INF:
                    continue

                candidate = (
                    previous
                    + cargo.profit
                )

                if candidate > dp[gamma][d]:

                    old_choice = choices[
                        gamma
                    ][
                        d - cargo.weight
                    ]

                    dp[gamma][d] = candidate

                    choices[gamma][d] = (
                        old_choice
                        + (j,)
                    )

        # ----------------------------------------------------
        # STEP 2
        #
        # Possibly pack item j using upper weight.
        #
        # This moves from stage s-1 to stage s.
        #
        # IMPORTANT:
        #
        # s is processed from Gamma down to 1.
        #
        # This ensures that the current item cannot be used
        # more than once.
        #
        # Paper:
        #
        # for s := Gamma down to 1 do
        #     for d := c down to w_hat_j do
        #         if z(d-w_hat_j,s-1) + p_j > z(d,s)
        # ----------------------------------------------------

        if cargo.max_weight <= capacity:

            for s in range(
                gamma,
                0,
                -1
            ):

                for d in range(
                    capacity,
                    cargo.max_weight - 1,
                    -1
                ):

                    previous = dp[
                        s - 1
                    ][
                        d - cargo.max_weight
                    ]

                    if previous == NEG_INF:
                        continue

                    candidate = (
                        previous
                        + cargo.profit
                    )

                    if candidate > dp[s][d]:

                        old_choice = choices[
                            s - 1
                        ][
                            d - cargo.max_weight
                        ]

                        dp[s][d] = candidate

                        choices[s][d] = (
                            old_choice
                            + (j,)
                        )

    # ========================================================
    # FIND BEST SOLUTION
    # ========================================================
    #
    # The paper's Figure 2 returns:
    #
    # max { z(d,s) |
    #       d = 1,...,c
    #       s = 1,...,Gamma }
    #
    # The destination can also be reached with fewer than
    # Gamma heavy items, so we include s = 0 as well.
    #
    # This is necessary for cases where Gamma is larger than
    # the number of selected items.
    # ========================================================

    best_profit = 0
    best_choice = ()

    for s in range(
        gamma + 1
    ):

        for d in range(
            capacity + 1
        ):

            if dp[s][d] > best_profit:

                best_profit = dp[s][d]

                best_choice = choices[s][d]

    # ========================================================
    # RECONSTRUCT SELECTED ITEMS
    # ========================================================

    selected_items = [
        items[index]
        for index in best_choice
    ]

    # ========================================================
    # CALCULATE RESULT
    # ========================================================

    total_profit = sum(
        cargo.profit
        for cargo in selected_items
    )

    nominal_weight = sum(
        cargo.weight
        for cargo in selected_items
    )

    # --------------------------------------------------------
    # Worst-case robust weight:
    #
    # nominal weight
    # +
    # Gamma largest uncertainties
    # --------------------------------------------------------

    uncertainties = sorted(
        (
            cargo.uncertainty
            for cargo in selected_items
        ),
        reverse=True
    )

    robust_weight = (
        nominal_weight
        + sum(
            uncertainties[:gamma]
        )
    )

    # ========================================================
    # SAFETY CHECK
    # ========================================================

    if robust_weight > capacity:

        raise RuntimeError(
            "Internal error: reconstructed solution "
            "is not robust feasible."
        )

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {
        "selected_items": selected_items,
        "total_profit": total_profit,
        "nominal_weight": nominal_weight,
        "robust_weight": robust_weight,
    }