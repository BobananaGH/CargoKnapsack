"""
LLPP algorithm for the Robust Knapsack Problem.

Based on Section 4.2 of:

"Exact solution of the robust knapsack problem"

M. Monaci, U. Pferschy, P. Serafini

The paper describes LLPP as the improved iterative approach
of Lee et al.

The Robust Knapsack Problem can be solved by solving at most

    n - Gamma + 1

ordinary 0/1 Knapsack problems.

Items are first sorted by non-increasing uncertainty:

    delta_j = max_weight_j - weight_j

For each candidate boundary l:

    modified capacity:
        C - Gamma * delta_l

    modified weight of item j:

        weight_j + delta_j - delta_l,   if j <= l
        weight_j,                       if j > l

The special final candidate uses:

    delta_(n+1) = 0

which means all items use their upper weights.

The best solution among these nominal KP instances is the
optimal Robust Knapsack solution.
"""


# ============================================================
# Ordinary 0/1 Knapsack
# ============================================================

def _solve_nominal_kp(items, capacity):
    """
    Solve a standard 0/1 Knapsack Problem.

    Parameters:
        items:
            List of tuples:

                (original_index, cargo, modified_weight)

        capacity:
            Knapsack capacity.

    Returns:
        selected_indices
        total_profit
    """

    if capacity < 0 or not items:
        return [], 0

    n = len(items)

    dp = [
        [0] * (capacity + 1)
        for _ in range(n + 1)
    ]

    # --------------------------------------------------------
    # Forward DP.
    # --------------------------------------------------------

    for i in range(1, n + 1):

        _, cargo, weight = items[i - 1]

        for d in range(capacity + 1):

            # Do not select item.
            dp[i][d] = dp[i - 1][d]

            # Select item.
            if weight <= d:

                candidate = (
                    dp[i - 1][d - weight]
                    + cargo.profit
                )

                if candidate > dp[i][d]:

                    dp[i][d] = candidate

    # --------------------------------------------------------
    # Reconstruct selected items.
    # --------------------------------------------------------

    selected = []

    d = capacity

    for i in range(n, 0, -1):

        if dp[i][d] != dp[i - 1][d]:

            original_index, _, weight = (
                items[i - 1]
            )

            selected.append(original_index)

            d -= weight

    selected.reverse()

    return selected, dp[n][capacity]


# ============================================================
# Robust weight calculation
# ============================================================

def _calculate_robust_weight(
    selected_items,
    gamma
):
    """
    Calculate the worst-case robust weight.

    robust weight =
        nominal weight
        + Gamma largest uncertainties
    """

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
        + sum(
            uncertainties[:gamma]
        )
    )

    return robust_weight


# ============================================================
# LLPP
# ============================================================

def llpp(
    cargo_list,
    capacity,
    gamma
):
    """
    Solve the Robust Knapsack Problem using LLPP.

    LLPP is the iterative nominal-KP approach described
    in Section 4.2 of the paper.

    Parameters:
        cargo_list:
            List of Cargo objects.

        capacity:
            Maximum capacity.

        gamma:
            Maximum number of items whose weights may reach
            their upper bounds.

    Returns:
        Dictionary containing:

            selected_items
            total_profit
            nominal_weight
            robust_weight
    """

    # --------------------------------------------------------
    # Empty input.
    # --------------------------------------------------------

    if not cargo_list or capacity <= 0:

        return {
            "selected_items": [],
            "total_profit": 0,
            "nominal_weight": 0,
            "robust_weight": 0,
        }

    n = len(cargo_list)

    # --------------------------------------------------------
    # Normalize Gamma.
    # --------------------------------------------------------

    gamma = min(
        max(gamma, 0),
        n
    )

    # ========================================================
    # Gamma = 0
    # ========================================================
    #
    # No uncertainty is active.
    #
    # Therefore solve an ordinary nominal KP.
    # ========================================================

    if gamma == 0:

        items = [
            (
                index,
                cargo,
                cargo.weight
            )
            for index, cargo
            in enumerate(cargo_list)
        ]

        selected_indices, _ = _solve_nominal_kp(
            items,
            capacity
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
        }

    # ========================================================
    # Sort by non-increasing uncertainty.
    #
    # delta_j =
    #     max_weight_j - weight_j
    # ========================================================

    sorted_items = sorted(
        enumerate(cargo_list),
        key=lambda pair: pair[1].uncertainty,
        reverse=True
    )

    # ========================================================
    # Best solution found so far.
    # ========================================================

    best_profit = 0
    best_selected = []

    # ========================================================
    # LLPP candidate values of l
    #
    # l = Gamma, ..., n - 1
    #
    # plus the dummy candidate:
    #
    # l = n
    #
    # where:
    #
    # delta_(n+1) = 0
    #
    # Therefore the number of nominal KP instances is:
    #
    #     n - Gamma + 1
    # ========================================================

    for l in range(gamma, n + 1):

        # ----------------------------------------------------
        # Candidate uncertainty delta_l.
        #
        # For l = n we use the dummy value 0.
        # ----------------------------------------------------

        if l == n:

            delta_l = 0

        else:

            delta_l = (
                sorted_items[l][1].uncertainty
            )

        # ----------------------------------------------------
        # Modified capacity:
        #
        # C - Gamma * delta_l
        # ----------------------------------------------------

        modified_capacity = (
            capacity
            - gamma * delta_l
        )

        # ----------------------------------------------------
        # If modified capacity is negative,
        # this candidate cannot produce a solution.
        # ----------------------------------------------------

        if modified_capacity < 0:

            continue

        # ----------------------------------------------------
        # Construct the ordinary KP instance.
        #
        # For j <= l:
        #
        #   w'_j =
        #       w_j + delta_j - delta_l
        #
        # For j > l:
        #
        #   w'_j = w_j
        # ----------------------------------------------------

        kp_items = []

        for j, (original_index, cargo) in enumerate(
            sorted_items
        ):

            if j <= l:

                modified_weight = (
                    cargo.weight
                    + cargo.uncertainty
                    - delta_l
                )

            else:

                modified_weight = cargo.weight

            # ------------------------------------------------
            # Safety:
            #
            # Due to sorting, for j <= l:
            #
            # delta_j >= delta_l
            #
            # so modified_weight should never be negative.
            # ------------------------------------------------

            if modified_weight < 0:

                raise RuntimeError(
                    "Invalid LLPP modified weight."
                )

            kp_items.append(
                (
                    original_index,
                    cargo,
                    modified_weight
                )
            )

        # ----------------------------------------------------
        # Solve the ordinary KP.
        # ----------------------------------------------------

        selected_indices, profit = (
            _solve_nominal_kp(
                kp_items,
                modified_capacity
            )
        )

        # ----------------------------------------------------
        # Convert original indexes back to Cargo objects.
        # ----------------------------------------------------

        selected_items = [
            cargo_list[index]
            for index in selected_indices
        ]

        # ----------------------------------------------------
        # Check the ORIGINAL robust constraint.
        #
        # This is useful as a final correctness check.
        # ----------------------------------------------------

        robust_weight = _calculate_robust_weight(
            selected_items,
            gamma
        )

        if robust_weight > capacity:

            continue

        # ----------------------------------------------------
        # Keep the best candidate.
        # ----------------------------------------------------

        if profit > best_profit:

            best_profit = profit
            best_selected = selected_items

    # ========================================================
    # Final result
    # ========================================================

    total_profit = sum(
        cargo.profit
        for cargo in best_selected
    )

    nominal_weight = sum(
        cargo.weight
        for cargo in best_selected
    )

    robust_weight = _calculate_robust_weight(
        best_selected,
        gamma
    )

    # --------------------------------------------------------
    # Final safety check.
    # --------------------------------------------------------

    if robust_weight > capacity:

        raise RuntimeError(
            "Internal error: LLPP returned "
            "an infeasible robust solution."
        )

    return {
        "selected_items": best_selected,
        "total_profit": total_profit,
        "nominal_weight": nominal_weight,
        "robust_weight": robust_weight,
    }