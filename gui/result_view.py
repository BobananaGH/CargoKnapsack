# gui/result_view.py

from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QListWidget,
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

        self.algorithm_label = QLabel(
            "Algorithm: -"
        )

        self.selected_title = QLabel(
            "Selected Cargo:"
        )

        self.selected_list = QListWidget()
        self.selected_list.setMinimumHeight(120)
        self.selected_list.setMaximumHeight(180)

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

        self.epsilon_label = QLabel(
            "Epsilon: -"
        )

        self.runtime_label = QLabel(
            "Runtime: -"
        )

        # Object names for QSS

        self.algorithm_label.setObjectName(
            "algorithmLabel"
        )

        self.selected_title.setObjectName(
            "selectedTitle"
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

        self.epsilon_label.setObjectName(
            "resultLabel"
        )

        self.runtime_label.setObjectName(
            "resultLabel"
        )

        # Add widgets

        result_layout.addWidget(
            self.algorithm_label
        )

        result_layout.addWidget(
            self.selected_title
        )

        result_layout.addWidget(
            self.selected_list
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

        result_layout.addWidget(
            self.epsilon_label
        )

        result_layout.addWidget(
            self.runtime_label
        )

        result_box.setLayout(
            result_layout
        )

        layout.addWidget(
            result_box
        )

    def show_result(
        self,
        result,
        capacity,
        gamma,
        algorithm,
        epsilon
    ):
        selected_items = result[
            "selected_items"
        ]

        # Clear previous cargo
        self.selected_list.clear()

        # Add selected cargo to scrollable list
        if selected_items:
            for cargo in selected_items:
                self.selected_list.addItem(
                    cargo.name
                )
        else:
            self.selected_list.addItem(
                "None"
            )

        self.algorithm_label.setText(
            f"Algorithm: {algorithm}"
        )

        self.profit_label.setText(
            f"Total Profit: "
            f"{result['total_profit']}"
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

        if algorithm == "FPTAS":
            self.epsilon_label.setText(
                f"Epsilon: {epsilon}"
            )
        else:
            self.epsilon_label.setText(
                "Epsilon: N/A"
            )

        self.runtime_label.setText(
            f"Runtime: "
            f"{result['runtime']:.6f} seconds"
        )