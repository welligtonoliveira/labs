#!/usr/bin/env python3
import csv
import logging
import os
import requests
import time
from dotenv import load_dotenv

# Configuration
load_dotenv()
API_URL = "https://api.noverde.com/platform-disbursement-public-api/v1/moneyplus/callback"
API_KEY = os.getenv("API_KEY")
CSV_FILE = "result_query.csv"
PROCESSED_FILE = "processed_ids.txt"
LOG_FILE = "audit.log"

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setup_logging():
    """Configures logging significantly for audit purposes."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

def load_processed_ids():
    """Loads previously processed identifiers to ensure persistence."""
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_processed_id(identifier):
    """Saves a processed identifier to the persistence file."""
    with open(PROCESSED_FILE, 'a') as f:
        f.write(f"{identifier}\n")

def process_disbursements():
    setup_logging()
    processed_ids = load_processed_ids()
    logging.info(f"Loaded {len(processed_ids)} already processed IDs.")

    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
    }

    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Normalize column names in case of whitespace
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            
            for row in reader:
                identifier = row.get('identificador')
                proposta = row.get('proposta')

                if not identifier or not proposta:
                    logging.warning(f"Skipping invalid row: {row}")
                    continue

                if identifier in processed_ids:
                    logging.debug(f"Skipping already processed ID: {identifier}")
                    continue

                # Prepare Query Parameters
                params = {
                    'proposta': proposta,
                    'situacao': '9',
                    'identificador': identifier,
                    'origin': 'sent_manually'
                }

                logging.info(f"Processing ID: {identifier}, Proposta: {proposta}...")
                
                try:
                    response = requests.get(API_URL, headers=headers, params=params, timeout=10, verify=False)
                    
                    log_msg = f"ID: {identifier} | Status: {response.status_code} | Response: {response.text}"
                    
                    if response.ok:
                        logging.info(f"SUCCESS - {log_msg}")
                        save_processed_id(identifier)
                        processed_ids.add(identifier)
                    else:
                        logging.error(f"FAILURE - {log_msg}")
                        # Depending on requirements, we might NOT want to save persistence on failure 
                        # so it can be retried. If 'situacao=9' implies a state change that should happen once, 
                        # determine if 4xx/5xx should block retry. Assuming retry is desired for failures.

                    time.sleep(0.5)

                except requests.RequestException as e:
                    logging.error(f"EXCEPTION processing ID {identifier}: {e}")

    except FileNotFoundError:
        logging.error(f"CSV file '{CSV_FILE}' not found.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    process_disbursements()
