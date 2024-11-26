import pandas as pd
import os
import re
from datetime import datetime

# ------------- CSV Processor base ----------------- #
class CSVProcessorBase:
    def __init__(self, directory_path: str, save_dir: str):
        """
        Initialize the processor with the directory path where CSV files are stored and save directory.
        """
        self.directory_path = directory_path
        self.save_dir = save_dir
        self.df = None
        self.accounts = None

    def merge_csv_files(self) -> pd.DataFrame:
        """
        Merges all CSV files in the directory into a single DataFrame with an added source file column.
        """
        dataframes = []
        for filename in os.listdir(self.directory_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.directory_path, filename)
                df = pd.read_csv(file_path)
                df['source_file'] = filename.replace('.csv', '')
                dataframes.append(df)
        
        if dataframes:
            self.df = pd.concat(dataframes, ignore_index=True)
        else:
            print("No CSV files found in the directory. ⚠️")
            self.df = pd.DataFrame()
        return self.df

    def fill_missing_values(self, value: str = "-"):
        if self.df is not None:
            self.df.fillna(value, inplace=True)
        else:
            print("DataFrame is empty. No missing values to fill.")

    def extract_emails(self, text: str) -> tuple[str, int]:
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        text = text if isinstance(text, str) else ''
        emails = re.findall(email_regex, text)
        return str(emails), len(emails)

    def extract_links(self, text: str) -> tuple[str, int]:
        url_regex = r'(https?://[^\s]+)'
        text = text if isinstance(text, str) else ''
        links = re.findall(url_regex, text)
        return str(links), len(links)

    def process_emails_column(self):
        if self.df is not None and 'text' in self.df.columns:
            self.df[['emails', 'email_count']] = self.df['text'].apply(
                lambda x: pd.Series(self.extract_emails(x)))
        else:
            print("No 'text' column found in the DataFrame. ⚠️")

    def process_links_column(self):
        if self.df is not None and 'text' in self.df.columns:
            self.df[['links', 'link_count']] = self.df['text'].apply(
                lambda x: pd.Series(self.extract_links(x)))
        else:
            print("No 'text' column found in the DataFrame. ⚠️")

    def convert_timestamps(self, timestamp_column: str, new_column_name: str):
        raise NotImplementedError("This method should be implemented in the subclass.")

    def add_status_column(self):
        self.df["postStatus"] = "Empty"

    def process(self, timestamp_column: str, new_column_name: str, email_csv_filename: str, email_excel_filename: str):
        self.merge_csv_files()
        self.fill_missing_values()
        self.process_emails_column()
        self.process_links_column()
        self.convert_timestamps(timestamp_column, new_column_name)
        self.add_status_column()
        self.drop_unimportant()
        self.save_processed_data(email_csv_filename, email_excel_filename)

    def drop_unimportant(self):
        raise NotImplementedError("This method should be implemented in the subclass.")

    def save_processed_data(self, email_csv_filename: str = 'filtered_data.csv', email_excel_filename: str = 'filtered_data.xlsx'):
        os.makedirs(self.save_dir, exist_ok=True)
        email_csv_filepath = os.path.join(self.save_dir, email_csv_filename)
        email_excel_filepath = os.path.join(self.save_dir, email_excel_filename)
        
        if self.df is not None and not self.df.empty:
            filtered_df = self.df[(self.df['email_count'] > 0) | (self.df['link_count'] > 0)].drop_duplicates().reset_index(drop=True)
            if not filtered_df.empty:
                filtered_df.to_csv(email_csv_filepath, index=True, index_label="Index")
                filtered_df.to_excel(email_excel_filepath, index=True, index_label="Index")
                print(f"Filtered data saved ✅ to {email_csv_filepath} and {email_excel_filepath}")
            else:
                print("No data where email_count > 0 ⚠️")
        else:
            print("DataFrame is empty. Nothing to save. ⚠️")
    
# ------------- Linkedin CSV Processor ----------------- #
class LinkedInCSVProcessor(CSVProcessorBase):
    def convert_timestamps(self, timestamp_column: str, new_column_name: str):
        if self.df is not None and timestamp_column in self.df.columns:
            self.df[new_column_name] = pd.to_datetime(self.df[timestamp_column], unit='ms')
        else:
            print(f"No '{timestamp_column}' column found in the DataFrame.")
            
    def drop_unimportant(self):
        if self.df is not None:
            self.df.drop(columns=["authorProfileId", "inputUrl", "postedAtTimestamp", "urn"], inplace=True)
        else:
            print("DataFrame is empty. No columns to drop.")

# ------------- Telegram CSV Processor ----------------- #
class TelegramCSVProcessor(CSVProcessorBase):
    def convert_timestamps(self, timestamp_column: str, new_column_name: str):
        if self.df is not None and timestamp_column in self.df.columns:
            self.df[new_column_name] = pd.to_datetime(self.df[timestamp_column]).dt.tz_convert(None)
        else:
            print(f"No '{timestamp_column}' column found in the DataFrame.")
            
    def drop_unimportant(self):
        if self.df is not None:
            self.df.drop(columns=["id"], inplace=True)
        else:
            print("DataFrame is empty. No columns to drop.")



# # Usage
# dir_path = "./Raw_Data/telegram"
# save_dir = "./Processed_Data/telegram_processed_data"
# processor = TelegramCSVProcessor(dir_path, save_dir)

# # Call the process method to execute all steps in sequence
# processor.process(
#     'date',  # The timestamp column you want to convert
#     'postTime',           # The new column name for converted timestamps
#     'filter_data2.csv',     # CSV file to save rows where email_count | link_count > 0
#     'filter_data2.xlsx',    # Excel file to save rows where email_count | link_count > 0

# )

# # # Usage
# dir_path = "./Raw_Data/linkedin"
# save_dir = "./Processed_Data/linkedin_processed_data"
# processor = LinkedInCSVProcessor(dir_path, save_dir)

# # Call the process method to execute all steps in sequence
# processor.process(
#     'postedAtTimestamp',  # The timestamp column you want to convert
#     'postTime',           # The new column name for converted timestamps
#     'filter_data2.csv',     # CSV file to save rows where email_count | link_count > 0
#     'filter_data2.xlsx',    # Excel file to save rows where email_count | link_count > 0

# )