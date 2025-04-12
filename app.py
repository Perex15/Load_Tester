import os
from flask import Flask, request, jsonify, render_template, send_file
import requests
import io
import base64

app = Flask(__name__)

# Ensure Flask can find templates and static files
app.template_folder = "templates"
app.static_folder = "static"

# Replace with your actual Discord webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1360559695001292922/gi0RKvRxSvLv7O6fMbu5iWoLwIML6Gj06VZ4EcIQlygt09-TTJw6h6qTgw7HJZaUd6eC"

def send_to_discord(embed):
    """Send an embed message to Discord."""
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]})
    except requests.RequestException as e:
        print(f"Failed to send to Discord: {e}")

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        return jsonify({"error": f"Failed to load index.html: {str(e)}"}), 500

@app.route("/api/run-test", methods=["POST"])
def run_test():
    try:
        data = request.get_json()
        target_url = data.get("targetUrl")
        num_users = data.get("numUsers")
        spawn_rate = data.get("spawnRate")
        run_time = data.get("runTime")

        if not all([target_url, num_users, spawn_rate, run_time]):
            return jsonify({"error": "All fields are required"}), 400

        if not target_url.startswith(("http://", "https://")):
            target_url = "http://" + target_url

        # Generate the Locust script with Discord integration
        locust_script = f"""
from locust import HttpUser, task, between, events
import requests

WEBHOOK_URL = "{WEBHOOK_URL}"

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    embed = {{
        "title": "🟢 Locust Test Started",
        "description": "A new load test has begun.",
        "color": 0x00FF00,
        "fields": [
            {{"name": "Target URL", "value": "{target_url}", "inline": true}},
            {{"name": "Users", "value": "{num_users}", "inline": true}},
            {{"name": "Spawn Rate", "value": "{spawn_rate}", "inline": true}},
            {{"name": "Duration", "value": "{run_time}s", "inline": true}}
        ],
        "footer": {{"text": "Ethical Server Load Tester"}}
    }}
    requests.post(WEBHOOK_URL, json={{"embeds": [embed]}})

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.stats.total
    embed = {{
        "title": "🔴 Locust Test Stopped",
        "description": "The load test has completed.",
        "color": 0xFF0000,
        "fields": [
            {{"name": "Total Requests", "value": str(stats.num_requests), "inline": true}},
            {{"name": "Failures", "value": str(stats.num_failures), "inline": true}},
            {{"name": "Avg Response Time", "value": f"{{stats.avg_response_time:.2f}}ms", "inline": true}}
        ],
        "footer": {{"text": "Ethical Server Load Tester"}}
    }}
    requests.post(WEBHOOK_URL, json={{"embeds": [embed]}})

@events.request_failure.add_listener
def on_request_failure(request_type, name, response_time, response_length, exception, **kwargs):
    embed = {{
        "title": "⚠️ Request Failure",
        "description": "A request failed during the test.",
        "color": 0xFFA500,
        "fields": [
            {{"name": "Request", "value": name, "inline": true}},
            {{"name": "Type", "value": request_type, "inline": true}},
            {{"name": "Response Time", "value": f"{{response_time}}ms", "inline": true}},
            {{"name": "Error", "value": str(exception), "inline": true}}
        ],
        "footer": {{"text": "Ethical Server Load Tester"}}
    }}
    requests.post(WEBHOOK_URL, json={{"embeds": [embed]}})

class StressTestUser(HttpUser):
    wait_time = between(1, 5)
    host = "{target_url}"
    @task
    def load_page(self):
        self.client.get("/")
"""

        # Encode the script as base64 for download
        script_bytes = locust_script.encode("utf-8")
        script_base64 = base64.b64encode(script_bytes).decode("utf-8")

        # Terminal instructions
        terminal_instructions = (
            f"1. Save the downloaded `locustfile.py`.\n"
            f"2. Install Locust and requests:\n"
            f"   pip install locust requests\n"
            f"3. Run the test in your terminal:\n"
            f"   locust -f locustfile.py --host={target_url} --users={num_users} "
            f"--spawn-rate={spawn_rate} --run-time={run_time}s --headless"
        )

        # Send to Discord
        embed = {
            "title": "📋 New Test Request",
            "description": "A user has requested a load test.",
            "color": 0x1E90FF,
            "fields": [
                {"name": "Target URL", "value": target_url, "inline": True},
                {"name": "Users", "value": str(num_users), "inline": True},
                {"name": "Spawn Rate", "value": str(spawn_rate), "inline": True},
                {"name": "Duration", "value": f"{run_time}s", "inline": True},
                {"name": "Terminal Command", "value": f"`locust -f locustfile.py --host={target_url} --users={num_users} --spawn-rate={spawn_rate} --run-time={run_time}s --headless`", "inline": False}
            ],
            "footer": {"text": "Ethical Server Load Tester"}
        }
        send_to_discord(embed)

        # Response to the user
        return jsonify({
            "message": terminal_instructions,
            "download": script_base64
        })
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/download-locustfile", methods=["POST"])
def download_locustfile():
    try:
        data = request.get_json()
        script_base64 = data.get("script")
        script_bytes = base64.b64decode(script_base64)
        return send_file(
            io.BytesIO(script_bytes),
            as_attachment=True,
            download_name="locustfile.py",
            mimetype="text/plain"
        )
    except Exception as e:
        return jsonify({"error": f"Download error: {str(e)}"}), 500

# Vercel requires this to work with WSGI
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
