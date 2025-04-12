from flask import Flask, request, render_template
from locust import HttpUser, task, between, Locust
import os

app = Flask(__name__)

# Locust script to simulate traffic
class StressTestUser(HttpUser):
    wait_time = between(1, 5)  # Simulate realistic user delays
    @task
    def load_page(self):
        self.client.get("/")  # Adjust endpoint based on your server

# Save Locust config dynamically
def generate_locust_file(target_url):
    with open("locustfile.py", "w") as f:
        f.write(f"""
from locust import HttpUser, task, between

class StressTestUser(HttpUser):
    wait_time = between(1, 5)
    host = "{target_url}"
    @task
    def load_page(self):
        self.client.get("/")
""")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        target_url = request.form.get("target_url")
        num_users = int(request.form.get("num_users", 10))
        spawn_rate = int(request.form.get("spawn_rate", 1))
        run_time = int(request.form.get("run_time", 60))

        if not target_url.startswith("http"):
            target_url = "http://" + target_url

        # Generate Locust script
        generate_locust_file(target_url)

        # Run Locust in headless mode
        os.system(f"locust -f locustfile.py --headless -u {num_users} -r {spawn_rate} --run-time {run_time}s --host {target_url}")

        return "Test completed! Check server logs for results."
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
