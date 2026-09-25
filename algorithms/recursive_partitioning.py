"""
Recursive Partitioning algorithm for the Robust Knapsack Problem.

Based on:

M. Monaci, U. Pferschy, P. Serafini,
"Exact solution of the robust knapsack problem"

This implementation follows the recursive solution-set
reconstruction scheme presented in Section 3 and Figure 3
of the paper.

Main structure:

    Solve_RKP(c, Gamma, N)
        |
        v
    obtain z*, c*, k*
        |
        v
    partition N into N1 and N2
        |
        +-------------------------------+
        |                               |
    k* >= Gamma                      k* < Gamma
        |                               |
        v                               v
    RKP(N1, Gamma)                  E-kKP(N1, k*)
    KP(N2)                          RKP(N2, Gamma-k*)
        |                               |
        +---------- capacity split -----+
                        |
                        v
                    recurse

The items must be sorted by non-increasing uncertainty:

    uncertainty_j = max_weight_j - weight_j

The Section 3 recursive reconstruction uses:

    - Solve_RKP
    - ordinary nominal KP
    - E-kKP (exactly k selected items)
    - recursive partitioning

The dominance/robust DP is used to determine:

    z* = optimal profit
    c* = capacity associated with z*
    k* = number of selected items from the first partition

This implementation keeps additional reconstruction information
where necessary, but the recursive structure follows Figure 3.

Complexity of the underlying Robust DP:

    Time:  O(Gamma * n * C)
    Space: O(n + Gamma * C)
"""

NEG_INF = float("-inf")


# ============================================================
# Solve_RKP
# ============================================================

def _solve_rkp_values(
    items,
    capacity,
    gamma
):
    """
    Solve_RKP from the paper.

    Returns the best robust-knapsack profit for every exact
    capacity d = 0 ... capacity.

    Also returns:

        first_half_count[d]
            Number of selected items from the first half.

        total_selected_count[d]
            Total number of selected items.

    The first-half counter corresponds to the k(d, Gamma)
    counter used by the recursive partitioning procedure
    in Section 3.

    DP state:

        dp[s][d]

    where:

        s = number of selected items assigned increased/max weight
        d = exact robust weight

    Transitions:

        Heavy:

            (d - max_weight, s - 1)
                -> (d, s)

        Light:

            (d - nominal_weight, Gamma)
                -> (d, Gamma)

    Once Gamma increased-weight items have been selected,
    additional selected items use their nominal weights.
    """

    n = len(items)

    gamma = min(
        max(gamma, 0),
        n
    )

    first_half_size = (
        n + 1
    ) // 2

    # --------------------------------------------------------
    # DP arrays.
    #
    # dp[s][d]
    #
    # s = number of increased-weight items
    # d = exact robust weight
    # --------------------------------------------------------

    dp = [
        [NEG_INF] * (capacity + 1)
        for _ in range(gamma + 1)
    ]

    first_half_count = [
        [0] * (capacity + 1)
        for _ in range(gamma + 1)
    ]

    total_selected_count = [
        [0] * (capacity + 1)
        for _ in range(gamma + 1)
    ]

    # Empty solution.
    dp[0][0] = 0

    # --------------------------------------------------------
    # Process items.
    # --------------------------------------------------------

    for index, cargo in enumerate(items):

        # Copy previous iteration so that each item
        # can be selected at most once.
        previous_dp = [
            row[:]
            for row in dp
        ]

        previous_first_count = [
            row[:]
            for row in first_half_count
        ]

        previous_total_count = [
            row[:]
            for row in total_selected_count
        ]

        # ----------------------------------------------------
        # Each state can:
        #
        # 1. Skip the item.
        # 2. Take the item as an increased-weight item.
        # 3. Take the item with nominal weight once Gamma
        #    increased-weight items have already been selected.
        # ----------------------------------------------------

        for s in range(gamma + 1):

            for d in range(capacity + 1):

                # ------------------------------------------------
                # Option 1: skip item.
                # ------------------------------------------------

                dp[s][d] = previous_dp[s][d]

                first_half_count[s][d] = (
                    previous_first_count[s][d]
                )

                total_selected_count[s][d] = (
                    previous_total_count[s][d]
                )

                # ------------------------------------------------
                # Option 2: increased/heavy transition.
                # ------------------------------------------------

                if s > 0:

                    if cargo.max_weight <= d:

                        previous = previous_dp[
                            s - 1
                        ][
                            d - cargo.max_weight
                        ]

                        if previous != NEG_INF:

                            candidate = (
                                previous
                                + cargo.profit
                            )

                            candidate_first_count = (
                                previous_first_count[
                                    s - 1
                                ][
                                    d - cargo.max_weight
                                ]
                                + (
                                    1
                                    if index < first_half_size
                                    else 0
                                )
                            )

                            candidate_total_count = (
                                previous_total_count[
                                    s - 1
                                ][
                                    d - cargo.max_weight
                                ]
                                + 1
                            )

                            if (
                                candidate > dp[s][d]
                                or (
                                    candidate == dp[s][d]
                                    and candidate_total_count
                                    > total_selected_count[s][d]
                                )
                            ):

                                dp[s][d] = candidate

                                first_half_count[s][d] = (
                                    candidate_first_count
                                )

                                total_selected_count[s][d] = (
                                    candidate_total_count
                                )

                # ------------------------------------------------
                # Option 3: nominal/light transition.
                #
                # This is possible only after Gamma
                # increased-weight items have been selected.
                # ------------------------------------------------

                if s == gamma:

                    if cargo.weight <= d:

                        previous = previous_dp[
                            gamma
                        ][
                            d - cargo.weight
                        ]

                        if previous != NEG_INF:

                            candidate = (
                                previous
                                + cargo.profit
                            )

                            candidate_first_count = (
                                previous_first_count[
                                    gamma
                                ][
                                    d - cargo.weight
                                ]
                                + (
                                    1
                                    if index < first_half_size
                                    else 0
                                )
                            )

                            candidate_total_count = (
                                previous_total_count[
                                    gamma
                                ][
                                    d - cargo.weight
                                ]
                                + 1
                            )

                            if (
                                candidate > dp[s][d]
                                or (
                                    candidate == dp[s][d]
                                    and candidate_total_count
                                    > total_selected_count[s][d]
                                )
                            ):

                                dp[s][d] = candidate

                                first_half_count[s][d] = (
                                    candidate_first_count
                                )

                                total_selected_count[s][d] = (
                                    candidate_total_count
                                )

    # --------------------------------------------------------
    # For every capacity d, select the best state over
    # s = 0 ... Gamma.
    #
    # The paper allows a solution to contain fewer than
    # Gamma selected items.
    # --------------------------------------------------------

    best_profit = [
        NEG_INF
        for _ in range(capacity + 1)
    ]

    best_first_count = [
        0
        for _ in range(capacity + 1)
    ]

    best_total_count = [
        0
        for _ in range(capacity + 1)
    ]

    for d in range(capacity + 1):

        for s in range(gamma + 1):

            value = dp[s][d]

            if value == NEG_INF:
                continue

            if (
                value > best_profit[d]
                or (
                    value == best_profit[d]
                    and total_selected_count[s][d]
                    > best_total_count[d]
                )
            ):

                best_profit[d] = value

                best_first_count[d] = (
                    first_half_count[s][d]
                )

                best_total_count[d] = (
                    total_selected_count[s][d]
                )

    return (
        best_profit,
        best_first_count,
        best_total_count,
    )


# ============================================================
# Standard KP values
# ============================================================

def _solve_kp_values(
    items,
    capacity
):
    """
    Solve the ordinary 0/1 Knapsack Problem.

    All selected items use their nominal weights.

    Returns the best profit for every exact capacity.
    """

    dp = [
        NEG_INF
        for _ in range(capacity + 1)
    ]

    dp[0] = 0

    for cargo in items:

        # Reverse iteration ensures 0/1 behavior.
        for d in range(
            capacity,
            cargo.weight - 1,
            -1
        ):

            previous = dp[
                d - cargo.weight
            ]

            if previous == NEG_INF:
                continue

            candidate = (
                previous
                + cargo.profit
            )

            if candidate > dp[d]:

                dp[d] = candidate

    return dp


# ============================================================
# Standard KP reconstruction
# ============================================================

def _solve_kp_solution(
    items,
    capacity
):
    """
    Solve ordinary KP for one exact capacity and reconstruct
    the selected item indices.
    """

    n = len(items)

    dp = [
        [NEG_INF] * (capacity + 1)
        for _ in range(n + 1)
    ]

    dp[0][0] = 0

    for i in range(
        1,
        n + 1
    ):

        cargo = items[i - 1]

        for d in range(
            capacity + 1
        ):

            # Skip.
            dp[i][d] = (
                dp[i - 1][d]
            )

            # Take.
            if cargo.weight <= d:

                previous = dp[
                    i - 1
                ][
                    d - cargo.weight
                ]

                if previous != NEG_INF:

                    candidate = (
                        previous
                        + cargo.profit
                    )

                    if candidate > dp[i][d]:

                        dp[i][d] = candidate

    if dp[n][capacity] == NEG_INF:

        return (
            [],
            NEG_INF
        )

    selected = []

    i = n
    d = capacity

    while i > 0:

        # Item was not selected.
        if (
            dp[i][d]
            == dp[i - 1][d]
        ):

            i -= 1
            continue

        # Item was selected.
        selected.append(
            i - 1
        )

        d -= items[i - 1].weight
        i -= 1

    selected.reverse()

    return (
        selected,
        dp[n][capacity]
    )


# ============================================================
# E-kKP values
# ============================================================

def _solve_exact_k_kp_values(
    items,
    capacity,
    k
):
    """
    Solve E-kKP from Section 3.

    Exactly k items must be selected.

    All selected items use their increased/max weights.

    This corresponds to the E-kKP subproblem in Figure 3.
    """

    n = len(items)

    if k < 0 or k > n:

        return [
            NEG_INF
            for _ in range(capacity + 1)
        ]

    dp = [
        [NEG_INF] * (capacity + 1)
        for _ in range(k + 1)
    ]

    dp[0][0] = 0

    for cargo in items:

        for selected_count in range(
            k,
            0,
            -1
        ):

            for d in range(
                capacity,
                cargo.max_weight - 1,
                -1
            ):

                previous = dp[
                    selected_count - 1
                ][
                    d - cargo.max_weight
                ]

                if previous == NEG_INF:
                    continue

                candidate = (
                    previous
                    + cargo.profit
                )

                if candidate > dp[
                    selected_count
                ][d]:

                    dp[
                        selected_count
                    ][d] = candidate

    return dp[k]


# ============================================================
# E-kKP reconstruction
# ============================================================

def _solve_exact_k_kp_solution(
    items,
    capacity,
    k
):
    """
    Solve E-kKP for one exact capacity and reconstruct
    the selected item indices.

    Exactly k items are selected.
    """

    n = len(items)

    if k < 0 or k > n:

        return (
            [],
            NEG_INF
        )

    dp = [
        [
            [NEG_INF] * (capacity + 1)
            for _ in range(k + 1)
        ]
        for _ in range(n + 1)
    ]

    dp[0][0][0] = 0

    for i in range(
        1,
        n + 1
    ):

        cargo = items[i - 1]

        for selected_count in range(
            k + 1
        ):

            for d in range(
                capacity + 1
            ):

                # Skip.
                dp[i][selected_count][d] = (
                    dp[i - 1][selected_count][d]
                )

                # Take.
                if (
                    selected_count > 0
                    and cargo.max_weight <= d
                ):

                    previous = dp[
                        i - 1
                    ][
                        selected_count - 1
                    ][
                        d - cargo.max_weight
                    ]

                    if previous != NEG_INF:

                        candidate = (
                            previous
                            + cargo.profit
                        )

                        if (
                            candidate
                            > dp[i][selected_count][d]
                        ):

                            dp[
                                i
                            ][
                                selected_count
                            ][
                                d
                            ] = candidate

    value = dp[n][k][capacity]

    if value == NEG_INF:

        return (
            [],
            NEG_INF
        )

    selected = []

    i = n
    d = capacity
    selected_count = k

    while i > 0:

        # Item was not selected.
        if (
            dp[i][selected_count][d]
            == dp[i - 1][selected_count][d]
        ):

            i -= 1
            continue

        # Item was selected.
        selected.append(
            i - 1
        )

        d -= items[i - 1].max_weight
        selected_count -= 1
        i -= 1

    selected.reverse()

    return (
        selected,
        value
    )


# ============================================================
# Recursive Partitioning
# ============================================================

def _recursive_reconstruct(
    items,
    capacity,
    gamma,
    z_star,
    k_star
):
    """
    Reconstruct the solution according to Figure 3.

    Parameters
    ----------
    items:
        Current item set N.

    capacity:
        Current capacity c*.

    gamma:
        Current robustness budget Gamma.

    z_star:
        Optimal profit z* associated with this recursive
        subproblem.

    k_star:
        Counter k* associated with z*.

    Returns
    -------
    selected_indices:
        Selected indices relative to the current item list.

    total_profit:
        Reconstructed optimal profit.

    The important difference from the previous implementation
    is that z_star and k_star are passed into the recursive
    call instead of being recomputed. This follows the
    recursive state passed by Figure 3.
    """

    n = len(items)

    # --------------------------------------------------------
    # Empty set.
    # --------------------------------------------------------

    if n == 0:

        return (
            [],
            0
        )

    # --------------------------------------------------------
    # Base case.
    #
    # Figure 3 terminates when |N| = 1.
    # --------------------------------------------------------

    if n == 1:

        cargo = items[0]

        if z_star <= 0:

            return (
                [],
                0
            )

        # For a single item:
        #
        # Gamma = 0:
        #     nominal weight
        #
        # Gamma >= 1:
        #     max weight
        #
        # Gamma has already been normalized to <= n.
        if gamma == 0:

            required_weight = (
                cargo.weight
            )

        else:

            required_weight = (
                cargo.max_weight
            )

        if (
            required_weight <= capacity
            and cargo.profit == z_star
        ):

            return (
                [0],
                cargo.profit
            )

        raise RuntimeError(
            "Could not reconstruct the base-case "
            "recursive solution."
        )

    gamma = min(
        max(gamma, 0),
        n
    )

    # --------------------------------------------------------
    # Partition N into:
    #
    # N1 = first ceil(n / 2) items
    # N2 = remaining items
    # --------------------------------------------------------

    split = (
        n + 1
    ) // 2

    N1 = items[:split]
    N2 = items[split:]

    # --------------------------------------------------------
    # Case 1:
    #
    # k* >= Gamma
    #
    # Figure 3:
    #
    # Solve RKP on N1 with Gamma
    # Solve KP on N2
    # Find c1 + c2 = c*
    # Recurse on N1
    # --------------------------------------------------------

    if k_star >= gamma:

        # ----------------------------------------------------
        # Solve RKP on N1 for every capacity.
        # ----------------------------------------------------

        (
            z1,
            first_counts_1,
            _
        ) = _solve_rkp_values(
            N1,
            capacity,
            gamma
        )

        # ----------------------------------------------------
        # Solve ordinary KP on N2.
        # ----------------------------------------------------

        z2 = _solve_kp_values(
            N2,
            capacity
        )

        c1 = None
        c2 = None

        # ----------------------------------------------------
        # Find:
        #
        # c1 + c2 = c*
        #
        # z1(c1) + z2(c2) = z*
        # ----------------------------------------------------

        for candidate_c1 in range(
            capacity + 1
        ):

            candidate_c2 = (
                capacity
                - candidate_c1
            )

            if (
                z1[candidate_c1] == NEG_INF
                or z2[candidate_c2] == NEG_INF
            ):

                continue

            if (
                z1[candidate_c1]
                + z2[candidate_c2]
                == z_star
            ):

                c1 = candidate_c1
                c2 = candidate_c2

                break

        if c1 is None:

            raise RuntimeError(
                "Could not find the capacity split "
                "for the k* >= Gamma recursive case."
            )

        # ----------------------------------------------------
        # Figure 3:
        #
        # k1* is the counter associated with z1(c1).
        # ----------------------------------------------------

        k1_star = first_counts_1[c1]

        # ----------------------------------------------------
        # Recurse on N1 using the actual z1(c1) and k1*.
        # ----------------------------------------------------

        selected_N1, profit_N1 = (
            _recursive_reconstruct(
                N1,
                c1,
                gamma,
                z1[c1],
                k1_star
            )
        )

        # ----------------------------------------------------
        # Reconstruct KP solution for N2.
        # ----------------------------------------------------

        selected_N2, profit_N2 = (
            _solve_kp_solution(
                N2,
                c2
            )
        )

        if (
            profit_N1
            + profit_N2
            != z_star
        ):

            raise RuntimeError(
                "Recursive reconstruction produced "
                "an incorrect profit."
            )

        # ----------------------------------------------------
        # Convert N2-local indices to current-N indices.
        # ----------------------------------------------------

        selected = (
            selected_N1
            + [
                split + index
                for index in selected_N2
            ]
        )

        return (
            selected,
            z_star
        )

    # --------------------------------------------------------
    # Case 2:
    #
    # k* < Gamma
    #
    # Figure 3:
    #
    # E-kKP on N1 with k*
    # RKP on N2 with Gamma-k*
    # Find c1 + c2 = c*
    # Recurse on N2
    # --------------------------------------------------------

    remaining_gamma = (
        gamma - k_star
    )

    # --------------------------------------------------------
    # Solve E-kKP on N1.
    # --------------------------------------------------------

    z1 = _solve_exact_k_kp_values(
        N1,
        capacity,
        k_star
    )

    # --------------------------------------------------------
    # Solve RKP on N2.
    # --------------------------------------------------------

    (
        z2,
        first_counts_2,
        _
    ) = _solve_rkp_values(
        N2,
        capacity,
        remaining_gamma
    )

    c1 = None
    c2 = None

    # --------------------------------------------------------
    # Find:
    #
    # c1 + c2 = c*
    #
    # z1(c1) + z2(c2) = z*
    # --------------------------------------------------------

    for candidate_c1 in range(
        capacity + 1
    ):

        candidate_c2 = (
            capacity
            - candidate_c1
        )

        if (
            z1[candidate_c1] == NEG_INF
            or z2[candidate_c2] == NEG_INF
        ):

            continue

        if (
            z1[candidate_c1]
            + z2[candidate_c2]
            == z_star
        ):

            c1 = candidate_c1
            c2 = candidate_c2

            break

    if c1 is None:

        raise RuntimeError(
            "Could not find the capacity split "
            "for the k* < Gamma recursive case."
        )

    # --------------------------------------------------------
    # Reconstruct E-kKP solution for N1.
    # --------------------------------------------------------

    selected_N1, profit_N1 = (
        _solve_exact_k_kp_solution(
            N1,
            c1,
            k_star
        )
    )

    # --------------------------------------------------------
    # Figure 3:
    #
    # k2* is the counter associated with z2(c2).
    # --------------------------------------------------------

    k2_star = first_counts_2[c2]

    # --------------------------------------------------------
    # Recurse on N2 using:
    #
    # z2(c2)
    # k2*
    # c2
    # Gamma - k*
    # --------------------------------------------------------

    selected_N2, profit_N2 = (
        _recursive_reconstruct(
            N2,
            c2,
            remaining_gamma,
            z2[c2],
            k2_star
        )
    )

    if (
        profit_N1
        + profit_N2
        != z_star
    ):

        raise RuntimeError(
            "Recursive reconstruction produced "
            "an incorrect profit."
        )

    # --------------------------------------------------------
    # Convert N2-local indices to current-N indices.
    # --------------------------------------------------------

    selected = (
        selected_N1
        + [
            split + index
            for index in selected_N2
        ]
    )

    return (
        selected,
        z_star
    )


# ============================================================
# Public API
# ============================================================

def recursive_partitioning(
    cargo_list,
    capacity,
    gamma
):
    """
    Solve the Robust Knapsack Problem using the recursive
    partitioning solution-set reconstruction method from
    Section 3 of the paper.

    Parameters
    ----------
    cargo_list:
        List of Cargo objects.

    capacity:
        Maximum robust capacity.

    gamma:
        Robustness budget Gamma.

    Returns
    -------
    dict

        {
            "selected_items": [...],
            "total_profit": ...,
            "nominal_weight": ...,
            "robust_weight": ...
        }
    """

    # --------------------------------------------------------
    # Empty input.
    # --------------------------------------------------------

    if not cargo_list:

        return {
            "selected_items": [],
            "total_profit": 0,
            "nominal_weight": 0,
            "robust_weight": 0,
        }

    # --------------------------------------------------------
    # Invalid/non-positive capacity.
    # --------------------------------------------------------

    if capacity <= 0:

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
        len(cargo_list)
    )

    # --------------------------------------------------------
    # Sort by non-increasing uncertainty.
    #
    # This ordering is required by the robust-knapsack
    # formulation used by the paper.
    # --------------------------------------------------------

    items = sorted(
        cargo_list,
        key=lambda cargo: cargo.uncertainty,
        reverse=True
    )

    # --------------------------------------------------------
    # Initial Solve_RKP.
    #
    # This corresponds to the first step of Figure 3:
    #
    # Solve_RKP(c, Gamma, N)
    #
    # Determine:
    #
    # z* = optimal profit
    # c* = capacity associated with z*
    # k* = counter associated with z*
    # --------------------------------------------------------

    (
        values,
        first_counts,
        _
    ) = _solve_rkp_values(
        items,
        capacity,
        gamma
    )

    z_star = NEG_INF
    c_star = 0
    k_star = 0

    for d in range(
        capacity + 1
    ):

        value = values[d]

        if value > z_star:

            z_star = value
            c_star = d
            k_star = first_counts[d]

    # --------------------------------------------------------
    # No feasible positive-profit solution.
    # --------------------------------------------------------

    if z_star == NEG_INF or z_star <= 0:

        return {
            "selected_items": [],
            "total_profit": 0,
            "nominal_weight": 0,
            "robust_weight": 0,
        }

    # --------------------------------------------------------
    # Recursive solution-set reconstruction.
    #
    # Pass z*, c*, and k* explicitly.
    # --------------------------------------------------------

    selected_indices, best_profit = (
        _recursive_reconstruct(
            items,
            c_star,
            gamma,
            z_star,
            k_star
        )
    )

    # --------------------------------------------------------
    # Convert indices back to Cargo objects.
    # --------------------------------------------------------

    selected_items = [
        items[index]
        for index in selected_indices
    ]

    # --------------------------------------------------------
    # Calculate nominal weight.
    # --------------------------------------------------------

    nominal_weight = sum(
        cargo.weight
        for cargo in selected_items
    )

    # --------------------------------------------------------
    # Calculate robust weight.
    #
    # nominal weight +
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

    # --------------------------------------------------------
    # Final feasibility verification.
    # --------------------------------------------------------

    if robust_weight > capacity:

        raise RuntimeError(
            "Internal error: recursive partitioning "
            "reconstructed an infeasible solution."
        )

    # --------------------------------------------------------
    # Final profit verification.
    # --------------------------------------------------------

    actual_profit = sum(
        cargo.profit
        for cargo in selected_items
    )

    if actual_profit != best_profit:

        raise RuntimeError(
            "Internal error: reconstructed solution "
            "profit does not match the recursive DP result."
        )

    # --------------------------------------------------------
    # Final result.
    # --------------------------------------------------------

    return {
        "selected_items": selected_items,
        "total_profit": actual_profit,
        "nominal_weight": nominal_weight,
        "robust_weight": robust_weight,
    }