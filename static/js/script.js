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

// Function to create an alert
function createAlert(form) {
    showLoadingSpinner(); // Show spinner when starting the request
    const formData = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    }).then(response => {
        hideLoadingSpinner(); // Hide spinner when request completes
        return response.json();
    }).then(data => {
        if (data.alert_id) {
            document.getElementById('alert-status').innerText = 'Alert created successfully! ID: ' + data.alert_id;
            form.reset(); // Reset the form
            fetchAlerts(); // Refresh the alert list
        }
    }).catch(error => {
        hideLoadingSpinner(); // Hide spinner in case of error
        console.error("Error creating alert:", error);
    });
}

// Function to fetch and display alerts
function fetchAlerts() {
    showLoadingSpinner(); // Show spinner when starting the request
    fetch('/alerts_websocket/')
        .then(response => response.json())
        .then(data => {
            hideLoadingSpinner(); // Hide spinner when request completes
            const alertsList = document.getElementById('alerts-list');
            alertsList.innerHTML = '';  // Clear existing alerts
            if (data.alerts) {
                data.alerts.forEach(function(alert) {
                    alertsList.innerHTML += `
                        <div>
                            <strong>${alert.title}</strong>: ${alert.message} (Period: ${alert.period} seconds)
                            <button onclick="deleteAlert(${alert.id})">Delete Alert</button>
                        </div>
                    `;
                });
            }
        })
        .catch(error => {
            hideLoadingSpinner(); // Hide spinner in case of error
            console.error("Failed to fetch alerts:", error);
        });
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
    const socket = new WebSocket('ws://' + window.location.host + '/alerts_websocket/');

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

// Initial fetch of alerts when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const alertForm = document.getElementById('alert-form');
    if (alertForm) {
        alertForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission
            createAlert(alertForm); // Call createAlert function
        });
    }
    fetchAlerts(); // Fetch existing alerts
    connectWebSocket(); // Establish WebSocket connection
});
