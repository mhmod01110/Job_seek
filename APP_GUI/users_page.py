import sys
import os

# Adjust the path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import from users_orders_manager
from users_orders_manager.interface import *
from orders_page import OrdersManagementPage

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QStackedWidget, QLabel, QPushButton, QFormLayout, QTableWidget, QTableWidgetItem,
    QDialog, QLineEdit, QComboBox, QDialogButtonBox, QSpinBox, QMessageBox,QHeaderView,
    QListWidget, QListWidgetItem, QAbstractItemView
    
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt


class CreateUserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create New User")

        # Layout for the form
        layout = QVBoxLayout()

        # Form layout for user data input
        form_layout = QFormLayout()

        # Create input fields
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.user_type_input = QComboBox()
        self.user_type_input.addItems(["SingleRequest", "Recurrent"])

        # Fields for request_num and period_days
        self.request_num_input = QSpinBox()
        self.request_num_input.setMinimum(1)
        self.request_num_input.setMaximum(10000)
        
        self.period_days_input = QSpinBox()
        self.period_days_input.setMinimum(1)
        self.period_days_input.setMaximum(100)
        
        # Set initial state
        self.period_days_input.setEnabled(False)

        # Add the input fields to the form layout
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("User Type:", self.user_type_input)
        form_layout.addRow("Request Number:", self.request_num_input)
        form_layout.addRow("Period Days:", self.period_days_input)

        # Buttons for submitting or canceling
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Add form layout and buttons to the dialog layout
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # Connect the user_type input to change the state of the period_days field
        self.user_type_input.currentIndexChanged.connect(self.update_period_days_state)

    def update_period_days_state(self):
        """Enable or disable the period_days field based on user_type."""
        if self.user_type_input.currentText() == "SingleRequest":
            self.period_days_input.setEnabled(False)
            self.period_days_input.setValue(0)
        else:
            self.period_days_input.setEnabled(True)

    def get_user_data(self):
        """Return the user data entered in the dialog."""
        return {
            'name': self.name_input.text(),
            'email': self.email_input.text(),
            'user_type': self.user_type_input.currentText(),
            'request_num': self.request_num_input.value(),
            'period_days': self.period_days_input.value() if self.period_days_input.isEnabled() else None
        }
    
class UpdateUserDialog(QDialog):
    def __init__(self, user_data):
        super().__init__()
        self.setWindowTitle("Update User")

        # Layout for the form
        layout = QVBoxLayout()

        # Form layout for user data input
        form_layout = QFormLayout()

        # Create input fields with existing user data
        self.name_input = QLineEdit(user_data.name)
        self.email_input = QLineEdit(user_data.email)
        self.user_type_input = QComboBox()
        self.user_type_input.addItems(["SingleRequest", "Recurrent"])
        self.user_type_input.setCurrentText(user_data.user_type.value)

        # Fields for request_num and period_days
        self.request_num_input = QSpinBox()
        self.request_num_input.setMinimum(1)
        self.request_num_input.setMaximum(10000)
        self.request_num_input.setValue(user_data.request_num)

        self.period_days_input = QSpinBox()
        self.period_days_input.setMinimum(1)
        self.period_days_input.setMaximum(100)
        self.period_days_input.setValue(user_data.period_days or 0)

        # Set the state for period_days based on user type
        self.period_days_input.setEnabled(user_data.user_type.value == "Recurrent")

        # Add the input fields to the form layout
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("User Type:", self.user_type_input)
        form_layout.addRow("Request Number:", self.request_num_input)
        form_layout.addRow("Period Days:", self.period_days_input)

        # Buttons for submitting or canceling
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Add form layout and buttons to the dialog layout
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # Connect the user_type input to change the state of the period_days field
        self.user_type_input.currentIndexChanged.connect(self.update_period_days_state)

    def update_period_days_state(self):
        """Enable or disable the period_days field based on user_type."""
        if self.user_type_input.currentText() == "SingleRequest":
            self.period_days_input.setEnabled(False)
            self.period_days_input.setValue(0)
        else:
            self.period_days_input.setEnabled(True)

    def get_user_data(self):
        """Return the updated user data."""
        return {
            'name': self.name_input.text(),
            'email': self.email_input.text(),
            'user_type': self.user_type_input.currentText(),
            'request_num': self.request_num_input.value(),
            'period_days': self.period_days_input.value() if self.period_days_input.isEnabled() else None
        }

class MultiSelectDialog(QDialog):
    """A dialog for selecting multiple items from a list."""

    def __init__(self, title, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayout(QVBoxLayout())

        # List widget for items
        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        for item in items:
            QListWidgetItem(item, self.list_widget)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Add widgets to layout
        self.layout().addWidget(self.list_widget)
        self.layout().addWidget(self.button_box)

    def get_selected_items(self):
        """Return a list of selected items."""
        return [item.text() for item in self.list_widget.selectedItems()]

 
class UsersManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(self.create_layout())
        self.order_mng = OrdersManagementPage()

    def create_layout(self):
        """Set up the layout for the users page."""
        layout = QVBoxLayout()

        # Title Label
        label = QLabel("Users Management")
        label.setFont(QFont("Arial", 18, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: black;")
        layout.addWidget(label)

        # Table to show users
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(7)
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Email", "Type", "Request Num", "Period Days", "Last Request Date"]
        )
        self.user_table.setStyleSheet("background-color: white;")
        self.user_table.horizontalHeader().setStyleSheet("background-color: lightgray; font-size: 16;")
        self.user_table.verticalHeader().setStyleSheet("background-color: lightgray; font-size: 16;")
        # Enable auto-resize for columns and rows
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.user_table.resizeColumnsToContents()
        self.user_table.resizeRowsToContents()
        # Enable word wrapping
        self.user_table.setWordWrap(True)
        self.user_table.setFont(QFont("Arial", 12))
        self.populate_user_table()
        layout.addWidget(self.user_table)

        # Buttons for CRUD operations
        self.create_user_button = QPushButton("Create User")
        self.update_user_button = QPushButton("Update User")
        self.delete_user_button = QPushButton("Delete User")
        self.create_order_button = QPushButton("Create Order")

        self.create_user_button.clicked.connect(self.show_create_user_dialog)
        self.update_user_button.clicked.connect(self.update_user)
        self.delete_user_button.clicked.connect(self.delete_user)
        self.create_order_button.clicked.connect(self.create_order_for_selected_user)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_user_button)
        button_layout.addWidget(self.update_user_button)
        button_layout.addWidget(self.delete_user_button)
        button_layout.addWidget(self.create_order_button)  # Add new button
        layout.addLayout(button_layout)

        return layout

    def populate_user_table(self):
        """Populate the users table with data from the database."""
        users = get_all_users()
        self.user_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.name))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.email))
            self.user_table.setItem(row, 3, QTableWidgetItem(user.user_type.value))
            self.user_table.setItem(row, 4, QTableWidgetItem(str(user.request_num)))
            self.user_table.setItem(row, 5, QTableWidgetItem(str(user.period_days)))
            self.user_table.setItem(row, 6, QTableWidgetItem(str(user.last_request_date)))

    def create_order_for_selected_user(self):
        """Create an order for the selected user with city and sector selection."""
        selected_row = self.user_table.currentRow()
        if selected_row >= 0:
            user_id = self.user_table.item(selected_row, 0).text()

            # Open dialog to select cities
            cities_dialog = MultiSelectDialog("Select Cities", cities_list)
            if cities_dialog.exec_() == QDialog.Accepted:
                selected_cities = cities_dialog.get_selected_items()
                # Open dialog to select sectors
                sectors_dialog = MultiSelectDialog("Select Sectors", sectors_list)
                if sectors_dialog.exec_() == QDialog.Accepted:
                    selected_sectors = sectors_dialog.get_selected_items()

                    # Proceed with order creation
                    retrieved_posts = 0  # Set as needed or fetch dynamically
                    try:
                        create_order_for_user(user_id, email_db, retrieved_posts, selected_cities, selected_sectors)
                        QMessageBox.information(self, "Success", "Order created successfully.")
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to create order: {e}")
                else:
                    QMessageBox.warning(self, "Warning", "No sectors selected. Order creation canceled.")
            else:
                QMessageBox.warning(self, "Warning", "No cities selected. Order creation canceled.")
        else:
            QMessageBox.warning(self, "Error", "Please select a user to create an order.")

        # Update orders table
        self.order_mng.populate_order_table()


    def show_create_user_dialog(self):
        """Show the Create User dialog."""
        dialog = CreateUserDialog()
        if dialog.exec() == QDialog.Accepted:
            user_data = dialog.get_user_data()
            create_user(
                user_data['name'],
                user_data['email'],
                user_data['user_type'],
                user_data['request_num'],
                user_data['period_days']
            )
            # Refresh the table
            self.populate_user_table()  

    def update_user(self):
        """Update a selected user."""
        selected_row = self.user_table.currentRow()
        if selected_row >= 0:
            user_id = self.user_table.item(selected_row, 0).text()
            user_data = get_user_by_id(user_id)
            dialog = UpdateUserDialog(user_data)
            if dialog.exec() == QDialog.Accepted:
                updated_data = dialog.get_user_data()
                update_user(user_id, **updated_data)
                self.populate_user_table()

    def delete_user(self):
        """Delete a selected user."""
        selected_row = self.user_table.currentRow()
        if selected_row >= 0:
            user_id = self.user_table.item(selected_row, 0).text()
            delete_user(user_id)
            self.populate_user_table()
