import logging
import json
import csv
import asyncio
from apify_client import ApifyClient
from datetime import datetime

# ----------------- Posts Scraper -------------------- #

class ApifyLinkedInScraper:
    def __init__(self, api_token, cookies, country="US", search_with_keywords=True, date="week"):
        self.client = ApifyClient(api_token)
        self.cookies = cookies
        self.country = country
        self.date = date
        self.search_with_keywords = search_with_keywords  # Control source of link
        self.logger = self.setup_logger()

    def setup_logger(self):
        """Sets up the logger for Apify client"""
        logger = logging.getLogger('apify_client')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        return logger

    def adjust_link(self, keyword=None, url=None):
        """Adjusts the search link based on the keyword, date, or direct URL"""
        if not self.search_with_keywords and url:
            return url  # Use the direct URL if search_with_keywords is False
        
        # Default to keyword search link if no URL is provided
        date_posted = {"day": "past-24h", "week": "past-week", "month": "past-month"}
        return f"https://www.linkedin.com/search/results/content/?datePosted={date_posted[self.date]}&keywords={keyword}&sortBy=%22date_posted%22"

    def get_run_input(self,keyword=None, url=None):
        """Prepares the input configuration for the Apify actor based on the keyword or URL"""
        post_link = self.adjust_link(keyword=keyword, url=url)
        return {
            "cookie": self.cookies,
            "urls": [post_link],
            "deepScrape": False,
            "rawData": False,
            "minDelay": 2,
            "maxDelay": 5,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyCountry": self.country,
            },
        }

    async def run_scraper(self, keyword=None, url=None):
        """Executes the LinkedIn scraper asynchronously for a given keyword or URL"""
        run_input = self.get_run_input(keyword=keyword, url=url)
        run = await asyncio.to_thread(self.client.actor("curious_coder/linkedin-post-search-scraper").call, run_input=run_input)
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


