# gui/main_window.py

import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from gui.cargo_view import CargoView
from gui.result_view import ResultView
from models.cargo import Cargo
from services.optimizer import optimize_cargo


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "CargoKnapsack - Robust Cargo Optimization"
        )

        self.setMinimumWidth(1000)
        self.resize(1000, 700)

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        layout = QVBoxLayout()

        layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        layout.setSpacing(15)

        central_widget.setLayout(
            layout
        )

        # ---------------------------------------------
        # Views
        # ---------------------------------------------

        self.cargo_view = CargoView()
        self.result_view = ResultView()

        layout.addWidget(
            self.cargo_view
        )

        layout.addWidget(
            self.result_view
        )

        # ---------------------------------------------
        # Optimize button
        # ---------------------------------------------

        self.cargo_view.optimize_button.clicked.connect(
            self.optimize
        )

    def optimize(self):

        try:
            # -----------------------------------------
            # Common parameters
            # -----------------------------------------

            capacity = (
                self.cargo_view.capacity_input.value()
            )

            algorithm = (
                self.cargo_view.algorithm_input.currentText()
            )

            epsilon = (
                self.cargo_view.epsilon_input.value()
            )

            # -----------------------------------------
            # Read normal cargo dataset
            # -----------------------------------------

            cargo_list = []

            table = (
                self.cargo_view.cargo_table
            )

            for row in range(
                table.rowCount()
            ):

                name_item = table.item(
                    row,
                    0
                )

                weight_item = table.item(
                    row,
                    1
                )

                max_weight_item = table.item(
                    row,
                    2
                )

                profit_item = table.item(
                    row,
                    3
                )

                if (
                    name_item is None
                    or weight_item is None
                    or max_weight_item is None
                    or profit_item is None
                ):
                    continue

                name = (
                    name_item.text().strip()
                )

                if not name:
                    raise ValueError(
                        f"Cargo row {row + 1} "
                        "has no name."
                    )

                try:
                    weight = int(
                        weight_item.text()
                    )

                    max_weight = int(
                        max_weight_item.text()
                    )

                    profit = int(
                        profit_item.text()
                    )

                except ValueError:

                    raise ValueError(
                        f"Invalid numeric value "
                        f"at cargo row {row + 1}."
                    )

                if weight < 0:

                    raise ValueError(
                        f"Weight cannot be negative "
                        f"at row {row + 1}."
                    )

                if max_weight < weight:

                    raise ValueError(
                        f"Max Weight cannot be smaller "
                        f"than Weight at row {row + 1}."
                    )

                if profit < 0:

                    raise ValueError(
                        f"Profit cannot be negative "
                        f"at row {row + 1}."
                    )

                cargo = Cargo(
                    name=name,
                    weight=weight,
                    max_weight=max_weight,
                    profit=profit
                )

                cargo_list.append(
                    cargo
                )

            if not cargo_list:

                raise ValueError(
                    "Please add at least one cargo."
                )

            # -----------------------------------------
            # Gamma
            # -----------------------------------------
            #
            # The 2013 algorithms use the robust
            # uncertainty budget.
            #
            # The 2026 dominance-list DP is being
            # compared on the ordinary 0/1 knapsack
            # problem, so gamma is fixed to zero.
            # -----------------------------------------

            if algorithm == "Dominance-List DP 2026":

                gamma = 0

            else:

                gamma = (
                    self.cargo_view.gamma_input.value()
                )

            # -----------------------------------------
            # Run optimization algorithm
            # -----------------------------------------

            result = optimize_cargo(
                cargo_list,
                capacity,
                gamma,
                algorithm,
                epsilon
            )

            # -----------------------------------------
            # Show result
            # -----------------------------------------

            self.result_view.show_result(
                result,
                capacity,
                gamma,
                algorithm,
                epsilon
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Invalid Input",
                str(error)
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Optimization Error",
                str(error)
            )

    def load_stylesheet(self):

        from pathlib import Path

        stylesheet_path = (
            Path(__file__).parent
            / "styles.qss"
        )

        with open(
            stylesheet_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.setStyleSheet(
                file.read()
            )


def main():

    app = QApplication(sys.argv)

    window = MainWindow()

    window.load_stylesheet()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()