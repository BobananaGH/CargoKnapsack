import heapq
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linprog


EPSILON = 1e-9


def _calculate_robust_weight(cargo_list, selected_indices, gamma):
    """
    Calculate the worst-case weight of a selected solution.

    Robust weight =
        nominal total weight
        + the Gamma largest uncertainties among selected items.
    """

    nominal_weight = sum(
        cargo_list[i].weight
        for i in selected_indices
    )

    uncertainties = sorted(
        (
            cargo_list[i].max_weight - cargo_list[i].weight
            for i in selected_indices
        ),
        reverse=True
    )

    robust_weight = (
        nominal_weight
        + sum(uncertainties[:gamma])
    )

    return robust_weight


def _build_result(cargo_list, selected_indices, gamma):
    """
    Build the result using the project's standard result format.
    """

    selected_items = [
        cargo_list[i]
        for i in selected_indices
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
        cargo_list,
        selected_indices,
        gamma
    )

    return {
        "selected_items": selected_items,
        "total_profit": total_profit,
        "nominal_weight": nominal_weight,
        "robust_weight": robust_weight,
    }


def _solve_lp(
    cargo_list,
    capacity,
    gamma,
    fixed_one,
    fixed_zero,
    cuts
):
    """
    Solve the LP relaxation at one Branch-and-Cut node.

    Variables:
        0 <= x_j <= 1

    Base constraint:
        sum(w_j x_j) <= capacity

    Robustness cuts:
        sum(w_j x_j)
        + sum(delta_j x_j for j in S)
        <= capacity

    where |S| <= Gamma.

    Returns:
        {
            "status": "optimal" / "infeasible",
            "objective": ...,
            "x": [...]
        }
    """

    n = len(cargo_list)

    if n == 0:
        return {
            "status": "optimal",
            "objective": 0.0,
            "x": []
        }

    profits = np.array(
        [cargo.profit for cargo in cargo_list],
        dtype=float
    )

    weights = np.array(
        [cargo.weight for cargo in cargo_list],
        dtype=float
    )

    uncertainties = np.array(
        [
            cargo.max_weight - cargo.weight
            for cargo in cargo_list
        ],
        dtype=float
    )

    # linprog minimizes the objective,
    # therefore maximize profit by minimizing -profit.
    objective = -profits

    # Basic nominal knapsack constraint.
    A_ub = [
        weights
    ]

    b_ub = [
        float(capacity)
    ]

    # Add all robustness cuts accumulated at this node.
    for cut_indices in cuts:

        coefficients = weights.copy()

        for index in cut_indices:
            coefficients[index] += uncertainties[index]

        A_ub.append(coefficients)
        b_ub.append(float(capacity))

    # Variable bounds.
    bounds = []

    for i in range(n):

        if i in fixed_one:
            bounds.append((1.0, 1.0))

        elif i in fixed_zero:
            bounds.append((0.0, 0.0))

        else:
            bounds.append((0.0, 1.0))

    result = linprog(
        c=objective,
        A_ub=np.array(A_ub),
        b_ub=np.array(b_ub),
        bounds=bounds,
        method="highs"
    )

    if not result.success:
        return {
            "status": "infeasible",
            "objective": None,
            "x": None
        }

    # linprog minimizes -profit.
    maximum_profit = -result.fun

    return {
        "status": "optimal",
        "objective": maximum_profit,
        "x": result.x
    }


def _separate_robustness_cut(
    cargo_list,
    x,
    capacity,
    gamma
):
    """
    Separate a violated robustness cut.

    The robust cut has the form:

        sum(w_j x_j)
        + sum(delta_j x_j for j in S)
        <= capacity

    for every S with |S| <= Gamma.

    For a fractional solution x, the most violated cut is obtained
    by selecting up to Gamma items with the largest:

        delta_j * x_j

    contributions.

    Returns:
        list of item indices for a violated cut,
        or None if no violated cut exists.
    """

    if gamma <= 0:
        return None

    nominal_weight = 0.0

    contributions = []

    for i, cargo in enumerate(cargo_list):

        value = float(x[i])

        nominal_weight += (
            cargo.weight * value
        )

        uncertainty = (
            cargo.max_weight
            - cargo.weight
        )

        contribution = uncertainty * value

        if contribution > EPSILON:
            contributions.append(
                (contribution, i)
            )

    if not contributions:
        return None

    # Largest Gamma delta_j * x_j values.
    contributions.sort(
        key=lambda item: item[0],
        reverse=True
    )

    selected = contributions[:gamma]

    additional_weight = sum(
        contribution
        for contribution, _ in selected
    )

    lhs = (
        nominal_weight
        + additional_weight
    )

    if lhs <= capacity + EPSILON:
        return None

    cut_indices = [
        index
        for _, index in selected
    ]

    return cut_indices


def _is_integral(x):
    """
    Check whether the LP solution is integral.
    """

    for value in x:

        if abs(value - round(value)) > EPSILON:
            return False

    return True


def _get_integral_indices(x):
    """
    Convert an integral LP solution into selected item indices.
    """

    return [
        i
        for i, value in enumerate(x)
        if value >= 0.5
    ]


def _choose_branch_variable(x):
    """
    Choose a fractional variable for branching.

    We choose the variable closest to 0.5.
    """

    fractional = []

    for i, value in enumerate(x):

        if (
            value > EPSILON
            and value < 1.0 - EPSILON
        ):
            distance = abs(value - 0.5)

            fractional.append(
                (distance, i)
            )

    if not fractional:
        return None

    fractional.sort(
        key=lambda item: item[0]
    )

    return fractional[0][1]


@dataclass(order=True)
class _Node:
    """
    Branch-and-Cut tree node.

    Python's heap uses the first field for priority.
    We use negative upper bound so that the node with the
    largest LP bound is processed first.
    """

    priority: float

    node_id: int = field(compare=False)

    fixed_one: frozenset = field(compare=False)

    fixed_zero: frozenset = field(compare=False)

    cuts: tuple = field(compare=False)

    upper_bound: float = field(compare=False)


def branch_and_cut(
    cargo_list,
    capacity,
    gamma
):
    """
    Exact Branch-and-Cut algorithm for the Robust Knapsack Problem.

    Based on Section 4.3 of:

        Monaci, Pferschy, Serafini
        "Exact solution of the robust knapsack problem"

    The algorithm:

        1. Solve the LP relaxation.
        2. Separate violated robustness cuts.
        3. Add cuts until the LP solution satisfies all
           separated robustness constraints.
        4. If the solution is integral, update the incumbent.
        5. Otherwise branch on a fractional x_j.
        6. Continue the enumerative tree using LP bounds.

    Gamma = 0 naturally reduces to the ordinary 0/1 Knapsack
    branch-and-bound problem.
    """

    # ---------------------------------------------------------
    # Basic input handling
    # ---------------------------------------------------------

    if not cargo_list:
        return _build_result(
            cargo_list,
            [],
            0
        )

    if capacity <= 0:
        return _build_result(
            cargo_list,
            [],
            gamma
        )

    n = len(cargo_list)

    gamma = max(
        0,
        min(gamma, n)
    )

    # ---------------------------------------------------------
    # Incumbent
    # ---------------------------------------------------------

    best_profit = 0.0
    best_indices = []

    # ---------------------------------------------------------
    # Initial LP relaxation
    # ---------------------------------------------------------

    root_lp = _solve_lp(
        cargo_list=cargo_list,
        capacity=capacity,
        gamma=gamma,
        fixed_one=frozenset(),
        fixed_zero=frozenset(),
        cuts=tuple()
    )

    if root_lp["status"] != "optimal":
        return _build_result(
            cargo_list,
            [],
            gamma
        )

    # ---------------------------------------------------------
    # Branch-and-Cut priority queue
    # ---------------------------------------------------------

    node_counter = 0

    root = _Node(
        priority=-root_lp["objective"],
        node_id=node_counter,
        fixed_one=frozenset(),
        fixed_zero=frozenset(),
        cuts=tuple(),
        upper_bound=root_lp["objective"]
    )

    heap = [root]

    # ---------------------------------------------------------
    # Main enumerative tree
    # ---------------------------------------------------------

    while heap:

        node = heapq.heappop(heap)

        # -----------------------------------------------------
        # Bound pruning
        # -----------------------------------------------------

        if node.upper_bound <= best_profit + EPSILON:
            continue

        # -----------------------------------------------------
        # Solve LP at this node
        # -----------------------------------------------------

        lp_result = _solve_lp(
            cargo_list=cargo_list,
            capacity=capacity,
            gamma=gamma,
            fixed_one=node.fixed_one,
            fixed_zero=node.fixed_zero,
            cuts=node.cuts
        )

        if lp_result["status"] != "optimal":
            continue

        x = lp_result["x"]

        upper_bound = lp_result["objective"]

        # -----------------------------------------------------
        # Bound pruning after solving
        # -----------------------------------------------------

        if upper_bound <= best_profit + EPSILON:
            continue

        # -----------------------------------------------------
        # Robustness cut separation
        # -----------------------------------------------------

        cut = _separate_robustness_cut(
            cargo_list=cargo_list,
            x=x,
            capacity=capacity,
            gamma=gamma
        )

        if cut is not None:

            # Add the violated robustness cut to this node.

            new_cuts = list(node.cuts)

            new_cuts.append(
                tuple(cut)
            )

            new_cuts = tuple(new_cuts)

            # Reinsert the same node with the new cut.
            node_counter += 1

            cut_node = _Node(
                priority=-upper_bound,
                node_id=node_counter,
                fixed_one=node.fixed_one,
                fixed_zero=node.fixed_zero,
                cuts=new_cuts,
                upper_bound=upper_bound
            )

            heapq.heappush(
                heap,
                cut_node
            )

            continue

        # -----------------------------------------------------
        # At this point the LP solution satisfies all currently
        # separated robustness cuts.
        # -----------------------------------------------------

        # -----------------------------------------------------
        # Integral solution
        # -----------------------------------------------------

        if _is_integral(x):

            selected_indices = _get_integral_indices(x)

            robust_weight = _calculate_robust_weight(
                cargo_list,
                selected_indices,
                gamma
            )

            # Final exact feasibility check.
            if robust_weight <= capacity + EPSILON:

                profit = sum(
                    cargo_list[i].profit
                    for i in selected_indices
                )

                if profit > best_profit + EPSILON:

                    best_profit = float(profit)

                    best_indices = list(
                        selected_indices
                    )

            continue

        # -----------------------------------------------------
        # Fractional solution -> branch
        # -----------------------------------------------------

        branch_index = _choose_branch_variable(x)

        if branch_index is None:
            continue

        # -----------------------------------------------------
        # Branch 1:
        # x_j = 1
        # -----------------------------------------------------

        if branch_index not in node.fixed_zero:

            child_fixed_one = set(
                node.fixed_one
            )

            child_fixed_one.add(
                branch_index
            )

            child_fixed_one = frozenset(
                child_fixed_one
            )

            # Check that we are not contradicting x_j = 0.
            if (
                branch_index
                not in node.fixed_zero
            ):

                child_lp = _solve_lp(
                    cargo_list=cargo_list,
                    capacity=capacity,
                    gamma=gamma,
                    fixed_one=child_fixed_one,
                    fixed_zero=node.fixed_zero,
                    cuts=node.cuts
                )

                if child_lp["status"] == "optimal":

                    child_bound = child_lp[
                        "objective"
                    ]

                    if (
                        child_bound
                        > best_profit + EPSILON
                    ):

                        node_counter += 1

                        child = _Node(
                            priority=-child_bound,
                            node_id=node_counter,
                            fixed_one=child_fixed_one,
                            fixed_zero=node.fixed_zero,
                            cuts=node.cuts,
                            upper_bound=child_bound
                        )

                        heapq.heappush(
                            heap,
                            child
                        )

        # -----------------------------------------------------
        # Branch 2:
        # x_j = 0
        # -----------------------------------------------------

        if branch_index not in node.fixed_one:

            child_fixed_zero = set(
                node.fixed_zero
            )

            child_fixed_zero.add(
                branch_index
            )

            child_fixed_zero = frozenset(
                child_fixed_zero
            )

            # Check that we are not contradicting x_j = 1.
            if (
                branch_index
                not in node.fixed_one
            ):

                child_lp = _solve_lp(
                    cargo_list=cargo_list,
                    capacity=capacity,
                    gamma=gamma,
                    fixed_one=node.fixed_one,
                    fixed_zero=child_fixed_zero,
                    cuts=node.cuts
                )

                if child_lp["status"] == "optimal":

                    child_bound = child_lp[
                        "objective"
                    ]

                    if (
                        child_bound
                        > best_profit + EPSILON
                    ):

                        node_counter += 1

                        child = _Node(
                            priority=-child_bound,
                            node_id=node_counter,
                            fixed_one=node.fixed_one,
                            fixed_zero=child_fixed_zero,
                            cuts=node.cuts,
                            upper_bound=child_bound
                        )

                        heapq.heappush(
                            heap,
                            child
                        )

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return _build_result(
        cargo_list,
        best_indices,
        gamma
    )