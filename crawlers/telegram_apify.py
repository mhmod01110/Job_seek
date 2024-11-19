import time
import logging
import json
import csv
import asyncio
from apify_client import ApifyClient
from datetime import datetime
from config import APIFY_API_TOKEN

# ----------------- Telegram Channels Scraper -------------------- #

class ApifyTelegramScraper:
    def __init__(self, api_token, channels, posts_from=10, posts_to=20):
        self.client = ApifyClient(api_token)
        self.channels = channels
        self.posts_from = posts_from
        self.posts_to = posts_to
        self.logger = self.setup_logger()

    def setup_logger(self):
        """Sets up the logger for Apify client"""
        logger = logging.getLogger('apify_client')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        return logger

    def get_run_input(self):
        """Prepares the input configuration for the Apify Telegram actor"""
        return {
            "channels": self.channels,
            "postsFrom": self.posts_from,
            "postsTo": self.posts_to,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            },
        }

    async def run_scraper(self):
        """Executes the Telegram scraper asynchronously for the given channels"""
        run_input = self.get_run_input()
        run = await asyncio.to_thread(self.client.actor("73JZk4CeKcDsWoJQu").call, run_input=run_input)
        return run["id"]

    async def monitor_scraping(self, run_id):
        """Monitors the scraping task asynchronously until completion"""
        self.logger.info(f"Scraping in progress... (Run ID: {run_id}) 🔃🔃")
        while True:
            run_info = await asyncio.to_thread(self.client.run(run_id).get)
            status = run_info["status"]
            if status == "SUCCEEDED":
                self.logger.info(f"Run {run_id} SUCCEEDED! ✅")
                return run_info["defaultDatasetId"]
            elif status in ["FAILED", "ABORTED"]:
                self.logger.error(f"Run {run_id} failed! ❌")
                return None
            await asyncio.sleep(5)

    async def fetch_results(self, dataset_id):
        """Fetches and returns the scraped results asynchronously"""
        dataset_items = await asyncio.to_thread(self.client.dataset(dataset_id).list_items, limit=100)
        return dataset_items.items

    def save_results_json(self, items, filename):
        """Saves the results to a JSON file"""
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for item in items:
            item['scrappingDate'] = current_datetime
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=4)
        self.logger.info(f"Results saved to {filename}")

    def save_results_csv(self, items, filename):
        """Saves the results to a CSV file"""
        if not items:
            self.logger.warning(f"No items to save in {filename}")
            return
        
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Add 'scrapping date' to each item
        for item in items:
            item['scrappingDate'] = current_datetime
            
        keys = set()
        for item in items:
            keys.update(item.keys())

        fieldnames = sorted(keys)
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=fieldnames)
            dict_writer.writeheader()
            dict_writer.writerows(items)
        self.logger.info(f"Results saved to {filename}")

# async def main():
#     # Replace these with your actual Apify API token and channel details
#     api_token = APIFY_API_TOKEN
#     channels = ["Taras_saudi"]  # List of Telegram channels to scrape
#     posts_from = 5000  # Start index for posts
#     posts_to = 5100   # End index for posts
    
#     # Initialize the scraper
#     scraper = ApifyTelegramScraper(api_token, channels, posts_from, posts_to)
    
#     # Run the scraper
#     run_id = await scraper.run_scraper()
#     if not run_id:
#         print("Failed to start scraper.")
#         return
    
#     # Monitor the scraping process until completion
#     dataset_id = await scraper.monitor_scraping(run_id)
#     if not dataset_id:
#         print("Scraping failed or was aborted.")
#         return
    
#     # Fetch the scraping results
#     items = await scraper.fetch_results(dataset_id)
    
#     # Save results to JSON and CSV files
#     if items:
#         scraper.save_results_json(items, "telegram_results.json")
#         scraper.save_results_csv(items, "telegram_results.csv")
#         print("Results saved to JSON and CSV files.")
#     else:
#         print("No data found to save.")

# # Run the main function
# if __name__ == "__main__":
#     asyncio.run(main())
