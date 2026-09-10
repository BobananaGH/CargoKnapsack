# algorithms/robust_dp.py

def robust_knapsack(cargo_list, capacity, gamma):
    """
    Solve the Robust Knapsack Problem using Dynamic Programming.

    Based on Section 2 of:
    "Exact solution of the robust knapsack problem"

    Parameters:
        cargo_list: list of Cargo objects
        capacity: maximum capacity
        gamma: maximum number of items that may reach
               their upper weight

    Returns:
        Dictionary containing:
            selected_items
            total_profit
            nominal_weight
            robust_weight
    """

    n = len(cargo_list)

    if n == 0 or capacity <= 0:
        return {
            "selected_items": [],
            "total_profit": 0,
            "nominal_weight": 0,
            "robust_weight": 0,
        }

    gamma = min(max(gamma, 0), n)

    # ---------------------------------------------------------
    # Sort by decreasing uncertainty.
    #
    # uncertainty = max_weight - weight
    # ---------------------------------------------------------

    items = sorted(
        cargo_list,
        key=lambda cargo: cargo.uncertainty,
        reverse=True
    )

    NEG_INF = float("-inf")

    # =========================================================
    # PART 1
    #
    # bar_dp[s][d]
    #
    # Best profit using exactly s selected items with
    # their UPPER weights.
    #
    # This is used for the cases s < Gamma.
    # =========================================================

    bar_dp = [
        [NEG_INF] * (capacity + 1)
        for _ in range(gamma + 1)
    ]

    bar_choice = [
        [None] * (capacity + 1)
        for _ in range(gamma + 1)
    ]

    bar_dp[0][0] = 0
    bar_choice[0][0] = ()

    # Process ALL items.
    #
    # This is necessary because the final solution may have
    # fewer than Gamma uncertain items.
    #
    for j in range(n):

        cargo = items[j]

        for s in range(gamma, 0, -1):

            for d in range(
                capacity,
                cargo.max_weight - 1,
                -1
            ):

                previous = bar_dp[s - 1][
                    d - cargo.max_weight
                ]

                if previous == NEG_INF:
                    continue

                new_profit = previous + cargo.profit

                if new_profit > bar_dp[s][d]:

                    bar_dp[s][d] = new_profit

                    previous_choice = bar_choice[
                        s - 1
                    ][
                        d - cargo.max_weight
                    ]

                    bar_choice[s][d] = (
                        previous_choice + (j,)
                    )

    # =========================================================
    # PART 2
    #
    # Exact Gamma uncertain items.
    #
    # According to the paper:
    #
    # z(d, Gamma) = bar_z(d, Gamma, Gamma)
    #
    # Therefore the Gamma uncertain items must come from
    # the FIRST Gamma items after sorting by uncertainty.
    # =========================================================

    z_dp = [NEG_INF] * (capacity + 1)
    z_choice = [None] * (capacity + 1)

    if gamma == 0:

        z_dp[0] = 0
        z_choice[0] = ()

    else:

        # Recalculate the DP using ONLY the first Gamma items.
        first_gamma_dp = [
            [NEG_INF] * (capacity + 1)
            for _ in range(gamma + 1)
        ]

        first_gamma_choice = [
            [None] * (capacity + 1)
            for _ in range(gamma + 1)
        ]

        first_gamma_dp[0][0] = 0
        first_gamma_choice[0][0] = ()

        for j in range(gamma):

            cargo = items[j]

            for s in range(gamma, 0, -1):

                for d in range(
                    capacity,
                    cargo.max_weight - 1,
                    -1
                ):

                    previous = first_gamma_dp[s - 1][
                        d - cargo.max_weight
                    ]

                    if previous == NEG_INF:
                        continue

                    new_profit = (
                        previous + cargo.profit
                    )

                    if new_profit > first_gamma_dp[s][d]:

                        first_gamma_dp[s][d] = new_profit

                        previous_choice = (
                            first_gamma_choice[
                                s - 1
                            ][
                                d - cargo.max_weight
                            ]
                        )

                        first_gamma_choice[s][d] = (
                            previous_choice + (j,)
                        )

        # z(d, Gamma) = bar_z(d, Gamma, Gamma)
        for d in range(capacity + 1):

            if first_gamma_dp[gamma][d] != NEG_INF:

                z_dp[d] = first_gamma_dp[gamma][d]
                z_choice[d] = first_gamma_choice[gamma][d]

    # =========================================================
    # PART 3
    #
    # Add remaining items using their NOMINAL weights.
    #
    # These are items Gamma+1 ... n in the paper.
    # =========================================================

    for j in range(gamma, n):

        cargo = items[j]

        for d in range(
            capacity,
            cargo.weight - 1,
            -1
        ):

            previous = z_dp[
                d - cargo.weight
            ]

            if previous == NEG_INF:
                continue

            new_profit = previous + cargo.profit

            if new_profit > z_dp[d]:

                z_dp[d] = new_profit

                previous_choice = z_choice[
                    d - cargo.weight
                ]

                z_choice[d] = (
                    previous_choice + (j,)
                )

    # =========================================================
    # PART 4
    #
    # Find the best solution.
    #
    # The paper considers:
    #
    # 1. Exactly Gamma uncertain items
    # 2. Fewer than Gamma uncertain items
    # =========================================================

    best_profit = 0
    best_choice = ()

    # Case 1:
    # Exactly Gamma uncertain items
    for d in range(capacity + 1):

        if z_dp[d] > best_profit:

            best_profit = z_dp[d]
            best_choice = z_choice[d]

    # Case 2:
    # Fewer than Gamma uncertain items
    for s in range(1, gamma):

        for d in range(capacity + 1):

            if bar_dp[s][d] > best_profit:

                best_profit = bar_dp[s][d]
                best_choice = bar_choice[s][d]

    # =========================================================
    # Convert indexes back to Cargo objects.
    # =========================================================

    selected_items = [
        items[index]
        for index in best_choice
    ]

    # =========================================================
    # Calculate final result.
    # =========================================================

    total_profit = sum(
        cargo.profit
        for cargo in selected_items
    )

    nominal_weight = sum(
        cargo.weight
        for cargo in selected_items
    )

    # Worst-case additional weight:
    # take the Gamma largest uncertainties.
    uncertainties = sorted(
        [
            cargo.uncertainty
            for cargo in selected_items
        ],
        reverse=True
    )

    robust_weight = (
        nominal_weight
        + sum(uncertainties[:gamma])
    )

    return {
        "selected_items": selected_items,
        "total_profit": total_profit,
        "nominal_weight": nominal_weight,
        "robust_weight": robust_weight,
    }