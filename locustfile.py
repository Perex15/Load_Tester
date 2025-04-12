
from locust import HttpUser, task, between, events
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1360559695001292922/gi0RKvRxSvLv7O6fMbu5iWoLwIML6Gj06VZ4EcIQlygt09-TTJw6h6qTgw7HJZaUd6eC"

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    embed = {
        "title": "ðŸŸ¢ Locust Test Started",
        "description": "A new load test has begun.",
        "color": 0x00FF00,
        "fields": [
            {"name": "Target URL", "value": "http://example.com", "inline": true},
            {"name": "Users", "value": "10", "inline": true},
            {"name": "Spawn Rate", "value": "1", "inline": true},
            {"name": "Duration", "value": "60s", "inline": true}
        ],
        "footer": {"text": "Ethical Server Load Tester"}
    }
    requests.post(WEBHOOK_URL, json={"embeds": [embed]})

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.stats.total
    embed = {
        "title": "ðŸ”´ Locust Test Stopped",
        "description": "The load test has completed.",
        "color": 0xFF0000,
        "fields": [
            {"name": "Total Requests", "value": str(stats.num_requests), "inline": true},
            {"name": "Failures", "value": str(stats.num_failures), "inline": true},
            {"name": "Avg Response Time", "value": f"{stats.avg_response_time:.2f}ms", "inline": true}
        ],
        "footer": {"text": "Ethical Server Load Tester"}
    }
    requests.post(WEBHOOK_URL, json={"embeds": [embed]})

@events.request_failure.add_listener
def on_request_failure(request_type, name, response_time, response_length, exception, **kwargs):
    embed = {
        "title": "âš ï¸ Request Failure",
        "description": "A request failed during the test.",
        "color": 0xFFA500,
        "fields": [
            {"name": "Request", "value": name, "inline": true},
            {"name": "Type", "value": request_type, "inline": true},
            {"name": "Response Time", "value": f"{response_time}ms", "inline": true},
            {"name": "Error", "value": str(exception), "inline": true}
        ],
        "footer": {"text": "Ethical Server Load Tester"}
    }
    requests.post(WEBHOOK_URL, json={"embeds": [embed]})

class StressTestUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://example.com"
    @task
    def load_page(self):
        self.client.get("/")
