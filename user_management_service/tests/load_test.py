import requests
import concurrent.futures
import time

URL = "http://localhost:5000/status"
NUM_REQUESTS = 1000  # Number of requests to send (total)
MAX_WORKERS = 50

# Function to send a single request
def send_request(index):
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            print(f"Request {index}: Success")
        else:
            print(f"Request {index}: Failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request {index}: Error - {e}")

def main():
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(send_request, i) for i in range(NUM_REQUESTS)]
        concurrent.futures.wait(futures)
    end_time = time.time()
    print(f"Completed {NUM_REQUESTS} requests in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
