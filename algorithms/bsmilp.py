# algorithms/bsmilp.py

"""
BSMILP algorithm for the Robust Knapsack Problem.

Based on Section 4.1 of:
"Exact solution of the robust knapsack problem"

BSMILP = Budgeted-Set Mixed Integer Linear Programming.

The robust constraint is represented by:

    sum(w_j * x_j) + Gamma * rho + sum(pi_j) <= capacity

with:

    rho + pi_j >= uncertainty_j * x_j
    rho >= 0
    pi_j >= 0
    x_j in {0, 1}

The objective is:

    maximize sum(profit_j * x_j)

The formulation gives an exact solution when the MILP solver
returns an optimal solution.
"""

try:
    import pulp
except ImportError:
    pulp = None


def _calculate_robust_weight(selected_items, gamma):
    """
    Calculate the worst-case robust weight of a selected set.

    Robust weight =
        nominal weight
        + sum of the Gamma largest uncertainties.
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

    robust_weight = (
        nominal_weight
        + sum(uncertainties[:gamma])
    )

    return robust_weight


def bsmilp(cargo_list, capacity, gamma):
    """
    Solve the Robust Knapsack Problem using BSMILP.

    Parameters:
        cargo_list: list of Cargo objects
        capacity: maximum cargo capacity
        gamma: maximum number of items that may
               reach their upper weight

    Returns:
        Dictionary containing:
            selected_items
            total_profit
            nominal_weight
            robust_weight
    """

    if pulp is None:
        raise ImportError(
            "PuLP is not installed. "
            "Install it with: pip install pulp"
        )

    if not cargo_list or capacity <= 0:
        return {
            "selected_items": [],
            "total_profit": 0,
            "nominal_weight": 0,
            "robust_weight": 0,
        }

    gamma = min(
        max(gamma, 0),
        len(cargo_list)
    )

    n = len(cargo_list)

    # ---------------------------------------------------------
    # Create MILP model
    # ---------------------------------------------------------

    model = pulp.LpProblem(
        "Robust_Knapsack_BSMILP",
        pulp.LpMaximize
    )

    # ---------------------------------------------------------
    # Decision variables
    #
    # x[j]    = 1 if cargo j is selected
    # rho     = auxiliary continuous variable
    # pi[j]   = auxiliary continuous variables
    # ---------------------------------------------------------

    x = [
        pulp.LpVariable(
            f"x_{j}",
            cat=pulp.LpBinary
        )
        for j in range(n)
    ]

    rho = pulp.LpVariable(
        "rho",
        lowBound=0,
        cat=pulp.LpContinuous
    )

    pi = [
        pulp.LpVariable(
            f"pi_{j}",
            lowBound=0,
            cat=pulp.LpContinuous
        )
        for j in range(n)
    ]

    # ---------------------------------------------------------
    # Objective:
    #
    # Maximize total profit
    # ---------------------------------------------------------

    model += pulp.lpSum(
        cargo_list[j].profit * x[j]
        for j in range(n)
    )

    # ---------------------------------------------------------
    # Robust capacity constraint:
    #
    # sum(w_j * x_j)
    # + Gamma * rho
    # + sum(pi_j)
    # <= capacity
    # ---------------------------------------------------------

    model += (
        pulp.lpSum(
            cargo_list[j].weight * x[j]
            for j in range(n)
        )
        + gamma * rho
        + pulp.lpSum(pi)
        <= capacity
    )

    # ---------------------------------------------------------
    # Robustness constraints:
    #
    # rho + pi_j >= uncertainty_j * x_j
    #
    # where:
    #
    # uncertainty_j = max_weight_j - weight_j
    # ---------------------------------------------------------

    for j in range(n):

        model += (
            rho + pi[j]
            >= cargo_list[j].uncertainty * x[j]
        )

    # ---------------------------------------------------------
    # Solve the MILP
    #
    # CBC is included with normal PuLP installations.
    # ---------------------------------------------------------

    solver = pulp.PULP_CBC_CMD(
        msg=False
    )

    model.solve(solver)

    # ---------------------------------------------------------
    # Check solver status
    # ---------------------------------------------------------

    status = pulp.LpStatus[
        model.status
    ]

    if status != "Optimal":
        raise RuntimeError(
            f"BSMILP solver did not find an optimal solution. "
            f"Status: {status}"
        )

    # ---------------------------------------------------------
    # Recover selected cargo
    # ---------------------------------------------------------

    selected_items = []

    for j in range(n):

        value = pulp.value(x[j])

        if value is not None and value > 0.5:
            selected_items.append(
                cargo_list[j]
            )

    # ---------------------------------------------------------
    # Calculate final result
    # ---------------------------------------------------------

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
    }