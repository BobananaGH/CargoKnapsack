# gui/result_view.py

from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class ResultView(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        result_box = QGroupBox(
            "Optimization Result"
        )

        result_layout = QVBoxLayout()

        self.selected_label = QLabel(
            "Selected Cargo: -"
        )

        self.profit_label = QLabel(
            "Total Profit: -"
        )

        self.nominal_label = QLabel(
            "Nominal Weight: -"
        )

        self.robust_label = QLabel(
            "Robust Weight: -"
        )

        self.capacity_label = QLabel(
            "Capacity: -"
        )

        self.gamma_label = QLabel(
            "Gamma: -"
        )

        # Object names for QSS

        self.selected_label.setObjectName(
            "resultLabel"
        )

        self.profit_label.setObjectName(
            "profitLabel"
        )

        self.nominal_label.setObjectName(
            "resultLabel"
        )

        self.robust_label.setObjectName(
            "resultLabel"
        )

        self.capacity_label.setObjectName(
            "resultLabel"
        )

        self.gamma_label.setObjectName(
            "resultLabel"
        )

        result_layout.addWidget(
            self.selected_label
        )

        result_layout.addWidget(
            self.profit_label
        )

        result_layout.addWidget(
            self.nominal_label
        )

        result_layout.addWidget(
            self.robust_label
        )

        result_layout.addWidget(
            self.capacity_label
        )

        result_layout.addWidget(
            self.gamma_label
        )

        result_box.setLayout(result_layout)

        layout.addWidget(result_box)

    def show_result(
        self,
        result,
        capacity,
        gamma
    ):

        selected_items = result[
            "selected_items"
        ]

        if selected_items:

            names = ", ".join(
                cargo.name
                for cargo in selected_items
            )

        else:

            names = "None"

        self.selected_label.setText(
            f"Selected Cargo: {names}"
        )

        self.profit_label.setText(
            f"Total Profit: {result['total_profit']}"
        )

        self.nominal_label.setText(
            f"Nominal Weight: "
            f"{result['nominal_weight']}"
        )

        self.robust_label.setText(
            f"Robust Weight: "
            f"{result['robust_weight']}"
        )

        self.capacity_label.setText(
            f"Capacity: {capacity}"
        )

        self.gamma_label.setText(
            f"Gamma: {gamma}"
        )