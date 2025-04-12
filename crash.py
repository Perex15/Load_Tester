from locust import HttpUser, task, between

class StressTestUser(HttpUser):
    wait_time = between(1, 5)
    @task
    def load_page(self):
        self.client.get('/')
