from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout,
    QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
import os

# Adjust the path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import from users_orders_manager
from users_orders_manager.interface import *


class OrdersManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.order_table = QTableWidget()
        self.setLayout(self.create_layout())
        self.populate_order_table()  # Populate table on initialization

    def create_layout(self):
        """Create the layout for the Orders Management page."""
        layout = QVBoxLayout()

        # Title Label
        label = QLabel("Orders Management")
        label.setFont(QFont("Arial", 18, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: black;")
        layout.addWidget(label)

        # Set up the order table
        self.order_table.setColumnCount(7)
        self.order_table.setHorizontalHeaderLabels(
            ["Order ID", "User ID", "User Name", "User Email", "Order Date", "Status", "Remaining Posts"]
        )
        layout.addWidget(self.order_table)

        # Populate the table with data
        self.populate_order_table()

        # Buttons for Request and Delete Order
        button_layout = QHBoxLayout()

        self.request_order_button = QPushButton("Request Order")
        self.delete_order_button = QPushButton("Delete Order")

        self.request_order_button.clicked.connect(self.request_order)
        self.delete_order_button.clicked.connect(self.delete_order)

        button_layout.addWidget(self.request_order_button)
        button_layout.addWidget(self.delete_order_button)

        layout.addLayout(button_layout)
        return layout

    def populate_order_table(self):
        """Populate the orders table with data from the database."""
        try:
            orders = get_all_orders()  # Fetch the orders
            self.order_table.setRowCount(len(orders))

            for row, order in enumerate(orders):
                self.order_table.setItem(row, 0, QTableWidgetItem(str(order.order_id)))
                self.order_table.setItem(row, 1, QTableWidgetItem(str(order.user_id)))

                # Retrieve associated user's name and email
                user_name = order.user.name if order.user else "Unknown"
                user_email = order.user.email if order.user else "Unknown"

                self.order_table.setItem(row, 2, QTableWidgetItem(user_name))
                self.order_table.setItem(row, 3, QTableWidgetItem(user_email))
                self.order_table.setItem(row, 4, QTableWidgetItem(order.order_date.strftime("%Y-%m-%d")))
                self.order_table.setItem(row, 5, QTableWidgetItem(order.order_status.value))
                self.order_table.setItem(row, 6, QTableWidgetItem(str(order.remaining_posts)))
            
            self.order_table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load orders: {str(e)}")

    def request_order(self):
        """Handle the 'Request Order' button click."""
        selected_row = self.order_table.currentRow()
        if selected_row >= 0:
            order_id = self.order_table.item(selected_row, 0).text()
            try:
                handle_order(order_id, email_db)  # Assuming handle_order is the correct function
                QMessageBox.information(self, "Success", "Order requested successfully.")
                self.populate_order_table()  # Refresh the table after the request
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to request order: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No order selected. Please select an order.")

    def delete_order(self):
        """Handle the 'Delete Order' button click."""
        selected_row = self.order_table.currentRow()
        if selected_row >= 0:
            order_id = self.order_table.item(selected_row, 0).text()

            confirm = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete order {order_id}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                try:
                    delete_order(order_id)  # Call the delete_order function
                    QMessageBox.information(self, "Success", "Order deleted successfully.")
                    self.populate_order_table()  # Refresh the table after deletion
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete order: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No order selected. Please select an order.")
