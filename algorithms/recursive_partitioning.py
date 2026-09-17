"""
Recursive Partitioning algorithm for the Robust Knapsack Problem.

Based on:

"Exact solution of the robust knapsack problem"

M. Monaci, U. Pferschy, P. Serafini

This implementation follows the recursive solution-set reconstruction
scheme presented in Section 3 and Figure 3 of the paper.

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

The paper's Section 3 uses:

    - Solve_RKP
    - ordinary nominal KP
    - E-kKP (exactly k selected items)
    - recursive partitioning

Complexity stated in the paper:

    Time:  O(Gamma * n * C)
    Space: O(n + Gamma * C)

This implementation keeps additional information during the
reconstruction phase to make the selected solution explicit.
"""

NEG_INF = float("-inf")


# ============================================================
# Solve_RKP
# ============================================================

def _solve_rkp_values(items, capacity, gamma):
    """
    Solve_RKP from the paper.

    Returns the best robust-knapsack profit for every exact
    capacity d = 0 ... capacity.

    Also returns:

        first_half_count[d]
            Number of selected items from the first half of items.

        total_selected_count[d]
            Total number of selected items.

    The first-half counter is the k(d, Gamma) counter described
    in Section 3 of the paper.

    The DP states correspond to the graph in Section 2:

        state (d, s)

    where s is the number of selected items that have been
    assigned their upper/max weight.

    Transitions:

        Heavy:
            (d - max_weight, s - 1)
                -> (d, s)

        Light:
            (d - nominal_weight, Gamma)
                -> (d, Gamma)

    Once Gamma heavy items have been selected, later items
    can be inserted using nominal weight.
    """

    n = len(items)

    gamma = min(
        max(gamma, 0),
        n
    )

    first_half_size = (n + 1) // 2

    # --------------------------------------------------------
    # DP arrays.
    #
    # dp[s][d]
    #
    # s = number of heavy/increased-weight items
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

        # We need the previous iteration because one item
        # cannot be selected twice.
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
        # Each state can either:
        #
        # 1. Skip the item.
        # 2. Take it as a heavy item.
        # 3. Take it as a light item if Gamma heavy items
        #    have already been selected.
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
                # Option 2: heavy transition.
                #
                # Previous state has s - 1 heavy items.
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
                # Option 3: light transition.
                #
                # Once Gamma heavy items have been selected,
                # additional items use nominal weight.
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
    # The paper allows solutions with fewer than Gamma
    # selected items. Therefore take the best state over
    # s = 0 ... Gamma.
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
# Robust DP with minimum cardinality
# ============================================================

def _solve_rkp_with_minimum_items(
    items,
    capacity,
    gamma,
    minimum_items
):
    """
    Solve an RKP subproblem while requiring at least
    minimum_items selected items.

    This is used in the k* >= Gamma branch.

    The requirement is necessary when reconstructing the
    particular parent solution described by Lemma 3.

    Returns:

        best_profit[d]
        first_half_count[d]
    """

    n = len(items)

    gamma = min(
        max(gamma, 0),
        n
    )

    first_half_size = (n + 1) // 2

    # --------------------------------------------------------
    # State:
    #
    # dp[s][k][d]
    #
    # s = heavy items
    # k = total selected items
    # d = exact weight
    #
    # This extra cardinality information is only used during
    # reconstruction of the recursive solution.
    # --------------------------------------------------------

    dp = [
        [
            [NEG_INF] * (capacity + 1)
            for _ in range(n + 1)
        ]
        for _ in range(gamma + 1)
    ]

    first_count = [
        [
            [0] * (capacity + 1)
            for _ in range(n + 1)
        ]
        for _ in range(gamma + 1)
    ]

    dp[0][0][0] = 0

    for index, cargo in enumerate(items):

        previous_dp = [
            [
                row[:]
                for row in stage
            ]
            for stage in dp
        ]

        previous_first_count = [
            [
                row[:]
                for row in stage
            ]
            for stage in first_count
        ]

        for s in range(gamma + 1):

            for k in range(n + 1):

                for d in range(capacity + 1):

                    dp[s][k][d] = previous_dp[s][k][d]

                    first_count[s][k][d] = (
                        previous_first_count[s][k][d]
                    )

                    # ------------------------------------------------
                    # Heavy transition.
                    # ------------------------------------------------

                    if s > 0 and k > 0:

                        if cargo.max_weight <= d:

                            previous = previous_dp[
                                s - 1
                            ][
                                k - 1
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
                                        k - 1
                                    ][
                                        d - cargo.max_weight
                                    ]
                                    + (
                                        1
                                        if index < first_half_size
                                        else 0
                                    )
                                )

                                if (
                                    candidate
                                    > dp[s][k][d]
                                ):

                                    dp[s][k][d] = (
                                        candidate
                                    )

                                    first_count[s][k][d] = (
                                        candidate_first_count
                                    )

                    # ------------------------------------------------
                    # Light transition.
                    # ------------------------------------------------

                    if s == gamma and k > 0:

                        if cargo.weight <= d:

                            previous = previous_dp[
                                gamma
                            ][
                                k - 1
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
                                        k - 1
                                    ][
                                        d - cargo.weight
                                    ]
                                    + (
                                        1
                                        if index < first_half_size
                                        else 0
                                    )
                                )

                                if (
                                    candidate
                                    > dp[s][k][d]
                                ):

                                    dp[s][k][d] = (
                                        candidate
                                    )

                                    first_count[s][k][d] = (
                                        candidate_first_count
                                    )

    # --------------------------------------------------------
    # Find best state with at least minimum_items.
    # --------------------------------------------------------

    best_profit = [
        NEG_INF
        for _ in range(capacity + 1)
    ]

    best_first_count = [
        0
        for _ in range(capacity + 1)
    ]

    for d in range(capacity + 1):

        for s in range(gamma + 1):

            for k in range(
                minimum_items,
                n + 1
            ):

                value = dp[s][k][d]

                if value > best_profit[d]:

                    best_profit[d] = value

                    best_first_count[d] = (
                        first_count[s][k][d]
                    )

    return (
        best_profit,
        best_first_count,
    )


# ============================================================
# Standard KP values
# ============================================================

def _solve_kp_values(items, capacity):
    """
    Standard 0/1 Knapsack.

    Returns the best profit for every exact weight.
    """

    dp = [
        NEG_INF
        for _ in range(capacity + 1)
    ]

    dp[0] = 0

    for cargo in items:

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
    Re-run ordinary KP for one capacity and reconstruct
    the selected item indices.
    """

    n = len(items)

    dp = [
        [NEG_INF] * (capacity + 1)
        for _ in range(n + 1)
    ]

    dp[0][0] = 0

    for i in range(1, n + 1):

        cargo = items[i - 1]

        for d in range(capacity + 1):

            # Skip.
            dp[i][d] = dp[i - 1][d]

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

        return [], NEG_INF

    selected = []

    i = n
    d = capacity

    while i > 0:

        if dp[i][d] == dp[i - 1][d]:

            i -= 1
            continue

        selected.append(i - 1)

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
    E-kKP from Section 3.

    Exactly k items must be selected.

    All items use their increased/max weights.

    This corresponds to equation (6) in the paper.
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
    Re-run E-kKP for a particular capacity and reconstruct
    the selected items.

    Exactly k items are selected.
    """

    n = len(items)

    dp = [
        [
            [NEG_INF] * (capacity + 1)
            for _ in range(k + 1)
        ]
        for _ in range(n + 1)
    ]

    dp[0][0][0] = 0

    for i in range(1, n + 1):

        cargo = items[i - 1]

        for selected_count in range(k + 1):

            for d in range(capacity + 1):

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

        return [], NEG_INF

    selected = []

    i = n
    d = capacity
    selected_count = k

    while i > 0:

        if (
            dp[i][selected_count][d]
            == dp[i - 1][selected_count][d]
        ):

            i -= 1
            continue

        selected.append(i - 1)

        d -= items[i - 1].max_weight
        selected_count -= 1
        i -= 1

    selected.reverse()

    return selected, value


# ============================================================
# Recursive Partitioning
# ============================================================

def _recursive_reconstruct(
    items,
    capacity,
    gamma,
):
    """
    Figure 3 recursive reconstruction.

    Returns:

        selected_indices
        total_profit
    """

    n = len(items)

    # --------------------------------------------------------
    # Empty set.
    # --------------------------------------------------------

    if n == 0:

        return [], 0

    # --------------------------------------------------------
    # Base case from Figure 3.
    # --------------------------------------------------------

    if n == 1:

        cargo = items[0]

        if gamma == 0:

            required_weight = cargo.weight

        else:

            required_weight = cargo.max_weight

        if required_weight <= capacity:

            return [0], cargo.profit

        return [], 0

    gamma = min(
        max(gamma, 0),
        n
    )

    # --------------------------------------------------------
    # Step 1:
    #
    # Solve_RKP(c, Gamma, N)
    #
    # Determine z*, c*, k*.
    # --------------------------------------------------------

    values, first_counts, total_counts = (
        _solve_rkp_values(
            items,
            capacity,
            gamma
        )
    )

    z_star = 0
    c_star = 0
    k_star = 0

    for d in range(capacity + 1):

        value = values[d]

        if value > z_star:

            z_star = value
            c_star = d
            k_star = first_counts[d]

    # No positive-profit solution.
    if z_star <= 0:

        return [], 0

    # --------------------------------------------------------
    # Step 2:
    #
    # Partition:
    #
    # N1 = first ceil(n/2)
    # N2 = remaining items
    # --------------------------------------------------------

    split = (n + 1) // 2

    N1 = items[:split]
    N2 = items[split:]

    # --------------------------------------------------------
    # Case 1:
    #
    # k* >= Gamma
    #
    # RKP on N1
    # KP on N2
    # --------------------------------------------------------

    if k_star >= gamma:

        (
            z1,
            k1
        ) = _solve_rkp_with_minimum_items(
            N1,
            c_star,
            gamma,
            gamma
        )

        z2 = _solve_kp_values(
            N2,
            c_star
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
            c_star + 1
        ):

            candidate_c2 = (
                c_star - candidate_c1
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
        # Step 6:
        #
        # Output KP solution for N2.
        # ----------------------------------------------------

        selected_N2, _ = _solve_kp_solution(
            N2,
            c2
        )

        # ----------------------------------------------------
        # Step 7:
        #
        # Obtain k1* for recursive call.
        #
        # The counter is relative to N1's own first half.
        # ----------------------------------------------------

        _, child_first_counts, _ = (
            _solve_rkp_values(
                N1,
                c1,
                gamma
            )
        )

        k1_star = child_first_counts[c1]

        # ----------------------------------------------------
        # Step 8:
        #
        # Recurse on N1.
        # ----------------------------------------------------

        selected_N1, _ = _recursive_reconstruct(
            N1,
            c1,
            gamma
        )

        selected = (
            selected_N1
            + [
                split + index
                for index in selected_N2
            ]
        )

        return selected, z_star

    # --------------------------------------------------------
    # Case 2:
    #
    # k* < Gamma
    #
    # E-kKP on N1
    # RKP on N2 with Gamma-k*
    # --------------------------------------------------------

    remaining_gamma = (
        gamma - k_star
    )

    # --------------------------------------------------------
    # Step 10:
    #
    # E-kKP(N1, k*)
    # --------------------------------------------------------

    z1 = _solve_exact_k_kp_values(
        N1,
        c_star,
        k_star
    )

    # --------------------------------------------------------
    # Step 11:
    #
    # RKP(N2, Gamma-k*)
    # --------------------------------------------------------

    (
        z2,
        k2,
        _
    ) = _solve_rkp_values(
        N2,
        c_star,
        remaining_gamma
    )

    c1 = None
    c2 = None

    # --------------------------------------------------------
    # Find capacity split.
    # --------------------------------------------------------

    for candidate_c1 in range(
        c_star + 1
    ):

        candidate_c2 = (
            c_star - candidate_c1
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
    # Step 13:
    #
    # Output E-kKP solution for N1.
    # --------------------------------------------------------

    selected_N1, _ = (
        _solve_exact_k_kp_solution(
            N1,
            c1,
            k_star
        )
    )

    # --------------------------------------------------------
    # Step 14:
    #
    # Get k2* for N2.
    # --------------------------------------------------------

    (
        _,
        child_first_counts,
        _
    ) = _solve_rkp_values(
        N2,
        c2,
        remaining_gamma
    )

    k2_star = child_first_counts[c2]

    # --------------------------------------------------------
    # Step 15:
    #
    # Recurse on N2.
    # --------------------------------------------------------

    selected_N2, _ = _recursive_reconstruct(
        N2,
        c2,
        remaining_gamma
    )

    selected = (
        selected_N1
        + [
            split + index
            for index in selected_N2
        ]
    )

    return selected, z_star


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

    Parameters:

        cargo_list:
            List of Cargo objects.

        capacity:
            Maximum robust capacity.

        gamma:
            Maximum number of selected items that may
            deviate to their upper weights.

    Returns:

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
    # Invalid capacity.
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
    # This is required by Lemma 1 of the paper.
    # --------------------------------------------------------

    items = sorted(
        cargo_list,
        key=lambda cargo: cargo.uncertainty,
        reverse=True
    )

    # --------------------------------------------------------
    # Recursive reconstruction.
    # --------------------------------------------------------

    selected_indices, best_profit = (
        _recursive_reconstruct(
            items,
            capacity,
            gamma
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
    # Final result.
    # --------------------------------------------------------

    return {
        "selected_items": selected_items,
        "total_profit": best_profit,
        "nominal_weight": nominal_weight,
        "robust_weight": robust_weight,
    }