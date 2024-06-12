import requests
import schedule
import time
from bs4 import BeautifulSoup

def check_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Extract the page title
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'No Title'
            return url, title, True
        else:
            return url, None, False
    except requests.RequestException:
        return url, None, False

def update_url_list_sequential(url_list):
    valid_urls = []
    invalid_urls = []

    for url in url_list:
        url, title, is_valid = check_url(url)
        if is_valid:
            valid_urls.append((url, title))
        else:
            invalid_urls.append(url)
        
        # Print each URL and its status
        print(f"Checked URL: {url}, Valid: {is_valid}")

        # Delay between requests to avoid overwhelming the server
        time.sleep(1)

    return valid_urls, invalid_urls

def extend_url_list(base_url, start, end):
    new_urls = []
    for i in range(start, end):
        new_urls.append(f"{base_url}/{i}")
    return new_urls

def read_ids(filename):
    try:
        with open(filename, 'r') as f:
            return list(map(int, f.read().splitlines()))
    except FileNotFoundError:
        return []

def save_ids(filename, ids):
    with open(filename, 'w') as f:
        for id in ids:
            f.write(f"{id}\n")

def read_valid_urls(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def save_valid_urls(filename, valid_urls):
    with open(filename, 'w') as f:
        for url, title in valid_urls:
            f.write(f"{title}: {url}\n")

def main():
    base_url = "http://127.0.0.1:5000"  # Use the local mock server
    active_ids = read_ids('active_ids.txt')
    current_valid_urls = read_valid_urls('valid_urls.txt')

    current_urls = [f"{base_url}/{id}" for id in active_ids]

    print(f"Checking {len(current_urls)} URLs from the active list...")

    valid_urls, invalid_urls = update_url_list_sequential(current_urls)

    valid_ids = [int(url.split('/')[-1]) for url, _ in valid_urls]
    invalid_ids = [int(url.split('/')[-1]) for url in invalid_urls]

    print(f"Found {len(valid_ids)} valid URLs and {len(invalid_ids)} invalid URLs from the active list.")

    # Save the updated list of valid IDs back to the file
    save_ids('active_ids.txt', valid_ids)

    # Save the updated list of valid URLs back to the file
    save_valid_urls('valid_urls.txt', valid_urls)

    # Extend the search to new IDs beyond the highest ID in the active list
    highest_id = max(active_ids) if active_ids else 0
    
    # Set the number of new IDs to check
    num_new_ids = 100  # Change this value to set how many extra URLs to check
    
    new_urls = extend_url_list(base_url, highest_id + 1, highest_id + 1 + num_new_ids)

    print(f"Checking {len(new_urls)} new URLs...")

    new_valid_urls, new_invalid_urls = update_url_list_sequential(new_urls)

    new_valid_ids = [int(url.split('/')[-1]) for url, _ in new_valid_urls]

    print(f"Found {len(new_valid_ids)} new valid URLs.")

    # Append new valid IDs to the active list
    valid_ids.extend(new_valid_ids)

    # Append new valid URLs to the valid URLs list
    valid_urls.extend(new_valid_urls)

    # Save the final list of valid IDs back to the file
    save_ids('active_ids.txt', valid_ids)

    # Save the final list of valid URLs back to the file
    save_valid_urls('valid_urls.txt', valid_urls)

    print("Final active IDs and valid URLs lists updated.")

# Schedule the script to run daily
schedule.every().day.at("00:00").do(main)

# Run the main function immediately for testing
main()

while True:
    schedule.run_pending()
    time.sleep(1)
