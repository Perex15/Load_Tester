document.getElementById("testForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const runButton = document.getElementById("runButton");
    const resultDiv = document.getElementById("result");
    const errorDiv = document.getElementById("error");

    runButton.disabled = true;
    resultDiv.classList.add("hidden");
    errorDiv.classList.add("hidden");
    resultDiv.textContent = "";
    errorDiv.textContent = "";

    const targetUrl = document.getElementById("targetUrl").value;
    const numUsers = document.getElementById("numUsers").value;
    const spawnRate = document.getElementById("spawnRate").value;
    const runTime = document.getElementById("runTime").value;

    try {
        const response = await fetch("/api/run-test", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ targetUrl, numUsers, spawnRate, runTime }),
        });

        const data = await response.json();

        if (response.ok) {
            resultDiv.textContent = data.message;
            resultDiv.classList.remove("hidden");
        } else {
            errorDiv.textContent = data.error;
            errorDiv.classList.remove("hidden");
        }
    } catch (err) {
        errorDiv.textContent = "Failed to connect to the server.";
        errorDiv.classList.remove("hidden");
    } finally {
        runButton.disabled = false;
    }
});
