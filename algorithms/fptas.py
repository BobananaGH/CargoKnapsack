# algorithms/fptas.py

"""
FPTAS for the Robust Knapsack Problem.

Based on Section 5 of:
"Exact solution of the robust knapsack problem"

The algorithm scales item profits and performs Dynamic
Programming over scaled profit values.

Items are first sorted by non-increasing uncertainty.

For a selected solution:
    - the first Gamma selected items use upper weights
    - remaining selected items use nominal weights

This follows the ordered uncertainty structure of the
Robust Knapsack Problem.
"""

import math


INF = float("inf")


def _calculate_robust_weight(selected_items, gamma):
    """
    Calculate the worst-case robust weight.

    Robust weight =
        nominal weight
        + Gamma largest uncertainties.
    """

    nominal_weight = sum(
        cargo.weight
        for cargo in selected_items
    )

    uncertainties = sorted(
        [
            cargo.uncertainty
            for cargo in selected_items
        ],
        reverse=True
    )

    return (
        nominal_weight
        + sum(uncertainties[:gamma])
    )


def _solve_scaled_dp(
    items,
    capacity,
    gamma,
    scaled_profits
):
    """
    Solve the scaled-profit DP.

    State:

        dp[s][p]

    where:

        s = number of selected items among the first
            Gamma uncertain items, capped at Gamma

        p = total scaled profit

    The stored value is the minimum robust weight.

    If s < Gamma:
        selecting another item uses its upper weight.

    If s == Gamma:
        selecting another item uses its nominal weight.

    Returns:
        selected indices
        original total profit
    """

    n = len(items)

    total_scaled_profit = sum(
        scaled_profits
    )

    dp = [
        [INF] * (total_scaled_profit + 1)
        for _ in range(gamma + 1)
    ]

    paths = [
        [None] * (total_scaled_profit + 1)
        for _ in range(gamma + 1)
    ]

    dp[0][0] = 0
    paths[0][0] = []

    for index, cargo in enumerate(items):

        scaled_profit = scaled_profits[index]

        new_dp = [
            row[:]
            for row in dp
        ]

        new_paths = [
            row[:]
            for row in paths
        ]

        # -----------------------------------------------------
        # Before Gamma uncertain items have been selected:
        #
        # Selecting this item means it is one of the
        # worst-case uncertain items, so use max_weight.
        # -----------------------------------------------------

        for s in range(gamma):

            weight = cargo.max_weight

            for p in range(
                total_scaled_profit - scaled_profit,
                -1,
                -1
            ):

                if dp[s][p] == INF:
                    continue

                new_profit = (
                    p + scaled_profit
                )

                new_weight = (
                    dp[s][p]
                    + weight
                )

                if new_weight <= capacity:

                    if (
                        new_weight
                        < new_dp[s + 1][new_profit]
                    ):

                        new_dp[s + 1][new_profit] = (
                            new_weight
                        )

                        old_path = paths[s][p]

                        if old_path is None:
                            new_paths[s + 1][
                                new_profit
                            ] = [index]
                        else:
                            new_paths[s + 1][
                                new_profit
                            ] = (
                                old_path + [index]
                            )

        # -----------------------------------------------------
        # Once Gamma uncertain items have been selected,
        # additional items use nominal weights.
        # -----------------------------------------------------

        if gamma >= 0:

            s = gamma

            for p in range(
                total_scaled_profit - scaled_profit,
                -1,
                -1
            ):

                if dp[s][p] == INF:
                    continue

                new_profit = (
                    p + scaled_profit
                )

                new_weight = (
                    dp[s][p]
                    + cargo.weight
                )

                if new_weight <= capacity:

                    if (
                        new_weight
                        < new_dp[s][new_profit]
                    ):

                        new_dp[s][new_profit] = (
                            new_weight
                        )

                        old_path = paths[s][p]

                        if old_path is None:
                            new_paths[s][new_profit] = [
                                index
                            ]
                        else:
                            new_paths[s][new_profit] = (
                                old_path + [index]
                            )

        dp = new_dp
        paths = new_paths

    # ---------------------------------------------------------
    # Find the largest scaled profit that is feasible.
    # ---------------------------------------------------------

    for p in range(
        total_scaled_profit,
        -1,
        -1
    ):

        for s in range(gamma + 1):

            if dp[s][p] <= capacity:

                selected_indices = paths[s][p]

                if selected_indices is None:
                    selected_indices = []

                total_profit = sum(
                    items[index].profit
                    for index in selected_indices
                )

                return (
                    selected_indices,
                    total_profit
                )

    return [], 0


def _solve_standard_fptas(
    cargo_list,
    capacity,
    epsilon
):
    """
    Standard FPTAS for ordinary 0/1 Knapsack.

    Used when Gamma = 0.
    """

    n = len(cargo_list)

    p_max = max(
        cargo.profit
        for cargo in cargo_list
    )

    if p_max <= 0:
        return []

    scaling_factor = (
        epsilon * p_max / n
    )

    scaled_profits = [
        math.floor(
            cargo.profit / scaling_factor
        )
        for cargo in cargo_list
    ]

    total_scaled_profit = sum(
        scaled_profits
    )

    dp = [
        INF
        for _ in range(
            total_scaled_profit + 1
        )
    ]

    paths = [
        None
        for _ in range(
            total_scaled_profit + 1
        )
    ]

    dp[0] = 0
    paths[0] = []

    for index, cargo in enumerate(
        cargo_list
    ):

        scaled_profit = scaled_profits[index]

        for p in range(
            total_scaled_profit - scaled_profit,
            -1,
            -1
        ):

            if dp[p] == INF:
                continue

            new_profit = (
                p + scaled_profit
            )

            new_weight = (
                dp[p]
                + cargo.weight
            )

            if new_weight <= capacity:

                if new_weight < dp[new_profit]:

                    dp[new_profit] = new_weight

                    old_path = paths[p]

                    if old_path is None:
                        paths[new_profit] = [
                            index
                        ]
                    else:
                        paths[new_profit] = (
                            old_path + [index]
                        )

    for p in range(
        total_scaled_profit,
        -1,
        -1
    ):

        if dp[p] <= capacity:

            if paths[p] is None:
                return []

            return paths[p]

    return []


def fptas(
    cargo_list,
    capacity,
    gamma,
    epsilon=0.2
):
    """
    Solve the Robust Knapsack Problem using FPTAS.

    Parameters:
        cargo_list: list of Cargo objects
        capacity: maximum capacity
        gamma: maximum number of items that may
               reach their upper weight
        epsilon: approximation parameter

    Returns:
        Dictionary containing:
            selected_items
            total_profit
            nominal_weight
            robust_weight
            epsilon
    """

    if epsilon <= 0:
        raise ValueError(
            "epsilon must be greater than 0."
        )

    if not cargo_list or capacity <= 0:
        return {
            "selected_items": [],
            "total_profit": 0,
            "nominal_weight": 0,
            "robust_weight": 0,
            "epsilon": epsilon,
        }

    gamma = min(
        max(gamma, 0),
        len(cargo_list)
    )

    # ---------------------------------------------------------
    # Gamma = 0
    #
    # RKP becomes ordinary 0/1 Knapsack.
    # ---------------------------------------------------------

    if gamma == 0:

        selected_indices = _solve_standard_fptas(
            cargo_list,
            capacity,
            epsilon
        )

        selected_items = [
            cargo_list[index]
            for index in selected_indices
        ]

        total_profit = sum(
            cargo.profit
            for cargo in selected_items
        )

        nominal_weight = sum(
            cargo.weight
            for cargo in selected_items
        )

        return {
            "selected_items": selected_items,
            "total_profit": total_profit,
            "nominal_weight": nominal_weight,
            "robust_weight": nominal_weight,
            "epsilon": epsilon,
        }

    # ---------------------------------------------------------
    # Sort by non-increasing uncertainty.
    # ---------------------------------------------------------

    items = sorted(
        cargo_list,
        key=lambda cargo: cargo.uncertainty,
        reverse=True
    )

    n = len(items)

    # ---------------------------------------------------------
    # Profit scaling.
    #
    # K = epsilon * p_max / n
    #
    # scaled_p_j =
    # floor(p_j / K)
    #
    # Equivalent to:
    #
    # floor(p_j * n / (epsilon * p_max))
    # ---------------------------------------------------------

    p_max = max(
        cargo.profit
        for cargo in items
    )

    if p_max <= 0:
        return {
            "selected_items": [],
            "total_profit": 0,
            "nominal_weight": 0,
            "robust_weight": 0,
            "epsilon": epsilon,
        }

    scaling_factor = (
        epsilon * p_max / n
    )

    scaled_profits = [
        math.floor(
            cargo.profit / scaling_factor
        )
        for cargo in items
    ]

    # ---------------------------------------------------------
    # Solve scaled robust DP.
    # ---------------------------------------------------------

    selected_indices, _ = _solve_scaled_dp(
        items,
        capacity,
        gamma,
        scaled_profits
    )

    selected_items = [
        items[index]
        for index in selected_indices
    ]

    total_profit = sum(
        cargo.profit
        for cargo in selected_items
    )

    nominal_weight = sum(
        cargo.weight
        for cargo in selected_items
    )

    robust_weight = _calculate_robust_weight(
        selected_items,
        gamma
    )

    return {
        "selected_items": selected_items,
        "total_profit": total_profit,
        "nominal_weight": nominal_weight,
        "robust_weight": robust_weight,
        "epsilon": epsilon,
    }