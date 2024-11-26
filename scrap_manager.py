import asyncio
import os
from crawlers.linkedin_apify import ApifyLinkedInScraper
from crawlers.telegram_apify import ApifyTelegramScraper
from search_keywords.keywords_comb import KeywordCombinations
from config import APIFY_API_TOKEN

# -------------------- Linkedin Scrap manager --------------------- #
class LinkedInScraperManager:
    def __init__(self, api_token,
                 cookies,
                 keywords_path,
                 urls_path,
                 save_path,
                 csv_keywords,
                 date="month", 
                 max_workers=5,
                 search_with_keywords=True,
                 generate_combinations=True,
                 time_limit=100):
        
        self.scraper = ApifyLinkedInScraper(api_token, cookies, date=date, search_with_keywords=search_with_keywords)
        self.keywords_path = keywords_path
        self.urls_path = urls_path
        self.save_path = save_path
        self.date = date
        self.max_workers = max_workers
        self.search_with_keywords = search_with_keywords
        self.generate_combinations = generate_combinations
        self.csv_keywords = csv_keywords
        self.queue = asyncio.Queue()
        self.time_limit = time_limit  # Time limit in minutes

        # Generate or read combinations
        if self.search_with_keywords:
            self.load_keywords()

    def load_keywords(self):
        if self.generate_combinations:
            print("Generating keyword combinations...")
            KeywordCombinations.generate_and_save_combinations(self.csv_keywords, self.keywords_path)
        else:
            print("Reading keyword combinations from file...")
            if not os.path.exists(self.keywords_path):
                print("Keyword file not found, generating new combinations...")
                KeywordCombinations.generate_and_save_combinations(self.csv_keywords, self.keywords_path)

    async def _load_inputs(self):
        if self.search_with_keywords:
            inputs = KeywordCombinations.read_from_text(self.keywords_path)
        else:
            with open(self.urls_path, 'r') as f:
                inputs = [line.strip() for line in f if line.strip()]
                
        for input_value in inputs[:5]:
            await self.queue.put(input_value)

    async def _worker(self):
        while True:
            input_value = await self.queue.get()
            if self.search_with_keywords:
                print(f"Worker scraping for keyword: {input_value} with date: {self.date}")
                run_id = await self.scraper.run_scraper(keyword=input_value)
            else:
                print(f"Worker scraping for URL: {input_value}")
                run_id = await self.scraper.run_scraper(url=input_value)
            
            dataset_id = await self.scraper.monitor_scraping(run_id)
            
            if dataset_id:
                results = await self.scraper.fetch_results(dataset_id)
                filename_prefix = os.path.join(self.save_path, dataset_id)
                json_filename = f"{filename_prefix}_results.json"
                csv_filename = f"{filename_prefix}_results.csv"
                self.scraper.save_results_json(results, json_filename)
                self.scraper.save_results_csv(results, csv_filename)
            
            self.queue.task_done()

    async def start_scraping(self):
        await self._load_inputs()
        workers = [asyncio.create_task(self._worker()) for _ in range(self.max_workers)]
        
        # Monitor the scraping process with a time limit
        try:
            if self.time_limit:
                await asyncio.wait_for(self.queue.join(), timeout=self.time_limit * 60)
            else:
                await self.queue.join()
        except asyncio.TimeoutError:
            print("Time limit reached, stopping scraping...")
        
        for worker in workers:
            worker.cancel()



# -------------------- Telegram Scrap manager --------------------- #

class TelegramScraperManager:
    def __init__(self, api_token, channels, save_path, posts_from=10, posts_to=20, max_workers=1, time_limit=100):
        """
        Initializes the Telegram scraper manager with required parameters.
        """
        self.scraper = ApifyTelegramScraper(api_token, channels, posts_from=posts_from, posts_to=posts_to)
        self.channels = channels
        self.save_path = save_path
        self.posts_from = posts_from
        self.posts_to = posts_to
        self.max_workers = max_workers
        self.queue = asyncio.Queue()
        self.time_limit = time_limit  # Time limit in minutes

    async def _load_channels(self):
        """
        Loads the channels into the queue for scraping.
        """
        for channel in self.channels:
            await self.queue.put(channel)

    async def _worker(self):
        """
        Worker to process each channel, run the scraper, monitor scraping, and save results.
        """
        while True:
            channel = await self.queue.get()
            print(f"Worker scraping for channel: {channel}")
            run_id = await self.scraper.run_scraper()  # Start the scraper run
            dataset_id = await self.scraper.monitor_scraping(run_id)  # Monitor the run status
            
            if dataset_id:
                results = await self.scraper.fetch_results(dataset_id)
                filename_prefix = os.path.join(self.save_path, f"{channel}_{dataset_id}")
                json_filename = f"{filename_prefix}_results.json"
                csv_filename = f"{filename_prefix}_results.csv"
                
                # Save results
                self.scraper.save_results_json(results, json_filename)
                self.scraper.save_results_csv(results, csv_filename)
            
            self.queue.task_done()

    async def start_scraping(self):
        """
        Starts the scraping process with the specified number of workers and time limit.
        """
        await self._load_channels()  # Load channels into the queue
        workers = [asyncio.create_task(self._worker()) for _ in range(self.max_workers)]
        
        # Monitor the scraping process with a time limit
        try:
            if self.time_limit:
                await asyncio.wait_for(self.queue.join(), timeout=self.time_limit * 60)
            else:
                await self.queue.join()
        except asyncio.TimeoutError:
            print("Time limit reached, stopping scraping...")
        
        for worker in workers:
            worker.cancel()

# if __name__ == "__main__":
#     async def scrap_main():
#         manager = LinkedInScraperManager(
#             api_token=APIFY_API_TOKEN,
#             cookies=COOKIES,
#             keywords_path="search_keywords/search_words.txt",
#             urls_path="search_keywords/urls.txt",
#             save_path="database2/",
#             date="day",
#             search_with_keywords=True,
#             generate_combinations=True,
#             time_limit=10  # Set your desired time limit here in minutes
#         )
#         await manager.start_scraping()

#     asyncio.run(scrap_main())


# async def main():
#     # Configuration
#     api_token = APIFY_API_TOKEN  # Replace with your actual API token or import from config
#     channels = ["Taras_saudi"]  # Replace with actual Telegram channel handles
#     save_path = "./Raw_Data/telegram"  # Directory where the results will be saved
#     max_workers = 3  # Number of concurrent workers for scraping
#     time_limit = 60  # Time limit in minutes for scraping
#     posts_from = 5000  # Start of posts range
#     posts_to = 5100    # End of posts range
    
#     # Initialize and start the Telegram scraper manager
#     scraper_manager = TelegramScraperManager(
#         api_token=api_token,
#         channels=channels,
#         save_path=save_path,
#         posts_from=posts_from,
#         posts_to=posts_to,
#         max_workers=max_workers,
#         time_limit=time_limit
#     )
    
#     await scraper_manager.start_scraping()

# # Entry point for asynchronous main function
# if __name__ == "__main__":
#     asyncio.run(main())