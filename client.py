###########################################
# ---------- Import Libraries ----------- #
###########################################
import sys
import datetime
import uuid
import requests
import os
import time
import json
from telegram_check import client, get_latest_post_number
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QLineEdit, QPushButton, 
    QFileDialog, QComboBox, QSpinBox, QMessageBox, QDialog, QTabWidget
)

###############################################
# ---------- Server URL and users ----------- #
###############################################
# Constants
SERVER_URL = "http://127.0.0.1:8000"
USER_DATA = {"admin": "admin123", "user": "user123"}

############################################
# ---------- Check paths exist ----------- #
############################################
# Define paths
paths = [
    "./Raw_Data/",
    "./Processed_Data/",
    "./Raw_Data/linkedin",
    "./Raw_Data/telegram",
    "./Processed_Data/linkedin_processed_data",
    "./Processed_Data/telegram_processed_data",
    "./Processed_Data/emails_database"
]

# Check and create paths if they don't exist
for path in paths:
    os.makedirs(path, exist_ok=True)

####################################################
# ---------- Generate random file name ----------- #
####################################################
# Utility Functions
def generate_random_filename():
    now = datetime.datetime.now()
    date_time_str = now.strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    return f"{date_time_str}_{unique_id}"

#####################################
# ---------- Login Page ----------- #
#####################################
# Login Dialog for user authentication
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Login")
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.authenticate)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password)
        layout.addWidget(self.login_button)

    def authenticate(self):
        username = self.username.text()
        password = self.password.text()
        if USER_DATA.get(username) == password:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid Username or Password")

###################################################
# ---------- GUI Of Program Client app----------- #
###################################################
class ScraperClientApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinkedIn Scraper Client")
        self.setGeometry(100, 100, 400, 600)
        self.random_filename = generate_random_filename()

        # Setup main layout with tabs
        self.tabs = QTabWidget()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(self.tabs)

        # Common server status label
        self.server_status_label = QLabel("Server Status: Unknown")
        main_layout.addWidget(self.server_status_label)

        # Create LinkedIn and Telegram Scraping Tabs
        self.linkedin_tab = self.create_linkedin_tab()
        self.tabs.addTab(self.linkedin_tab, "LinkedIn Scrap")

        self.telegram_tab = self.create_telegram_tab()
        self.tabs.addTab(self.telegram_tab, "Telegram Scrap")
        
        # Timer for periodic server status check
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_server_status)
        self.status_timer.start(5000)  # Check every 5 seconds
        
    def update_random_filename(self):
        self.random_filename = generate_random_filename()
        self.li_filtered_file_name.setText(self.random_filename)
        self.t_filtered_file_name.setText(self.random_filename)
        
    ######################################
    # ---------- Linkedin Tab----------- #
    ######################################
    def create_linkedin_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add LinkedIn specific UI components
        self.add_linkedin_ui(layout)

        return tab

    def add_linkedin_ui(self, layout):
        # Checkboxes
        search_option_label = QLabel("Search Option:")
        layout.addWidget(search_option_label)
        
        # Dropdown (ComboBox) for search options
        self.search_option_dropdown = QComboBox()
        self.search_option_dropdown.addItems(["URL", "Keywords"])  # Add options
        self.search_option_dropdown.setCurrentText("URL")  # Set "URL" as default
        layout.addWidget(self.search_option_dropdown)

        self.generate_keywords = QCheckBox("Generate Keywords From CSV file")
        layout.addWidget(self.generate_keywords)

        # Dropdown for date options
        layout.addWidget(QLabel("Select Date:"))
        self.date_combo = QComboBox()
        self.date_combo.addItems(["day", "week", "month"])
        layout.addWidget(self.date_combo)

        # Spinbox for time limit
        layout.addWidget(QLabel("Set Time Limit (0-3600 Minutes):"))
        self.time_limit = QSpinBox()
        self.time_limit.setRange(0, 3600)
        self.time_limit.setValue(100)
        layout.addWidget(self.time_limit)

        # Filtered file name entry
        layout.addWidget(QLabel("Enter Filtered File Name:"))
        self.li_filtered_file_name = QLineEdit(self.random_filename)
        layout.addWidget(self.li_filtered_file_name)
        
        # Button to toggle random filename generation
        self.generate_name_button = QPushButton("Generate Random Name")
        self.generate_name_button.clicked.connect(self.update_random_filename)
        layout.addWidget(self.generate_name_button)

        # File selection buttons
        self.select_csv_btn = QPushButton("Select CSV Keywords File")
        self.select_csv_btn.clicked.connect(self.select_csv_keywords_file)
        layout.addWidget(self.select_csv_btn)

        self.select_keywords_btn = QPushButton("Select Keywords File")
        self.select_keywords_btn.clicked.connect(self.select_keywords_file)
        layout.addWidget(self.select_keywords_btn)

        self.select_urls_btn = QPushButton("Select URLs File")
        self.select_urls_btn.clicked.connect(self.select_urls_file)
        layout.addWidget(self.select_urls_btn)

        # Scraping and processing buttons
        self.start_scraping_btn = QPushButton("Start Scraping")
        self.start_scraping_btn.clicked.connect(self.on_linkedin_scraping_button_clicked)
        layout.addWidget(self.start_scraping_btn)

        self.process_data_btn = QPushButton("Process Data")
        self.process_data_btn.clicked.connect(self.process_data)
        self.process_data_btn.setEnabled(True)
        layout.addWidget(self.process_data_btn)

        # Default file paths
        self.csv_keywords = "search_keywords/keywords.csv"
        self.keywords_path = "search_keywords/search_words.txt"
        self.urls_path = "search_keywords/urls.txt"
        self.li_raw_dir = "Raw_Data/linkedin/"
        self.li_proc_dir = "./Processed_Data/linkedin_processed_data/"

    ######################################
    # ---------- Telegram Tab----------- #
    ######################################
    def create_telegram_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add Telegram specific UI components
        self.add_telegram_ui(layout)

        return tab

    def add_telegram_ui(self, layout):
        # Initialize lists to store channel rows
        self.channel_inputs = []
        self.posts_from_inputs = []
        self.posts_to_inputs = []
        self.channel_rows = []
        self.total_posts_labels = []  # To store total posts labels

        # Create a layout to contain the dynamically added rows
        self.channel_layout = QVBoxLayout()
        layout.addWidget(QLabel("Channels, Posts From, and Posts To:"))
        layout.addLayout(self.channel_layout)

        
        # Add / Remove channel buttons
        self.add_channel_button = QPushButton("Add Channel")
        self.add_channel_button.clicked.connect(self.add_channel_row)
        layout.addWidget(self.add_channel_button)

        self.remove_channel_button = QPushButton("Remove Channel")
        self.remove_channel_button.clicked.connect(self.remove_channel_row)
        layout.addWidget(self.remove_channel_button)

        # Check Last Posts Button
        self.check_last_posts_btn = QPushButton("Check Last Posts")
        self.check_last_posts_btn.clicked.connect(self.check_channel_posts)
        layout.addWidget(self.check_last_posts_btn)
        
        # Initial row count
        self.max_channels = 10
        self.min_channels = 1
        self.channel_count = 0 
        self.add_channel_row()

        # Filtered file name entry
        layout.addWidget(QLabel("Enter Filtered File Name:"))
        self.t_filtered_file_name = QLineEdit(self.random_filename)
        layout.addWidget(self.t_filtered_file_name)
        
        # Button to toggle random filename generation
        self.generate_name_button = QPushButton("Generate Random Name")
        self.generate_name_button.clicked.connect(self.update_random_filename)
        layout.addWidget(self.generate_name_button)
        
        # Scraping and Processing button for Telegram
        self.start_telegram_scraping_btn = QPushButton("Start Telegram Scraping")
        self.start_telegram_scraping_btn.clicked.connect(self.on_telegram_scraping_button_clicked)
        layout.addWidget(self.start_telegram_scraping_btn)

        self.process_data_btn = QPushButton("Process Data")
        self.process_data_btn.clicked.connect(self.process_data)
        self.process_data_btn.setEnabled(True)
        layout.addWidget(self.process_data_btn)


        self.t_raw_dir = "Raw_Data/telegram/"
        self.t_proc_dir = "./Processed_Data/telegram_processed_data/"

    def add_channel_row(self):
        """Adds a new channel input row if within the max limit."""
        if self.channel_count < self.max_channels:
            row_layout = QHBoxLayout()

            # Channel input
            channel_input = QLineEdit()
            channel_input.setPlaceholderText(f"Channel {self.channel_count + 1}")
            row_layout.addWidget(channel_input)
            self.channel_inputs.append(channel_input)

            # Posts from input
            posts_from_input = QSpinBox()
            posts_from_input.setRange(0, 100000)
            row_layout.addWidget(QLabel("Posts From:"))
            row_layout.addWidget(posts_from_input)
            self.posts_from_inputs.append(posts_from_input)

            # Posts to input
            posts_to_input = QSpinBox()
            posts_to_input.setRange(0, 100000)
            row_layout.addWidget(QLabel("Posts To:"))
            row_layout.addWidget(posts_to_input)
            self.posts_to_inputs.append(posts_to_input)

            # Total posts label
            total_posts_label = QLabel("Total Posts: 0")
            row_layout.addWidget(total_posts_label)
            self.total_posts_labels.append(total_posts_label)

            # Add the row layout to the main channel layout
            self.channel_layout.addLayout(row_layout)
            self.channel_rows.append(row_layout)

            self.channel_count += 1

        # Disable the Add button if the max limit is reached
        self.add_channel_button.setEnabled(self.channel_count < self.max_channels)
        self.remove_channel_button.setEnabled(self.channel_count > self.min_channels)

    def remove_channel_row(self):
        """Removes the last channel input row if above the min limit."""
        if self.channel_count > self.min_channels:
            # Remove the last row layout from the main layout
            row_layout = self.channel_rows.pop()
            for i in reversed(range(row_layout.count())):
                widget = row_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

            self.channel_inputs.pop()
            self.posts_from_inputs.pop()
            self.posts_to_inputs.pop()

            self.channel_count -= 1

        # Enable the Add button if under the max limit
        self.add_channel_button.setEnabled(self.channel_count < self.max_channels)
        self.remove_channel_button.setEnabled(self.channel_count > self.min_channels)
    
    ####################################################
    # ------------ Check channel posts ----------------#
    ####################################################
    def check_channel_posts(self):
        for i, channel_input in enumerate(self.channel_inputs):
            channel_name = channel_input.text()
            if channel_name:
                with client:
                    num_posts = client.loop.run_until_complete(get_latest_post_number(channel_name))
                    self.total_posts_labels[i].setText(f"Total Posts: {num_posts}")

        
    ##########################################################
    # ---------- Files Selections for preparation ---------- #
    ##########################################################
    def select_csv_keywords_file(self):
        self.select_file("Select CSV Keywords File", "CSV Files (*.csv)", "csv_keywords")

    def select_keywords_file(self):
        self.select_file("Select Keywords File", "Text Files (*.txt)", "keywords_path")

    def select_urls_file(self):
        self.select_file("Select URLs File", "Text Files (*.txt)", "urls_path")

    def select_file(self, dialog_title, file_filter, attribute):
        file_path, _ = QFileDialog.getOpenFileName(self, dialog_title, "", file_filter)
        if file_path:
            setattr(self, attribute, file_path)
            QMessageBox.information(self, "File Selected", f"{dialog_title}: {file_path}")
    
    def on_linkedin_scraping_button_clicked(self):
        self.start_linkedin_scraping()
        self.update_random_filename()
        
    def on_telegram_scraping_button_clicked(self):
        self.start_telegram_scraping()
        self.update_random_filename()

    #############################################
    # ---------- Linkedin Scrapping ----------- #
    #############################################
    def start_linkedin_scraping(self):
        
        if not (self.keywords_path and self.urls_path):
            QMessageBox.warning(self, "Missing File", "Please select Keywords, URLs files.")
            return

        auto_process = QMessageBox.question(
            self, "Auto Process", "Do you want to process data automatically after scraping?", 
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes

        data = self.collect_scraping_data(auto_process, linkedin_signal=True)
        self.send_request(data, "start_scraping", "Linkedin Scraping", "Scraping started for Linkedin.", "Failed to extract linkedin posts", "Linkedin scraping in progress ..")


    ############################################
    # ---------- Telegram Scrapping----------- #
    ############################################
    def start_telegram_scraping(self):
        # Collect channels from the inputs
        channels = [input.text() for input in self.channel_inputs if input.text().strip()]
        
        if not channels:
            QMessageBox.warning(self, "Missing Channels", "Please specify at least one Telegram channel.")
            return
        if len(channels) > 10:
            QMessageBox.warning(self, "Too Many Channels", "You can specify a maximum of 10 channels.")
            return
            
        data = self.collect_scraping_data(auto_process=False, linkedin_signal=False, channels=channels)
        
        if not data["linkedin_signal"] and any(
            (abs(from_val.value() - to_val.value()) > 1000 or abs(from_val.value() - to_val.value()) < 1)
            for from_val, to_val in zip(self.posts_from_inputs, self.posts_to_inputs)
        ):
            print([input.value() for input in self.posts_from_inputs])
            print([input.value() for input in self.posts_to_inputs])

            QMessageBox.critical(self, "Limit Error", "Please limit the posts range to be less than 1000 and more than 0.")
            return
        auto_process = QMessageBox.question(
            self, "Auto Process", "Do you want to process data automatically after scraping?", 
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes
        data["process"] = auto_process
        payloads = self.generate_telegram_payload(data)
        print(payloads)
        for payload in payloads:
            self.send_request(payload, "start_scraping", "Telegram Scraping", "Scraping started for Telegram.", "Failed to extract telegram posts", "Telegram scraping in progress ..")
    
    ######################################################
    # ------------ Prepare telegram payload ------------ #
    ######################################################
    def generate_telegram_payload(self, data):
        channels = data['t_channel']
        posts_from_list = data['t_posts_from']
        posts_to_list = data['t_posts_to']
        payloads = []
        for channel, posts_from, posts_to in zip(channels, posts_from_list, posts_to_list):
            # Prepare individual request data for each channel
            channel_data = data.copy()
            channel_data.update({
                "t_channel": [channel],
                "t_posts_from": posts_from,
                "t_posts_to": posts_to
            })
            payloads.append(channel_data)
        return payloads
        
        

    ##################################################
    # ---------- Data processing and GPT ----------- #
    ##################################################

    def process_data(self):
        data = self.collect_scraping_data(True, linkedin_signal=self.is_linkedin_tab_active())
        self.send_request(data, "process_data", "Success ✅", "Data processed Started successfully!", "Failed to process data.", "Data processing in progress .. ")
        self.send_request(data, "gpt_extract", "Success ✅", "GPT Extraction Started Successfully!", "Failed to GPT Extract.", "GPT extraction in progress ..")
        self.process_data_btn.setEnabled(False)

    ###############################################################
    # ---------- Check Active Tab (To decide LI or T) ----------- #
    ###############################################################
    def is_linkedin_tab_active(self):
        return self.tabs.currentWidget() == self.linkedin_tab
    
    ##############################################
    # ---------- Data to-send server ----------- #
    ##############################################
    def collect_scraping_data(self, auto_process, linkedin_signal, channels=None):
        data = {
            "li_keywords_path": self.keywords_path,
            "li_urls_path": self.urls_path,
            "t_raw_dir": self.t_raw_dir,
            "t_proc_dir": self.t_proc_dir,
            "li_proc_dir": self.li_proc_dir,
            "li_raw_dir": self.li_raw_dir,
            "li_csv_keywords": self.csv_keywords,
            "filtered_file_name": self.li_filtered_file_name.text() if linkedin_signal else self.t_filtered_file_name.text(),
            "li_date": self.date_combo.currentText(),
            "li_search_with_keywords": self.search_option_dropdown.currentText() == "Keywords",
            "li_generate_combinations": self.generate_keywords.isChecked(),
            "time_limit": self.time_limit.value(),
            "process": auto_process,
            "linkedin_signal": linkedin_signal,
            "t_channel": channels,
            "t_posts_from": [input.value() for input in self.posts_from_inputs],
            "t_posts_to": [input.value() for input in self.posts_to_inputs],
        }
        return data

    ########################################
    # ---------- Send  request ----------- #
    ########################################

    def send_request(self, data, endpoint, success_title, success_message, error_message, status_message):
        self.server_status_label.setText(f"Server Status: {status_message}")
        try:
            response = requests.post(f"{SERVER_URL}/{endpoint}", json=data)
            if response.status_code == 200:
                QMessageBox.information(self, success_title, success_message)
            else:
                QMessageBox.critical(self, "Error ❌", error_message)
        except requests.RequestException as e:
            QMessageBox.critical(self, "Connection Error ❌", str(e))


    ##############################################
    # ---------- Check server status ----------- #
    ##############################################
    def check_server_status(self):
        try:
            response = requests.get(f"{SERVER_URL}/scraping_status")
            if response.status_code == 200:
                status = response.json().get("status", "Unknown")
                if status.lower() == "completed":
                    self.process_data_btn.setEnabled(True)
                self.server_status_label.setText(f"Server Status: {status}")
            else:
                self.server_status_label.setText("Server Status: Unreachable")
        except requests.RequestException:
            self.server_status_label.setText("Server Status: Unreachable")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    
    # if login_dialog.exec_() == QDialog.Accepted:
    main_window = ScraperClientApp()
    main_window.show()
    sys.exit(app.exec_())