import os
import time
import requests
from prometheus_client import start_http_server, Gauge

# Constants
USERNAME = os.getenv('DOCKERHUB_USERNAME')
PASSWORD = os.getenv('DOCKERHUB_PASSWORD')
TOKEN_URL = "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull"
MANIFEST_URL = "https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest"
PROMETHEUS_PORT = 9000

# Create Prometheus metrics
rate_limit_limit = Gauge('docker_ratelimit_limit', 'Rate limit limit')
rate_limit_remaining = Gauge('docker_ratelimit_remaining', 'Rate limit remaining')

def get_token():
    """Fetch the authentication token from Docker registry."""
    response = requests.get(TOKEN_URL, auth=(USERNAME, PASSWORD))
    response.raise_for_status()  # Raise an error for bad responses
    return response.json().get('token')

def query_rate_limit():
    """Query the Docker registry and extract rate limit headers."""
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.head(MANIFEST_URL, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    
    # Extract rate limit headers
    limit = response.headers.get('ratelimit-limit')
    remaining = response.headers.get('ratelimit-remaining')

    # Parse the limit and remaining values
    if limit:
        limit_value = int(limit.split(';')[0])  # Take the first part before ';'
        rate_limit_limit.set(limit_value)
    
    if remaining:
        remaining_value = int(remaining.split(';')[0])  # Take the first part before ';'
        rate_limit_remaining.set(remaining_value)
        print(f"remaining {remaining_value}")

def main():
    """Main function to start the server and query the rate limit."""
    start_http_server(PROMETHEUS_PORT)  # Start Prometheus metrics server
    print(f"Serving metrics on port {PROMETHEUS_PORT}")

    while True:
        query_rate_limit()  # Query the rate limit
        time.sleep(60)  # Wait for 1 minute

if __name__ == "__main__":
    main()

