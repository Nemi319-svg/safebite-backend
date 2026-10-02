import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

URL = "https://safebite-g3fc.onrender.com/health"

if __name__ == "__main__":
    logging.info(f"Starting SafeBite Keep-Alive Pinger for {URL}")
    while True:
        try:
            res = requests.get(URL, timeout=30)
            logging.info(f"Keep-Alive ping successful: HTTP {res.status_code}")
        except Exception as e:
            logging.warning(f"Keep-Alive ping attempt: {e}")
        time.sleep(600)  # Ping every 10 minutes to prevent Render from sleeping
