# gui/cargo_view.py

import json
from pathlib import Path

from PySide6.QtWidgets import (
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

        capacity_label = QLabel("Capacity:")

        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(1, 100000)

        gamma_label = QLabel("Gamma:")

        self.gamma_input = QSpinBox()
        self.gamma_input.setRange(0, 100)

        parameter_layout.addWidget(
            capacity_label
        )

        parameter_layout.addWidget(
            self.capacity_input
        )

        parameter_layout.addSpacing(20)

        parameter_layout.addWidget(
            gamma_label
        )

        parameter_layout.addWidget(
            self.gamma_input
        )

        parameter_layout.addStretch()

        parameter_box.setLayout(
            parameter_layout
        )

        main_layout.addWidget(
            parameter_box
        )

        # ---------------------------------------------
        # Cargo table
        # ---------------------------------------------

        cargo_label = QLabel("Cargo List")

        self.cargo_table = QTableWidget()

        self.cargo_table.setColumnCount(4)

        self.cargo_table.setHorizontalHeaderLabels(
            [
                "Name",
                "Weight",
                "Max Weight",
                "Profit",
            ]
        )

        self.cargo_table.horizontalHeader().setStretchLastSection(
            True
        )

        self.cargo_table.setAlternatingRowColors(
            True
        )

        main_layout.addWidget(
            cargo_label
        )

        main_layout.addWidget(
            self.cargo_table
        )

        # ---------------------------------------------
        # Buttons
        # ---------------------------------------------

        button_layout = QHBoxLayout()

        add_button = QPushButton(
            "Add Cargo"
        )

        remove_button = QPushButton(
            "Remove Selected"
        )

        self.optimize_button = QPushButton(
            "Optimize"
        )

        self.optimize_button.setObjectName(
            "optimizeButton"
        )

        add_button.clicked.connect(
            self.add_cargo
        )

        remove_button.clicked.connect(
            self.remove_cargo
        )

        button_layout.addWidget(
            add_button
        )

        button_layout.addWidget(
            remove_button
        )

        button_layout.addStretch()

        button_layout.addWidget(
            self.optimize_button
        )

        main_layout.addLayout(
            button_layout
        )

        # ---------------------------------------------
        # Load sample data
        # ---------------------------------------------

        self.load_sample_data()

    def load_sample_data(self):

        data_path = (
            Path(__file__).parent.parent
            / "data"
            / "sample_data.json"
        )

        with open(
            data_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        # Load capacity
        self.capacity_input.setValue(
            data["capacity"]
        )

        # Load Gamma
        self.gamma_input.setValue(
            data["gamma"]
        )

        # Load cargo
        for cargo in data["cargo"]:

            self.add_cargo(
                cargo["name"],
                cargo["weight"],
                cargo["max_weight"],
                cargo["profit"]
            )

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