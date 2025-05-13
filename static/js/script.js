
// Initial fetch of alerts when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const alertForm = document.getElementById('alert-form');
    if (alertForm) {
        alertForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission
        });
    }
    connectWebSocket(); // Establish WebSocket connection
});

// Function to show the loading spinner
function showLoadingSpinner() {
    document.getElementById('loading-spinner').style.display = 'block';
}

// Function to hide the loading spinner
function hideLoadingSpinner() {
    document.getElementById('loading-spinner').style.display = 'none';
}

// Function to get CSRF token for AJAX requests
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}



// Function to delete an alert
function deleteAlert(alertId) {
    showLoadingSpinner(); // Show spinner when starting the request
    fetch(`/alerts/delete/${alertId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (response.ok) {
            fetchAlerts();  // Refresh the alert list after deleting an alert
        } else {
            console.error("Failed to delete alert:", response.statusText);
        }
    })
    .catch(error => {
        hideLoadingSpinner(); // Hide spinner in case of error
        console.error("Error deleting alert:", error);
    });
}

// Function to establish a WebSocket connection
function connectWebSocket() {
    const socket = new WebSocket('ws://localhost:6789');

    socket.onopen = function(e) {
        console.log("WebSocket connection established.");
    };

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const alertsList = document.getElementById('alerts-list');
        alertsList.innerHTML += `
            <div>
                <strong>${data.title}</strong>: ${data.message} (Period: ${data.period} seconds)
                <button onclick="deleteAlert(${data.id})">Delete Alert</button>
            </div>
        `;
    };

    socket.onclose = function(e) {
        console.error("WebSocket connection closed:", e);
    };
}


