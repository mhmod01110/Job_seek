import sys
import os

# Adjust the path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import from users_orders_manager
from users_orders_manager.interface import *
from emails_page import *
from users_page import *
from orders_page import *

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QStackedWidget, QLabel, QPushButton, QFormLayout, QTableWidget, QTableWidgetItem,
    QDialog, QLineEdit, QComboBox, QDialogButtonBox, QSpinBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Management Program")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("background-color: #ecf0f1;")
        self.icons_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icons"))

        # Main layout
        main_layout = QVBoxLayout()

        # Header
        header = QLabel("📊 Data Management Program")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("background-color: #34495e; color: white; padding: 10px;")
        main_layout.addWidget(header)

        # Content layout
        content_layout = QHBoxLayout()

        # Sidebar
        self.tree_widget = QTreeWidget()
        self.tree_widget.setFixedWidth(250)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #2c3e50;
                color: white;
                border: none;
            }
            QTreeWidget::item {
                padding: 8px;
                font-size: 16px;
            }
            QTreeWidget::item:selected {
                background-color: #16a085;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #44d6db;
            }
        """)
        self.tree_widget.currentItemChanged.connect(self.display_page)

        # Main area (StackedWidget)
        self.stacked_widget = QStackedWidget()

        # Emails Management Page
        self.emails_page = EmailsManagementPage()
        self.add_tree_item("Emails Management", "emails.png", 0)
        self.stacked_widget.addWidget(self.emails_page)  # index 0
        
        # Users Management Page
        self.users_page = UsersManagementPage()
        self.add_tree_item("Users Management", "users.png", 1)
        self.stacked_widget.addWidget(self.users_page)  # index 1

        # Orders Management Page
        self.orders_page = OrdersManagementPage()
        self.add_tree_item("Orders Management", "orders.png", 2)
        self.stacked_widget.addWidget(self.orders_page)  # index 2

        # Combine layouts
        content_layout.addWidget(self.tree_widget)
        content_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    def add_tree_item(self, text, icon_file, page_index):
        """Add an item to the sidebar."""
        item = QTreeWidgetItem()
        item.setText(0, text)
        icon_path = os.path.join(self.icons_path, icon_file)
        item.setIcon(0, QIcon(icon_path))
        item.setData(0, Qt.UserRole, page_index)
        self.tree_widget.addTopLevelItem(item)


    def display_page(self, current, previous):
        """Switch pages and refresh data if needed."""
        if current:
            page_index = current.data(0, Qt.UserRole)
            self.stacked_widget.setCurrentIndex(page_index)
            
            # Automatically populate data when switching to Users or Orders page
            if page_index == 1:  # Users Management page
                self.users_page.populate_user_table()  # Refresh users data
            elif page_index == 2:  # Orders Management page
                self.orders_page.populate_order_table()  # Refresh orders data


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
