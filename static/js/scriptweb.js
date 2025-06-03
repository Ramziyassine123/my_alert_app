// Function to establish a WebSocket connection
function connectWebSocket() {
    const socket = new WebSocket('ws://localhost:6789');

    socket.onopen = function(e) {
        console.log("WebSocket connection established.");
    };

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const alertsList = document.getElementById('alerts-list');
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert';
        alertDiv.innerHTML =`<strong>${data.title}</strong><p>${data.message}</p>`;
        alertsList.appendChild(alertDiv);
    };

    socket.onclose = function(e) {
        console.error("WebSocket connection closed:", e);
    };

    socket.onerror = function(error) {
        console.error("WebSocket error:", error);
    };
}

// Establish WebSocket connection when the page loads
document.addEventListener('DOMContentLoaded', function() {
    connectWebSocket();
});

// Function to show the loading spinner
function showLoadingSpinner() {
    document.getElementById('loading-spinner').style.display = 'block';
}

// Function to hide the loading spinner
function hideLoadingSpinner() {
    document.getElementById('loading-spinner').style.display = 'none';
}
