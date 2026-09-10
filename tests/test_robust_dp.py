# tests/test_robust_dp.py

from models.cargo import Cargo
from algorithms.robust_dp import robust_knapsack


def test_normal_case():
    cargo_list = [
        Cargo("Laptop", 10, 12, 100),
        Cargo("Machine", 40, 50, 300),
        Cargo("Food", 20, 25, 150),
        Cargo("Box A", 30, 35, 200),
    ]

    result = robust_knapsack(
        cargo_list,
        capacity=100,
        gamma=2
    )

    print("\nTest 1 - Normal case")
    print("Selected cargo:", result["selected_items"])
    print("Total profit:", result["total_profit"])
    print("Nominal weight:", result["nominal_weight"])
    print("Robust weight:", result["robust_weight"])


def test_gamma_zero():
    cargo_list = [
        Cargo("A", 20, 30, 100),
        Cargo("B", 30, 40, 150),
        Cargo("C", 40, 50, 200),
    ]

    result = robust_knapsack(
        cargo_list,
        capacity=50,
        gamma=0
    )

    print("\nTest 2 - Gamma = 0")
    print("Selected cargo:", result["selected_items"])
    print("Total profit:", result["total_profit"])
    print("Nominal weight:", result["nominal_weight"])
    print("Robust weight:", result["robust_weight"])


def test_gamma_one():
    cargo_list = [
        Cargo("A", 20, 30, 100),
        Cargo("B", 30, 35, 150),
        Cargo("C", 10, 12, 80),
    ]

    result = robust_knapsack(
        cargo_list,
        capacity=50,
        gamma=1
    )

    print("\nTest 3 - Gamma = 1")
    print("Selected cargo:", result["selected_items"])
    print("Total profit:", result["total_profit"])
    print("Nominal weight:", result["nominal_weight"])
    print("Robust weight:", result["robust_weight"])


def test_capacity_too_small():
    cargo_list = [
        Cargo("A", 20, 25, 100),
        Cargo("B", 30, 35, 150),
    ]

    result = robust_knapsack(
        cargo_list,
        capacity=10,
        gamma=1
    )

    print("\nTest 4 - Capacity too small")
    print("Selected cargo:", result["selected_items"])
    print("Total profit:", result["total_profit"])
    print("Nominal weight:", result["nominal_weight"])
    print("Robust weight:", result["robust_weight"])


def test_empty_list():
    result = robust_knapsack(
        [],
        capacity=100,
        gamma=2
    )

    print("\nTest 5 - Empty cargo list")
    print("Selected cargo:", result["selected_items"])
    print("Total profit:", result["total_profit"])
    print("Nominal weight:", result["nominal_weight"])
    print("Robust weight:", result["robust_weight"])


if __name__ == "__main__":
    test_normal_case()
    test_gamma_zero()
    test_gamma_one()
    test_capacity_too_small()
    test_empty_list()

    print("\nAll tests completed.")