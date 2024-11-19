import sys
import os

# Adjust the path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import from users_orders_manager
from users_orders_manager.interface import *  # Replace with the actual functions or classes you need

# Import pandas if it's not already imported
import pandas as pd

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QSpinBox, QMessageBox, QPushButton, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


# Dialog to Create New Email Record
class CreateEmailRecordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create New Email Record")

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.email_input = QLineEdit()
        self.city_input = QLineEdit()
        self.region_input = QLineEdit()
        self.sectors_input = QLineEdit()

        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("City (comma-separated):", self.city_input)
        form_layout.addRow("Region (comma-separated):", self.region_input)
        form_layout.addRow("Sectors (comma-separated):", self.sectors_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_email_data(self):
        """Return the email data entered in the dialog."""
        return {
            'email': self.email_input.text(),
            'city': self.city_input.text().split(','),
            'region': self.region_input.text().split(','),
            'sectors': self.sectors_input.text().split(',')
        }


# Dialog to Update Email Record
class UpdateEmailRecordDialog(QDialog):
    def __init__(self, email_data):
        super().__init__()
        self.setWindowTitle("Update Email Record")

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.email_input = QLineEdit(email_data['email'])
        self.city_input = QLineEdit(', '.join(email_data['city']))
        self.region_input = QLineEdit(', '.join(email_data['region']))
        self.sectors_input = QLineEdit(', '.join(email_data['sectors']))

        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("City (comma-separated):", self.city_input)
        form_layout.addRow("Region (comma-separated):", self.region_input)
        form_layout.addRow("Sectors (comma-separated):", self.sectors_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_email_data(self):
        """Return the updated email data."""
        return {
            'email': self.email_input.text(),
            'city': self.city_input.text().split(','),
            'region': self.region_input.text().split(','),
            'sectors': self.sectors_input.text().split(',')
        }


# Emails Management Page
class EmailsManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(self.create_layout())

    def create_layout(self):
        layout = QVBoxLayout()

        # Title Label
        label = QLabel("Emails Management")
        label.setFont(QFont("Arial", 18, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: black;")
        layout.addWidget(label)

        # Table to show email records
        self.email_table = QTableWidget()
        self.email_table.setColumnCount(4)
        self.email_table.setHorizontalHeaderLabels(["Email", "City", "Region", "Sectors"])
        self.populate_email_table()
        layout.addWidget(self.email_table)

        # Buttons for CRUD operations
        self.create_email_button = QPushButton("Create Email Record")
        self.update_email_button = QPushButton("Update Email Record")
        self.delete_email_button = QPushButton("Delete Email Record")

        self.create_email_button.clicked.connect(self.show_create_email_dialog)
        self.update_email_button.clicked.connect(self.update_email_record)
        self.delete_email_button.clicked.connect(self.delete_email_record)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_email_button)
        button_layout.addWidget(self.update_email_button)
        button_layout.addWidget(self.delete_email_button)
        layout.addLayout(button_layout)

        return layout

    def populate_email_table(self):
        """Populate the email records table with data from the email_db."""
        global email_db

        # Set the number of rows in the table based on the number of records
        self.email_table.setRowCount(len(email_db))

        # Populate the table with data
        for row in range(len(email_db)):
            email = email_db["email"].iloc[row]
            city = ", ".join(email_db["city"].iloc[row])
            region = ", ".join(email_db["region"].iloc[row])
            sectors = ", ".join(email_db["sectors"].iloc[row])

            self.email_table.setItem(row, 0, QTableWidgetItem(email))
            self.email_table.setItem(row, 1, QTableWidgetItem(city))
            self.email_table.setItem(row, 2, QTableWidgetItem(region))
            self.email_table.setItem(row, 3, QTableWidgetItem(sectors))

    def show_create_email_dialog(self):
        """Show the Create Email Record dialog."""
        dialog = CreateEmailRecordDialog()
        if dialog.exec() == QDialog.Accepted:
            email_data = dialog.get_email_data()
            self.add_email_record(email_data)
            self.populate_email_table()

    def update_email_record(self):
        """Update a selected email record."""
        selected_row = self.email_table.currentRow()
        if selected_row >= 0:
            email = self.email_table.item(selected_row, 0).text()

            # Get the current email data
            email_data = self.get_email_data_by_email(email)

            # Show the update dialog
            dialog = UpdateEmailRecordDialog(email_data)
            if dialog.exec() == QDialog.Accepted:
                updated_data = dialog.get_email_data()
                self.update_email_record_in_db(email, updated_data)
                self.populate_email_table()

    def delete_email_record(self):
        """Delete a selected email record."""
        selected_row = self.email_table.currentRow()
        if selected_row >= 0:
            email = self.email_table.item(selected_row, 0).text()
            self.delete_email_record_from_db(email)
            self.populate_email_table()

    def get_email_data_by_email(self, email):
        """Retrieve email record data by email."""
        global email_db
        record = email_db[email_db['email'] == email].iloc[0]
        return {
            'email': record['email'],
            'city': record['city'],
            'region': record['region'],
            'sectors': record['sectors']
        }

    def add_email_record(self, email_data):
        """Add a new email record to the database."""
        global email_db
        new_record = pd.DataFrame([email_data])
        email_db = pd.concat([email_db, new_record], ignore_index=True)
        email_db = group_email_db(email_db)

    def update_email_record_in_db(self, email, updated_data):
        """Update an existing email record in the database."""
        global email_db
        email_db.loc[email_db['email'] == email, ['city', 'region', 'sectors']] = [updated_data['city'], updated_data['region'], updated_data['sectors']]
        email_db = group_email_db(email_db)

    def delete_email_record_from_db(self, email):
        """Delete an email record from the database."""
        global email_db
        email_db = email_db[email_db['email'] != email]
        email_db = group_email_db(email_db)
