# gui/cargo_view.py

import json

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class CargoView(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        self.setLayout(main_layout)

        # ---------------------------------------------
        # Parameters
        # ---------------------------------------------
        parameter_box = QGroupBox(
            "Optimization Parameters"
        )

        parameter_layout = QHBoxLayout()

        # Dataset
        dataset_label = QLabel("Dataset:")

        self.dataset_input = QComboBox()
        self.dataset_input.addItems([
            "Sample",
            "Small Benchmark",
            "Medium Benchmark",
            "Large Benchmark",
        ])

        self.dataset_input.currentTextChanged.connect(
            self.load_selected_dataset
        )

        # Capacity
        capacity_label = QLabel("Capacity:")

        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(1, 100000)

        # Gamma
        gamma_label = QLabel("Gamma:")

        self.gamma_input = QSpinBox()
        self.gamma_input.setRange(0, 100)

        # Algorithm
        algorithm_label = QLabel("Algorithm:")

        self.algorithm_input = QComboBox()
        self.algorithm_input.addItems([
            "Robust DP",
            "Recursive Partitioning",
            "BSMILP",
            "LLPP",
            "Branch-and-Cut",
            "FPTAS",
        ])

        # Epsilon
        epsilon_label = QLabel("Epsilon:")

        self.epsilon_input = QDoubleSpinBox()
        self.epsilon_input.setRange(0.01, 1.0)
        self.epsilon_input.setSingleStep(0.05)
        self.epsilon_input.setValue(0.2)
        self.epsilon_input.setDecimals(2)

        # Add widgets
        parameter_layout.addWidget(dataset_label)
        parameter_layout.addWidget(self.dataset_input)

        parameter_layout.addSpacing(10)

        parameter_layout.addWidget(capacity_label)
        parameter_layout.addWidget(self.capacity_input)

        parameter_layout.addSpacing(10)

        parameter_layout.addWidget(gamma_label)
        parameter_layout.addWidget(self.gamma_input)

        parameter_layout.addSpacing(10)

        parameter_layout.addWidget(algorithm_label)
        parameter_layout.addWidget(self.algorithm_input)

        parameter_layout.addSpacing(10)

        parameter_layout.addWidget(epsilon_label)
        parameter_layout.addWidget(self.epsilon_input)

        parameter_layout.addStretch()

        parameter_box.setLayout(parameter_layout)
        main_layout.addWidget(parameter_box)

        # ---------------------------------------------
        # Cargo table
        # ---------------------------------------------
        cargo_label = QLabel("Cargo List")

        self.cargo_table = QTableWidget()
        self.cargo_table.setColumnCount(4)

        self.cargo_table.setHorizontalHeaderLabels([
            "Name",
            "Weight",
            "Max Weight",
            "Profit",
        ])

        self.cargo_table.horizontalHeader().setStretchLastSection(
            True
        )

        self.cargo_table.setAlternatingRowColors(True)

        main_layout.addWidget(cargo_label)
        main_layout.addWidget(self.cargo_table)

        # ---------------------------------------------
        # Buttons
        # ---------------------------------------------
        button_layout = QHBoxLayout()

        add_button = QPushButton("Add Cargo")
        remove_button = QPushButton("Remove Selected")

        self.optimize_button = QPushButton("Optimize")
        self.optimize_button.setObjectName(
            "optimizeButton"
        )

        add_button.clicked.connect(
            self.add_cargo
        )

        remove_button.clicked.connect(
            self.remove_cargo
        )

        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)

        button_layout.addStretch()

        button_layout.addWidget(
            self.optimize_button
        )

        main_layout.addLayout(button_layout)

        # ---------------------------------------------
        # Load default dataset
        # ---------------------------------------------
        self.load_selected_dataset("Sample")

    # ---------------------------------------------
    # Dataset handling
    # ---------------------------------------------

    def get_dataset_path(self, dataset_name):
        data_directory = (
            Path(__file__).parent.parent
            / "data"
        )

        dataset_files = {
            "Sample": "sample_data.json",
            "Small Benchmark": "benchmark_small.json",
            "Medium Benchmark": "benchmark_medium.json",
            "Large Benchmark": "benchmark_large.json",
        }

        if dataset_name not in dataset_files:
            raise ValueError(
                f"Unknown dataset: {dataset_name}"
            )

        return (
            data_directory
            / dataset_files[dataset_name]
        )

    def load_selected_dataset(self, dataset_name):
        data_path = self.get_dataset_path(
            dataset_name
        )

        with open(
            data_path,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        # -----------------------------------------
        # Load parameters
        # -----------------------------------------
        self.capacity_input.setValue(
            data["capacity"]
        )

        self.gamma_input.setValue(
            data["gamma"]
        )

        # -----------------------------------------
        # Clear existing cargo
        # -----------------------------------------
        self.cargo_table.setRowCount(0)

        # -----------------------------------------
        # Load cargo
        # -----------------------------------------
        for cargo in data["cargo"]:
            self.add_cargo(
                cargo["name"],
                cargo["weight"],
                cargo["max_weight"],
                cargo["profit"]
            )

    # ---------------------------------------------
    # Cargo operations
    # ---------------------------------------------

    def add_cargo(
        self,
        name="",
        weight=0,
        max_weight=0,
        profit=0,
    ):
        row = self.cargo_table.rowCount()

        self.cargo_table.insertRow(row)

        self.cargo_table.setItem(
            row,
            0,
            QTableWidgetItem(str(name))
        )

        self.cargo_table.setItem(
            row,
            1,
            QTableWidgetItem(str(weight))
        )

        self.cargo_table.setItem(
            row,
            2,
            QTableWidgetItem(str(max_weight))
        )

        self.cargo_table.setItem(
            row,
            3,
            QTableWidgetItem(str(profit))
        )

    def remove_cargo(self):
        selected_rows = set()

        for item in self.cargo_table.selectedItems():
            selected_rows.add(item.row())

        for row in sorted(
            selected_rows,
            reverse=True
        ):
            self.cargo_table.removeRow(row)