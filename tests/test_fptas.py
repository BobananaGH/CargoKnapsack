# tests/test_fptas.py

from models.cargo import Cargo
from algorithms.fptas import fptas


def test_normal_case():
    cargo_list = [
        Cargo("Laptop", 10, 12, 100),
        Cargo("Machine", 40, 50, 300),
        Cargo("Food", 20, 25, 150),
        Cargo("Box A", 30, 35, 200),
    ]

    result = fptas(
        cargo_list,
        capacity=100,
        gamma=2,
        epsilon=0.2
    )

    print("\nTest 1 - Normal case")
    print("Selected cargo:", result["selected_items"])
    print("Total profit:", result["total_profit"])
    print("Nominal weight:", result["nominal_weight"])
    print("Robust weight:", result["robust_weight"])
    print("Epsilon:", result["epsilon"])


def test_gamma_zero():
    cargo_list = [
        Cargo("A", 20, 30, 100),
        Cargo("B", 30, 40, 150),
        Cargo("C", 40, 50, 200),
    ]

    result = fptas(
        cargo_list,
        capacity=50,
        gamma=0,
        epsilon=0.2
    )

    print("\nTest 2 - Gamma = 0")
    print("Selected cargo:", result["selected_items"])
    print("Total profit:", result["total_profit"])
    print("Nominal weight:", result["nominal_weight"])
    print("Robust weight:", result["robust_weight"])
    print("Epsilon:", result["epsilon"])


def test_gamma_one():
    cargo_list = [
        Cargo("A", 20, 30, 100),
        Cargo("B", 30, 35, 150),
        Cargo("C", 10, 12, 80),
    ]

    result = fptas(
        cargo_list,
        capacity=50,
        gamma=1,
        epsilon=0.2
    )

    print("\nTest 3 - Gamma = 1")
    print("Selected cargo:", result["selected_items"])
    print("Total profit:", result["total_profit"])
    print("Nominal weight:", result["nominal_weight"])
    print("Robust weight:", result["robust_weight"])
    print("Epsilon:", result["epsilon"])


def test_capacity_too_small():
    cargo_list = [
        Cargo("A", 20, 25, 100),
        Cargo("B", 30, 35, 150),
    ]

    result = fptas(
        cargo_list,
        capacity=10,
        gamma=1,
        epsilon=0.2
    )

    print("\nTest 4 - Capacity too small")
    print("Selected cargo:", result["selected_items"])
    print("Total profit:", result["total_profit"])
    print("Nominal weight:", result["nominal_weight"])
    print("Robust weight:", result["robust_weight"])
    print("Epsilon:", result["epsilon"])


def test_empty_list():
    result = fptas(
        [],
        capacity=100,
        gamma=2,
        epsilon=0.2
    )

    print("\nTest 5 - Empty cargo list")
    print("Selected cargo:", result["selected_items"])
    print("Total profit:", result["total_profit"])
    print("Nominal weight:", result["nominal_weight"])
    print("Robust weight:", result["robust_weight"])
    print("Epsilon:", result["epsilon"])


def test_invalid_epsilon():
    cargo_list = [
        Cargo("A", 20, 25, 100),
    ]

    try:
        fptas(
            cargo_list,
            capacity=50,
            gamma=1,
            epsilon=0
        )
        print("\nTest 6 - Invalid epsilon")
        print("ERROR: Expected ValueError")
    except ValueError as error:
        print("\nTest 6 - Invalid epsilon")
        print("ValueError:", error)


if __name__ == "__main__":
    test_normal_case()
    test_gamma_zero()
    test_gamma_one()
    test_capacity_too_small()
    test_empty_list()
    test_invalid_epsilon()

    print("\nAll tests completed.")