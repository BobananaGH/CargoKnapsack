from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QVBoxLayout,
    QWidget,
)


class ResultView(QWidget):

    def __init__(self):

        super().__init__()

        self.setMaximumHeight(260)

        layout = QVBoxLayout()

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.setLayout(layout)

        # ---------------------------------------------
        # Result box
        # ---------------------------------------------

        result_box = QGroupBox(
            "Optimization Result"
        )

        result_layout = QHBoxLayout()

        result_layout.setSpacing(20)

        # ---------------------------------------------
        # Left column
        # ---------------------------------------------

        left_column = QVBoxLayout()

        left_column.setSpacing(3)

        self.algorithm_label = QLabel(
            "Algorithm: -"
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

        # ---------------------------------------------
        # Object names for QSS
        # ---------------------------------------------

        self.algorithm_label.setObjectName(
            "algorithmLabel"
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

        # ---------------------------------------------
        # Add result information
        # ---------------------------------------------

        left_column.addWidget(
            self.algorithm_label
        )

        left_column.addWidget(
            self.nominal_label
        )

        left_column.addWidget(
            self.robust_label
        )

        left_column.addWidget(
            self.capacity_label
        )

        left_column.addWidget(
            self.gamma_label
        )

        left_column.addWidget(
            self.epsilon_label
        )

        left_column.addWidget(
            self.runtime_label
        )

        left_column.addStretch()

        # ---------------------------------------------
        # Right column
        # ---------------------------------------------

        right_column = QVBoxLayout()

        right_column.setSpacing(4)

        self.selected_title = QLabel(
            "Selected Cargo:"
        )

        self.selected_list = QListWidget()

        self.selected_list.setMinimumHeight(
            80
        )

        self.profit_label = QLabel(
            "Total Profit: -"
        )

        self.selected_title.setObjectName(
            "selectedTitle"
        )

        self.profit_label.setObjectName(
            "profitLabel"
        )

        # ---------------------------------------------
        # Add selected cargo
        # ---------------------------------------------

        right_column.addWidget(
            self.selected_title
        )

        # Stretch to fill available space
        right_column.addWidget(
            self.selected_list,
            1
        )

        # ---------------------------------------------
        # Total profit
        # ---------------------------------------------

        right_column.addWidget(
            self.profit_label
        )

        # ---------------------------------------------
        # Combine columns
        # ---------------------------------------------

        result_layout.addLayout(
            left_column,
            2
        )

        result_layout.addLayout(
            right_column,
            1
        )

        result_box.setLayout(
            result_layout
        )

        layout.addWidget(
            result_box
        )

    # ---------------------------------------------
    # Show result
    # ---------------------------------------------

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

        # -----------------------------------------
        # Clear previous cargo
        # -----------------------------------------

        self.selected_list.clear()

        # -----------------------------------------
        # Add selected cargo
        # -----------------------------------------

        if selected_items:

            for cargo in selected_items:

                self.selected_list.addItem(
                    cargo.name
                )

        else:

            self.selected_list.addItem(
                "None"
            )

        # -----------------------------------------
        # Result information
        # -----------------------------------------

        self.algorithm_label.setText(
            f"Algorithm: {algorithm}"
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

        self.profit_label.setText(
            f"Total Profit: "
            f"{result['total_profit']}"
        )