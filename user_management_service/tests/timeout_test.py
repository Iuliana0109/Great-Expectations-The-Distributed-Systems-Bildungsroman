import requests
from requests.exceptions import Timeout
TIMEOUT_DURATION = 1

# URL of the status endpoint
URL = "http://localhost:5000/status"

def test_status_endpoint():
    try:
        response = requests.get(URL, timeout=TIMEOUT_DURATION)
        print(f"Request succeeded: Status Code: {response.status_code}, Response: {response.json()}")
    except Timeout:
        print("Request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_status_endpoint()
