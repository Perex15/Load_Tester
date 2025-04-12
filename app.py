from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/run-test", methods=["POST"])
def run_test():
    data = request.get_json()
    target_url = data.get("targetUrl")
    num_users = data.get("numUsers")
    spawn_rate = data.get("spawnRate")
    run_time = data.get("runTime")

    if not all([target_url, num_users, spawn_rate, run_time]):
        return jsonify({"error": "All fields are required"}), 400

    if not target_url.startswith(("http://", "https://")):
        target_url = "http://" + target_url

    message = (
        f"To test {target_url}, run this command on a server with Locust installed:\n\n"
        f"locust -f locustfile.py --host={target_url} --users={num_users} "
        f"--spawn-rate={spawn_rate} --run-time={run_time}s --headless\n\n"
        f"Use this Locust script (locustfile.py):\n"
        f"from locust import HttpUser, task, between\n\n"
        f"class StressTestUser(HttpUser):\n"
        f"    wait_time = between(1, 5)\n"
        f"    @task\n"
        f"    def load_page(self):\n"
        f"        self.client.get('/')\n\n"
        f"Ensure you have permission to test the target server."
    )

    return jsonify({"message": message})

if __name__ == "__main__":
    app.run(debug=True)
