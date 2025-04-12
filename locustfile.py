from locust import HttpUser, task, between, events
import requests

WEBHOOK_URL = "your_discord_webhook_url"  # Replace with your actual webhook URL

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    requests.post(WEBHOOK_URL, json={"content": "Locust test started"})

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    requests.post(WEBHOOK_URL, json={"content": "Locust test stopped"})

@events.request_failure.add_listener
def on_request_failure(request_type, name, response_time, response_length, exception, **kwargs):
    message = f"Request failed: {name} - {str(exception)}"
    requests.post(WEBHOOK_URL, json={"content": message})

class StressTestUser(HttpUser):
    wait_time = between(1, 5)
    @task
    def load_page(self):
        self.client.get("/")
