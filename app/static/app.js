const tbody = document.querySelector("tbody");

const totalLogsEl = document.getElementById("totalLogs");
const errorLogsEl = document.getElementById("errorLogs");
const warningLogsEl = document.getElementById("warningLogs");
const servicesEl = document.getElementById("services");

const connectionStatusEl = document.getElementById("connectionStatus");
const logForm = document.getElementById("logForm");
const sendResultEl = document.getElementById("sendResult");

let levelsChart;
let servicesChart;
let hourlyChart;
let socket;

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

function addRow(log) {
    const row = document.createElement("tr");

    row.innerHTML = `
        <td>${new Date(log.timestamp).toLocaleString()}</td>
        <td class="service-cell">${escapeHtml(log.service)}</td>
        <td><span class="level-badge ${escapeHtml(log.level)}">${escapeHtml(log.level)}</span></td>
        <td class="message-cell">${escapeHtml(log.message)}</td>
        <td class="request-cell">${escapeHtml(log.request_id)}</td>
    `;

    tbody.prepend(row);

    while (tbody.children.length > 100) {
        tbody.removeChild(tbody.lastChild);
    }
}

async function loadLogs() {
    const response = await fetch("/logs?limit=50&sort=desc");

    if (!response.ok) {
        throw new Error("Unable to load logs");
    }

    const data = await response.json();

    tbody.innerHTML = "";

    data.logs.reverse().forEach(addRow);
}

async function loadDashboardStats() {
    const response = await fetch("/analytics/summary");

    if (!response.ok) {
        throw new Error("Unable to load summary");
    }

    const stats = await response.json();

    totalLogsEl.innerText = stats.total_logs;
    errorLogsEl.innerText = stats.errors;
    warningLogsEl.innerText = stats.warnings;
    servicesEl.innerText = stats.services;
}

async function loadLevelsChart() {
    const response = await fetch("/analytics/levels");
    const data = await response.json();

    if (levelsChart) {
        levelsChart.destroy();
    }

    levelsChart = new Chart(
        document.getElementById("levelsChart"),
        {
            type: "doughnut",
            data: {
                labels: Object.keys(data),
                datasets: [
                    {
                        data: Object.values(data)
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        }
    );
}

async function loadServicesChart() {
    const response = await fetch("/analytics/services");
    const data = await response.json();

    if (servicesChart) {
        servicesChart.destroy();
    }

    servicesChart = new Chart(
        document.getElementById("servicesChart"),
        {
            type: "bar",
            data: {
                labels: Object.keys(data),
                datasets: [
                    {
                        label: "Logs",
                        data: Object.values(data),
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    );
}

async function loadHourlyChart() {
    const response = await fetch("/analytics/logs/hourly");
    const data = await response.json();

    if (hourlyChart) {
        hourlyChart.destroy();
    }

    hourlyChart = new Chart(
        document.getElementById("hourlyChart"),
        {
            type: "line",
            data: {
                labels: data.map(x => new Date(x.hour).toLocaleString()),
                datasets: [
                    {
                        label: "Logs",
                        data: data.map(x => x.count),
                        fill: true,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    );
}

async function refreshDashboard() {
    await Promise.all([
        loadDashboardStats(),
        loadLevelsChart(),
        loadServicesChart(),
        loadHourlyChart()
    ]);
}

function setConnectionStatus(state, label) {
    connectionStatusEl.className = `status-pill ${state}`;
    connectionStatusEl.innerHTML = `
        <span class="status-dot"></span>
        ${label}
    `;
}

function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";

    socket = new WebSocket(
        `${protocol}//${window.location.host}/ws/logs`
    );

    socket.onopen = () => {
        setConnectionStatus("connected", "Live");
    };

    socket.onmessage = (event) => {
        const log = JSON.parse(event.data);

        addRow(log);
        refreshDashboard();
    };

    socket.onerror = () => {
        setConnectionStatus("disconnected", "Connection error");
    };

    socket.onclose = () => {
        setConnectionStatus("connecting", "Reconnecting");

        setTimeout(connectWebSocket, 3000);
    };
}

logForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    sendResultEl.textContent = "Sending…";
    sendResultEl.className = "form-result";

    const payload = {
        timestamp: new Date().toISOString(),
        service: document.getElementById("serviceInput").value,
        level: document.getElementById("levelInput").value,
        message: document.getElementById("messageInput").value,
        request_id: document.getElementById("requestInput").value,
        user_id: document.getElementById("userInput").value,
        metadata: {
            source: "dashboard",
            browser: "web-ui"
        }
    };

    try {
        const response = await fetch("/logs", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        sendResultEl.textContent =
            "Accepted by API — waiting for worker processing…";
        sendResultEl.className = "form-result success";
    } catch (error) {
        sendResultEl.textContent = "Failed to send log.";
        sendResultEl.className = "form-result error";
        console.error(error);
    }
});

async function initialize() {
    try {
        await loadLogs();
        await refreshDashboard();
        connectWebSocket();
    } catch (error) {
        console.error(error);
        setConnectionStatus("disconnected", "API unavailable");
    }
}

initialize();
