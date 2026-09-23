# gui/result_view.py

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

        self.setMaximumHeight(320)

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

        result_layout.setSpacing(
            20
        )

        # ---------------------------------------------
        # Left column
        # ---------------------------------------------

        left_column = QVBoxLayout()

        left_column.setSpacing(
            3
        )

        self.algorithm_label = QLabel(
            "Algorithm: -"
        )

        self.nominal_label = QLabel(
            "Nominal Weight: -"
        )

        self.robust_label = QLabel(
            "Robust Weight: -"
        )

        self.optimal_weight_label = QLabel(
            "Optimal Weight: -"
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

        self.objective_label = QLabel(
            "Objective Value: -"
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

        self.optimal_weight_label.setObjectName(
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

        self.objective_label.setObjectName(
            "profitLabel"
        )

        # ---------------------------------------------
        # Add result information
        # ---------------------------------------------

        left_column.addWidget(
            self.algorithm_label
        )

        left_column.addWidget(
            self.objective_label
        )

        left_column.addWidget(
            self.nominal_label
        )

        left_column.addWidget(
            self.robust_label
        )

        left_column.addWidget(
            self.optimal_weight_label
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

        right_column.setSpacing(
            4
        )

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

        right_column.addWidget(
            self.selected_list,
            1
        )

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
        # Initial visibility
        # ---------------------------------------------

        self.set_robust_result_visible(
            True
        )

    # ---------------------------------------------
    # Visibility helpers
    # ---------------------------------------------

    def set_robust_result_visible(
        self,
        visible
    ):
        """
        Configure the result panel for the
        2013 Robust Knapsack algorithms.
        """

        self.nominal_label.setVisible(
            visible
        )

        self.robust_label.setVisible(
            visible
        )

        self.optimal_weight_label.setVisible(
            not visible
        )

        self.gamma_label.setVisible(
            visible
        )

        self.selected_title.setVisible(
            visible
        )

        self.selected_list.setVisible(
            visible
        )

        self.profit_label.setVisible(
            visible
        )

        self.objective_label.setVisible(
            not visible
        )

    # ---------------------------------------------
    # Show 2026 Dominance-List DP result
    # ---------------------------------------------

    def show_dominance_dp_result(
        self,
        result,
        capacity,
        algorithm
    ):
        """
        Display the result of the 2026
        dominance-list dynamic programming algorithm.
        """

        # -----------------------------------------
        # Hide Robust Knapsack-specific fields
        # -----------------------------------------

        self.nominal_label.setVisible(
            False
        )

        self.robust_label.setVisible(
            False
        )

        self.gamma_label.setVisible(
            False
        )

        self.epsilon_label.setVisible(
            False
        )

        self.profit_label.setVisible(
            False
        )

        # -----------------------------------------
        # General information
        # -----------------------------------------

        self.algorithm_label.setText(
            f"Algorithm: {algorithm}"
        )

        self.algorithm_label.setVisible(
            True
        )

        self.capacity_label.setText(
            f"Capacity: {capacity}"
        )

        self.capacity_label.setVisible(
            True
        )

        self.runtime_label.setText(
            "Runtime: "
            f"{result['runtime']:.6f} seconds"
        )

        self.runtime_label.setVisible(
            True
        )

        # -----------------------------------------
        # Optimal weight
        # -----------------------------------------

        total_weight = result[
            "total_weight"
        ]

        self.optimal_weight_label.setText(
            "Optimal Weight: "
            f"{total_weight}"
        )

        self.optimal_weight_label.setVisible(
            True
        )

        # -----------------------------------------
        # Optimal profit
        # -----------------------------------------

        total_profit = result[
            "total_profit"
        ]

        self.objective_label.setText(
            "Optimal Profit: "
            f"{total_profit}"
        )

        self.objective_label.setVisible(
            True
        )

        # -----------------------------------------
        # Clear previous selected cargo
        # -----------------------------------------

        self.selected_list.clear()

        # -----------------------------------------
        # Selected cargo
        # -----------------------------------------

        self.selected_title.setText(
            "Selected Cargo:"
        )

        self.selected_title.setVisible(
            True
        )

        self.selected_list.setVisible(
            True
        )

        selected_items = result.get(
            "selected_items",
            []
        )

        if selected_items:

            for cargo in selected_items:

                self.selected_list.addItem(
                    cargo.name
                )

        else:

            self.selected_list.addItem(
                "None"
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

        # -----------------------------------------
        # 2026 Dominance-List DP
        # -----------------------------------------

        if algorithm == "Dominance-List DP 2026":

            self.show_dominance_dp_result(
                result,
                capacity,
                algorithm
            )

            return

        # -----------------------------------------
        # 2013 Robust Knapsack
        # -----------------------------------------

        self.set_robust_result_visible(
            True
        )

        selected_items = result[
            "selected_items"
        ]

        # -----------------------------------------
        # Clear previous solution
        # -----------------------------------------

        self.selected_list.clear()

        self.selected_title.setText(
            "Selected Cargo:"
        )

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
            "Nominal Weight: "
            f"{result['nominal_weight']}"
        )

        self.robust_label.setText(
            "Robust Weight: "
            f"{result['robust_weight']}"
        )

        self.capacity_label.setText(
            f"Capacity: {capacity}"
        )

        self.gamma_label.setText(
            f"Gamma: {gamma}"
        )

        if algorithm == "FPTAS 2013":

            self.epsilon_label.setText(
                f"Epsilon: {epsilon}"
            )

        else:

            self.epsilon_label.setText(
                "Epsilon: N/A"
            )

        self.runtime_label.setText(
            "Runtime: "
            f"{result['runtime']:.6f} seconds"
        )

        self.profit_label.setText(
            "Total Profit: "
            f"{result['total_profit']}"
        )