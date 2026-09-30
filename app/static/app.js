const tbody = document.querySelector("tbody");

const totalLogsEl =
    document.getElementById("totalLogs");

const errorLogsEl =
    document.getElementById("errorLogs");

const warningLogsEl =
    document.getElementById("warningLogs");

const servicesEl =
    document.getElementById("services");

const searchInput =
    document.getElementById("search");

const serviceFilter =
    document.getElementById("serviceFilter");

const levelFilter =
    document.getElementById("levelFilter");

const startTimeInput =
    document.getElementById("startTime");

const endTimeInput =
    document.getElementById("endTime");

const resultCount =
    document.getElementById("resultCount");

const pageInfo =
    document.getElementById("pageInfo");

const previousPage =
    document.getElementById("previousPage");

const nextPage =
    document.getElementById("nextPage");

const emptyState =
    document.getElementById("emptyState");

const liveUpdates =
    document.getElementById("liveUpdates");

const connectionDot =
    document.getElementById("connectionDot");

const connectionStatus =
    document.getElementById("connectionStatus");


let levelsChart = null;
let servicesChart = null;
let hourlyChart = null;

let currentPage = 1;
const pageSize = 50;
let totalLogs = 0;

let socket = null;


function escapeHtml(value) {

    const div = document.createElement("div");

    div.textContent =
        value === null || value === undefined
            ? ""
            : String(value);

    return div.innerHTML;
}


function addRow(log, prepend = true) {

    const row =
        document.createElement("tr");

    const level =
        String(log.level || "").toUpperCase();

    row.innerHTML = `
        <td>
            ${escapeHtml(
        new Date(log.timestamp)
            .toLocaleString()
    )}
        </td>

        <td>
            ${escapeHtml(log.service)}
        </td>

        <td class="${escapeHtml(level)}">
            ${escapeHtml(level)}
        </td>

        <td>
            ${escapeHtml(log.message)}
        </td>
    `;

    if (prepend) {
        tbody.prepend(row);
    } else {
        tbody.appendChild(row);
    }
}


function updateEmptyState() {

    const hasRows =
        tbody.children.length > 0;

    emptyState.style.display =
        hasRows ? "none" : "block";

    document.getElementById("logsTable")
        .style.display =
        hasRows ? "table" : "none";
}


function buildQueryString() {

    const params =
        new URLSearchParams();

    params.set("page", currentPage);
    params.set("limit", pageSize);
    params.set("sort", "desc");

    const search =
        searchInput.value.trim();

    if (search) {
        params.set("search", search);
    }

    if (serviceFilter.value) {
        params.set(
            "service",
            serviceFilter.value
        );
    }

    if (levelFilter.value) {
        params.set(
            "level",
            levelFilter.value
        );
    }

    if (startTimeInput.value) {

        params.set(
            "start_time",
            new Date(
                startTimeInput.value
            ).toISOString()
        );

    }

    if (endTimeInput.value) {

        params.set(
            "end_time",
            new Date(
                endTimeInput.value
            ).toISOString()
        );

    }

    return params.toString();
}


async function loadLogs() {

    try {

        const response =
            await fetch(
                `/logs?${buildQueryString()}`
            );

        if (!response.ok) {
            throw new Error(
                "Failed to load logs"
            );
        }

        const data =
            await response.json();

        totalLogs = data.total;

        tbody.innerHTML = "";

        data.logs
            .reverse()
            .forEach(
                log => addRow(log, false)
            );

        resultCount.innerText =
            `${data.total} log${data.total === 1 ? "" : "s"}`;

        pageInfo.innerText =
            `Page ${data.page}`;

        previousPage.disabled =
            currentPage <= 1;

        nextPage.disabled =
            currentPage * pageSize >= totalLogs;

        updateEmptyState();

    } catch (error) {

        console.error(
            "Could not load logs:",
            error
        );

    }

}


async function loadDashboardStats() {

    try {

        const response =
            await fetch(
                "/analytics/summary"
            );

        if (!response.ok) {
            return;
        }

        const stats =
            await response.json();

        totalLogsEl.innerText =
            stats.total_logs ?? 0;

        errorLogsEl.innerText =
            stats.errors ?? 0;

        warningLogsEl.innerText =
            stats.warnings ?? 0;

        servicesEl.innerText =
            stats.services ?? 0;

    } catch (error) {

        console.error(
            "Stats error:",
            error
        );

    }

}


async function loadLevelsChart() {

    try {

        const response =
            await fetch(
                "/analytics/levels"
            );

        const data =
            await response.json();

        populateLevelFilter(data);

        if (levelsChart) {
            levelsChart.destroy();
        }

        levelsChart =
            new Chart(
                document.getElementById(
                    "levelsChart"
                ),
                {
                    type: "doughnut",

                    data: {
                        labels:
                            Object.keys(data),

                        datasets: [
                            {
                                data:
                                    Object.values(
                                        data
                                    )
                            }
                        ]
                    },

                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                }
            );

    } catch (error) {

        console.error(
            "Level chart error:",
            error
        );

    }

}


async function loadServicesChart() {

    try {

        const response =
            await fetch(
                "/analytics/services"
            );

        const data =
            await response.json();

        populateServiceFilter(data);

        if (servicesChart) {
            servicesChart.destroy();
        }

        servicesChart =
            new Chart(
                document.getElementById(
                    "servicesChart"
                ),
                {
                    type: "bar",

                    data: {
                        labels:
                            Object.keys(data),

                        datasets: [
                            {
                                label:
                                    "Logs",

                                data:
                                    Object.values(
                                        data
                                    )
                            }
                        ]
                    },

                    options: {
                        responsive: true,
                        maintainAspectRatio: false,

                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                }
            );

    } catch (error) {

        console.error(
            "Service chart error:",
            error
        );

    }

}


async function loadHourlyChart() {

    try {

        const response =
            await fetch(
                "/analytics/logs/hourly"
            );

        const data =
            await response.json();

        if (hourlyChart) {
            hourlyChart.destroy();
        }

        hourlyChart =
            new Chart(
                document.getElementById(
                    "hourlyChart"
                ),
                {
                    type: "line",

                    data: {

                        labels:
                            data.map(
                                item =>
                                    new Date(
                                        item.hour
                                    ).toLocaleString()
                            ),

                        datasets: [
                            {
                                label:
                                    "Logs",

                                data:
                                    data.map(
                                        item =>
                                            item.count
                                    ),

                                tension: 0.3,

                                fill: true
                            }
                        ]
                    },

                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                }
            );

    } catch (error) {

        console.error(
            "Hourly chart error:",
            error
        );

    }

}


function populateLevelFilter(data) {

    const current =
        levelFilter.value;

    levelFilter.innerHTML =
        `<option value="">All Levels</option>`;

    Object.keys(data)
        .sort()
        .forEach(level => {

            const option =
                document.createElement(
                    "option"
                );

            option.value = level;
            option.textContent = level;

            levelFilter.appendChild(
                option
            );

        });

    if (
        Object.keys(data)
            .includes(current)
    ) {
        levelFilter.value = current;
    }

}


function populateServiceFilter(data) {

    const current =
        serviceFilter.value;

    serviceFilter.innerHTML =
        `<option value="">All Services</option>`;

    Object.keys(data)
        .sort()
        .forEach(service => {

            const option =
                document.createElement(
                    "option"
                );

            option.value = service;
            option.textContent = service;

            serviceFilter.appendChild(
                option
            );

        });

    if (
        Object.keys(data)
            .includes(current)
    ) {
        serviceFilter.value = current;
    }

}


function clearFilters() {

    searchInput.value = "";

    serviceFilter.value = "";

    levelFilter.value = "";

    startTimeInput.value = "";

    endTimeInput.value = "";

    currentPage = 1;

    loadLogs();

}


function exportLogs() {

    const params =
        new URLSearchParams();

    const search =
        searchInput.value.trim();

    if (search) {
        params.set(
            "search",
            search
        );
    }

    if (serviceFilter.value) {
        params.set(
            "service",
            serviceFilter.value
        );
    }

    if (levelFilter.value) {
        params.set(
            "level",
            levelFilter.value
        );
    }

    if (startTimeInput.value) {

        params.set(
            "start_time",
            new Date(
                startTimeInput.value
            ).toISOString()
        );

    }

    if (endTimeInput.value) {

        params.set(
            "end_time",
            new Date(
                endTimeInput.value
            ).toISOString()
        );

    }

    params.set("sort", "desc");

    window.location.href =
        `/logs/export?${params.toString()}`;
}


function connectWebSocket() {

    const protocol =
        window.location.protocol === "https:"
            ? "wss:"
            : "ws:";

    socket =
        new WebSocket(
            `${protocol}//${window.location.host}/ws/logs`
        );


    socket.onopen = () => {

        connectionStatus.innerText =
            "Connected";

        connectionDot.classList.add(
            "connected"
        );

    };


    socket.onmessage = event => {

        if (!liveUpdates.checked) {
            return;
        }

        const log =
            JSON.parse(event.data);

        addRow(log, true);

        updateEmptyState();

        if (currentPage === 1) {
            loadDashboardStats();
        }

    };


    socket.onclose = () => {

        connectionStatus.innerText =
            "Disconnected";

        connectionDot.classList.remove(
            "connected"
        );

        setTimeout(
            connectWebSocket,
            3000
        );

    };


    socket.onerror = error => {

        console.error(
            "WebSocket error:",
            error
        );

    };

}


document
    .getElementById("applyFilters")
    .addEventListener(
        "click",
        () => {

            currentPage = 1;

            loadLogs();

        }
    );


document
    .getElementById("clearFilters")
    .addEventListener(
        "click",
        clearFilters
    );


document
    .getElementById("exportLogs")
    .addEventListener(
        "click",
        exportLogs
    );


previousPage.addEventListener(
    "click",
    () => {

        if (currentPage > 1) {

            currentPage--;

            loadLogs();

        }

    }
);


nextPage.addEventListener(
    "click",
    () => {

        if (
            currentPage * pageSize <
            totalLogs
        ) {

            currentPage++;

            loadLogs();

        }

    }
);


searchInput.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {

            currentPage = 1;

            loadLogs();

        }

    }
);


async function refreshDashboard() {

    await loadDashboardStats();

    await loadLevelsChart();

    await loadServicesChart();

    await loadHourlyChart();

}


loadLogs();

refreshDashboard();

connectWebSocket();


// Refresh analytics periodically rather than
// rebuilding charts for every individual log.

setInterval(
    () => {

        if (liveUpdates.checked) {
            refreshDashboard();
        }

    },
    10000
);