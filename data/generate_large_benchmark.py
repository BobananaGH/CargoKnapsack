import json
import random
from pathlib import Path


random.seed(42)

cargo = []

for i in range(1, 151):
    weight = random.randint(10, 50)
    uncertainty = random.randint(2, 12)
    max_weight = weight + uncertainty
    profit = random.randint(30, 200)

    cargo.append({
        "name": f"Cargo {i}",
        "weight": weight,
        "max_weight": max_weight,
        "profit": profit
    })


data = {
    "capacity": 1500,
    "gamma": 20,
    "cargo": cargo
}


output_path = Path(__file__).parent / "benchmark_large.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)

print(f"Created: {output_path}")
print(f"Cargo items: {len(cargo)}")
print(f"Capacity: {data['capacity']}")
print(f"Gamma: {data['gamma']}")