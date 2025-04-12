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
            // Display instructions
            resultDiv.textContent = data.message;
            resultDiv.classList.remove("hidden");

            // Create a download link
            const downloadLink = document.createElement("a");
            downloadLink.textContent = "Download locustfile.py";
            downloadLink.href = "#";
            downloadLink.style.color = "#3498db";
            downloadLink.style.textDecoration = "underline";
            downloadLink.addEventListener("click", async (e) => {
                e.preventDefault();
                const downloadResponse = await fetch("/download-locustfile", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ script: data.download }),
                });
                const blob = await downloadResponse.blob();
                const url = window.URL.createObjectURL(blob);
                const tempLink = document.createElement("a");
                tempLink.href = url;
                tempLink.download = "locustfile.py";
                tempLink.click();
                window.URL.revokeObjectURL(url);
            });

            resultDiv.appendChild(document.createElement("br"));
            resultDiv.appendChild(downloadLink);
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
