# models/cargo.py

class Cargo:
    def __init__(self, name, weight, max_weight, profit):
        self.name = name
        self.weight = weight
        self.max_weight = max_weight
        self.profit = profit

    @property
    def uncertainty(self):
        return self.max_weight - self.weight

    def __repr__(self):
        return (
            f"Cargo(name='{self.name}', "
            f"weight={self.weight}, "
            f"max_weight={self.max_weight}, "
            f"profit={self.profit})"
        )