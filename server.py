#############################################
# ------------ Import Libraries ----------- #
#############################################
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel
from typing import List
from time import time
import logging
import sys
import asyncio
from collections import deque

# Other imports remain the same...
from config import APIFY_API_TOKEN, COOKIES
from scrap_manager import LinkedInScraperManager, TelegramScraperManager
from data_processing import LinkedInCSVProcessor, TelegramCSVProcessor
from jobs_ai import JobProcessor


###############################################
# ------------ Create fastapi app ----------- #
###############################################
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request Queue
MAX_QUEUE_LENGTH = 20
request_queue = deque(maxlen=MAX_QUEUE_LENGTH)

# Queue processing status
is_processing = False

# Scraping status tracking
scraping_status = {"status": "Idle"}

# ######################################
# # --------- API Limitaions --------- #
# ######################################
# # Semaphore to limit concurrent tasks
# MAX_CONCURRENT_TASKS = 3
# semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

# # Rate limit configuration
# RATE_LIMIT_SECONDS = 60  # Time window in seconds
# MAX_REQUESTS = 1         # Max requests allowed per window

# # Dictionary to track request times per IP
# post_request_log = {}
# @app.middleware("http")
# async def rate_limit_post_requests(request: Request, call_next):
#     if request.method == "POST":
#         client_ip = request.client.host  # Get the client's IP address
#         current_time = time()
        
#         # Check if this IP has made a recent POST request
#         if client_ip in post_request_log:
#             last_request_time = post_request_log[client_ip]
            
#             # If the time since the last POST request is within the limit, raise an exception
#             if current_time - last_request_time < RATE_LIMIT_SECONDS:
#                 raise HTTPException(
#                     status_code=429,
#                     detail="Too Many POST Requests: Please wait before making another POST request."
#                 )

#         # Update the log with the current POST request time
#         post_request_log[client_ip] = current_time
    
#     # Proceed with the request
#     response = await call_next(request)
#     return response

##################################################
# ------------ Default server Status ----------- #
##################################################
# To keep track of the scraping status
scraping_status = {"status": "Idle"}

#############################################
# ------------ Data transfered  ----------- #
#############################################
class ScrapeRequest(BaseModel):
    li_keywords_path: str
    li_urls_path: str
    t_raw_dir: str
    li_raw_dir: str
    li_proc_dir: str
    t_proc_dir: str
    li_csv_keywords: str
    filtered_file_name: str
    li_date: str
    li_search_with_keywords: bool
    li_generate_combinations: bool
    time_limit: int
    process: bool
    linkedin_signal: bool
    t_channel: List[str] | None | List[None]
    t_posts_from: int  
    t_posts_to: int

################################################
# ------------ Scraping Async task ----------- #
################################################
async def process_queue():
    global is_processing

    while True:
        if request_queue and not is_processing:
            scrape_request = request_queue.popleft()
            await start_scraping_task(scrape_request)
            print("do start scrapping task")
        else:
            logger.info("Queue is empty, waiting for requests...")
            print("not to do start scrapping task")
        await asyncio.sleep(60)  # Wait for 5 minutes

async def start_scraping_task(scrape_request: ScrapeRequest):
    global is_processing
    is_processing = True
    scraping_status["status"] = "Scraping In Progress .."
    print("start scrap taaaask")
    try:
        # Choose the appropriate scraper manager based on linkedin_signal
        if scrape_request.linkedin_signal:
            manager = LinkedInScraperManager(
                api_token=APIFY_API_TOKEN,
                cookies=COOKIES,
                keywords_path=scrape_request.li_keywords_path,
                urls_path=scrape_request.li_urls_path,
                save_path=scrape_request.li_raw_dir,
                csv_keywords=scrape_request.li_csv_keywords,
                date=scrape_request.li_date,
                search_with_keywords=scrape_request.li_search_with_keywords,
                generate_combinations=scrape_request.li_generate_combinations,
                time_limit=scrape_request.time_limit
            )
        else:
            print("start scrap taaaask telegram")
            
            manager = TelegramScraperManager(
                api_token=APIFY_API_TOKEN,
                channels=scrape_request.t_channel,
                save_path=scrape_request.t_raw_dir,
                posts_from=scrape_request.t_posts_from,
                posts_to=scrape_request.t_posts_to,
                time_limit=scrape_request.time_limit
            )

        await manager.start_scraping()
        scraping_status["status"] = "Completed"
        
        # Automatic data processing if requested
        if scrape_request.process:
            raw_dir = scrape_request.li_raw_dir if scrape_request.linkedin_signal else scrape_request.t_raw_dir
            proc_dir = scrape_request.li_proc_dir if scrape_request.linkedin_signal else scrape_request.t_proc_dir
            processor_class = LinkedInCSVProcessor if scrape_request.linkedin_signal else TelegramCSVProcessor
            process_data(raw_dir, proc_dir, scrape_request.filtered_file_name, scrape_request.linkedin_signal, processor_class)
            scraping_status["status"] += " - Processing Complete"
            csv_path = f"Processed_Data/{'linkedin' if scrape_request.linkedin_signal else 'telegram'}_processed_data"
            await gpt_extract(csv_path)
            scraping_status["status"] += " - GPT Extract Complete"

    except Exception as e:
        scraping_status["status"] = f"Failed: {e}"
        logger.error(f"Scraping failed: {e}")
    finally:
        is_processing = False
        
##########################################
# ------------ Async Process ----------- #
##########################################
async def start_process_task(scrape_request: ScrapeRequest):
    scraping_status["status"] = "Processing In Progress .."
    raw_dir = scrape_request.li_raw_dir if scrape_request.linkedin_signal else scrape_request.t_raw_dir
    proc_dir = scrape_request.li_proc_dir if scrape_request.linkedin_signal else scrape_request.t_proc_dir
    processor_class = LinkedInCSVProcessor if scrape_request.linkedin_signal else TelegramCSVProcessor
    try:
        process_data(raw_dir, proc_dir, scrape_request.filtered_file_name, scrape_request.linkedin_signal, processor_class)
        scraping_status["status"] += " - Processing Complete"
    except Exception as e:
        scraping_status["status"] = f"Failed: {e}"
        logger.error(f"Processing failed: {e}")
        
###########################################
# ------------ Data processor ----------- #
###########################################
def process_data(raw_dir: str, proc_dir: str, filtered_file_name: str, linkedin_signal: bool, processor_class):
    try:
        processor = processor_class(raw_dir, proc_dir)        
        processor.process(
            'postedAtTimestamp' if linkedin_signal else 'date',
            'postTime',
            f"{filtered_file_name}.csv",  
            f"{filtered_file_name}.xlsx"  
        )
    except Exception as e:
        logger.error(f"Data processing failed: {e}")

###########################################
# ------------ GPT Extraction ----------- #
###########################################
async def gpt_extract(csv_path: str):
    scraping_status["status"] = "Start GPT Extraction .."
    try:
        processor = JobProcessor(csv_path=csv_path)
        await processor.process_jobs()
        scraping_status["status"] = " - GPT Extraction Complete"
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received! Saving jobs before exit...")
        processor._save_jobs_to_json()
        sys.exit(0)
    except Exception as e:
        logger.error(f"GPT extraction failed: {e}")
        
#######################################
# ------------ End-points ----------- #
#######################################
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_queue())

@app.post("/start_scraping")
async def start_scraping(scrape_request: ScrapeRequest):
    if len(request_queue) < MAX_QUEUE_LENGTH:
        request_queue.append(scrape_request)
        return {"message": "Scraping request added to the queue."}
    else:
        raise HTTPException(status_code=429, detail="Queue is full. Please try again later.")


@app.post("/process_data")
async def start_process(scrape_request: ScrapeRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(start_process_task, scrape_request)
    return {"message": "Processing started"}

@app.post("/gpt_extract")
async def start_extract(scrape_request: ScrapeRequest, background_tasks: BackgroundTasks):
    csv_path = f"Processed_Data/{'linkedin' if scrape_request.linkedin_signal else 'telegram'}_processed_data"
    background_tasks.add_task(gpt_extract, csv_path)
    return {"message": "GPT extraction started"}

@app.get("/scraping_status")
def get_scraping_status():
    return {"status": scraping_status["status"]}
