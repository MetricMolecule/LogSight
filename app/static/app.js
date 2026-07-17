const tbody = document.querySelector("tbody");

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

    data.logs
        .slice()
        .reverse()
        .forEach(addRow);
}

loadLogs();

const socket = new WebSocket("ws://localhost:8000/ws/logs");

socket.onmessage = (event) => {
    const log = JSON.parse(event.data);
    addRow(log);
};

socket.onopen = () => {
    console.log("Connected to websocket");
};

socket.onclose = () => {
    console.log("Websocket disconnected");
};

socket.onerror = (err) => {
    console.error(err);
};