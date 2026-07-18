const tbody = document.querySelector("tbody");

const totalLogsEl = document.getElementById("totalLogs");
const errorLogsEl = document.getElementById("errorLogs");
const warningLogsEl = document.getElementById("warningLogs");
const servicesEl = document.getElementById("services");
let levelsChart;
let servicesChart;
let hourlyChart;


function addRow(log) {
    const row = document.createElement("tr");

    row.innerHTML = `
        <td>${new Date(log.timestamp).toLocaleString()}</td>
        <td>${log.service}</td>
        <td class="${log.level}">
            ${log.level}
        </td>
        <td>${log.message}</td>
    `;

    tbody.prepend(row);

    while (tbody.children.length > 100) {
        tbody.removeChild(tbody.lastChild);
    }
}

async function loadLogs() {
    const response = await fetch("/logs?limit=50&sort=desc");
    const data = await response.json();

    tbody.innerHTML = "";

    data.logs.reverse().forEach(addRow);
}

async function loadDashboardStats() {

    const response = await fetch("/analytics/summary");

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
            type: "pie",

            data: {
                labels: Object.keys(data),

                datasets: [
                    {
                        data: Object.values(data)
                    }
                ]
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

                        data: Object.values(data)
                    }
                ]
            },

            options: {
                responsive: true
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

                        fill: false,

                        tension: .3
                    }
                ]
            },

            options: {
                responsive: true
            }
        }
    );
}

loadLogs();
loadDashboardStats();
loadLevelsChart();
loadServicesChart();
loadHourlyChart();

const socket = new WebSocket("ws://localhost:8000/ws/logs");

socket.onmessage = (event) => {
    const log = JSON.parse(event.data);

    addRow(log);

    loadDashboardStats();
    loadLevelsChart();
    loadServicesChart();
    loadHourlyChart();
};