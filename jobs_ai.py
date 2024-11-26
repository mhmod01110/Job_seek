import os
import pandas as pd
import json
import logging
import sys
import time
from datetime import datetime  # Import the datetime module
from gpt_client import client, get_response

class JobProcessor:
    def __init__(self, csv_path, log_path="job_processing.log", duration_limit=3):
        self.csv_path = csv_path
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.json_path = f"Processed_Data/emails_database/jobs_data_{current_date}.json"
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)

        self.duration_limit = duration_limit * 60
        self.job_posts = self._load_job_posts()
        self.all_jobs = []
        self.df = None  # To store the loaded DataFrame
        self._setup_logging(log_path)

    def _setup_logging(self, log_path):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def _load_job_posts(self):
        csv_files = [f for f in os.listdir(self.csv_path) if f.endswith(".csv")]
        if not csv_files:
            return []

        full_paths = [os.path.join(self.csv_path, f) for f in csv_files]
        most_recent_file = max(full_paths, key=os.path.getmtime)
        
        self.df = pd.read_csv(most_recent_file)
        
        self.df = self.df[self.df["email_count"] > 0]

        # Filter to exclude "Completed Extraction"
        filtered_df = self.df[self.df["postStatus"] != "Completed Extraction"]
        return filtered_df["text"].tolist()

    def _update_post_status(self):
        try:
            # Update the "postStatus" for processed rows
            self.df.loc[
                self.df["text"].isin(self.job_posts), "postStatus"
            ] = "Completed Extraction"
            
            # Save back to the same CSV file
            csv_file_path = os.path.join(self.csv_path, "updated_jobs.csv")
            self.df.to_csv(csv_file_path, index=False, encoding="utf-8")
            logging.info(f"Updated post statuses saved to: {csv_file_path}")
        except Exception as e:
            logging.error(f"Error updating post statuses: {e}")

    def _save_jobs_to_json(self):
        try:
            with open(self.json_path, 'w', encoding="utf-8") as json_file:
                json.dump(self.all_jobs, json_file, ensure_ascii=False, indent=4)
            logging.info("Job results have been saved to JSON file.")
        except Exception as e:
            logging.error(f"Error saving to JSON file: {e}")

    def save_jobs_to_csv_and_xlsx(self):
        try:
            # Convert the list of jobs to a DataFrame
            df = pd.DataFrame(self.all_jobs)

            # Check if the DataFrame is not empty
            if not df.empty:  
                df['date'] = pd.Timestamp('today').normalize()  # Add a date column
                
                # Save DataFrame to CSV
                csv_file_path = self.json_path.replace(".json", ".csv")
                df.to_csv(csv_file_path, index=False, encoding='utf-8')
                logging.info(f"Job results have been saved to CSV file: {csv_file_path}")

                # Save DataFrame to Excel
                xlsx_file_path = self.json_path.replace(".json", ".xlsx")
                df.to_excel(xlsx_file_path, index=False, engine='openpyxl')
                logging.info(f"Job results have been saved to Excel file: {xlsx_file_path}")
            else:
                logging.warning("No jobs to save. The DataFrame is empty.")

        except Exception as e:
            logging.error(f"Error saving to CSV or Excel files: {e}")


    async def fetch_job_post(self, prompt):
        
        return await get_response(f"Extract job information for the following ad : {prompt}", client)

    async def process_jobs(self):
        start_time = time.time()
        
        for i, prompt in enumerate(self.job_posts):
            if time.time() - start_time > self.duration_limit:
                logging.info("Time limit exceeded! Saving jobs before exit...")
                self._save_jobs_to_json()
                self._update_post_status()
                break
            else:
                try:
                    result = await self.fetch_job_post(prompt)
                    if result:
                        self.all_jobs.extend(result)
                        logging.info(f"Processed Prompt No: ({i}), which is '{prompt[:30]}' successfully ✅")
                except Exception as e:
                    logging.error(f"Error processing prompt No: ({i}) which is '{prompt[:30]}': {e}")
                    
        self._update_post_status()
        self._save_jobs_to_json()
        self.save_jobs_to_csv_and_xlsx()  

# if __name__ == "__main__":
#     try:
#         processor = JobProcessor(csv_path="filter_data.csv")
#         processor.process_jobs()
#     except KeyboardInterrupt:
#         logging.info("KeyboardInterrupt received! Saving jobs before exit...")
#         processor._save_jobs_to_json()
#         sys.exit(0)
