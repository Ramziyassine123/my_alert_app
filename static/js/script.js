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
function createAlert(title, message, period) {
    showLoadingSpinner(); // Show spinner when starting the request
    return fetch('/alerts/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ title, message, period })
    }).then(response => {
        hideLoadingSpinner(); // Hide spinner when request completes
        return response.json();
    });
}
// Function to fetch and display alerts
function fetchAlerts() {
    showLoadingSpinner(); // Show spinner when starting the request
    fetch('/alerts/')
        .then(response => response.json())
        .then(data => {
            hideLoadingSpinner(); // Hide spinner when request completes
            console.log(data);  // Log the entire response
            const alertsList = document.getElementById('alerts-list');
            alertsList.innerHTML = '';  // Clear existing alerts
            if (data.alerts) {  // Check if alerts are present in the response
                data.alerts.forEach(function(alert) {
                    alertsList.innerHTML += `
                        <div>
                            <h3>${alert.title}</h3>
                            <p>${alert.message}</p>
                            <p>Period: ${alert.period} seconds</p>
                            <button onclick="deleteAlert(${alert.id})">Delete Alert</button>
                        </div>
                    `;
                });
            } else {
                console.error("No alerts found in the response.");
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

// Firebase Messaging Setup
// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.7.1/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.7.1/firebase-analytics.js";
import { getMessaging, requestPermission, getToken } from "https://www.gstatic.com/firebasejs/11.7.1/firebase-messaging.js";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyDGcByybA0Oio1J-TfA2WY7RYSv7Iwqk9Y",
    authDomain: "fir-101-44510.firebaseapp.com",
    projectId: "fir-101-44510",
    storageBucket: "fir-101-44510.appspot.com",
    messagingSenderId: "83600789430",
    appId: "1:83600789430:web:b4cd7cb4d9f3f463eafb17",
    measurementId: "G-W7LBFCD3MJ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const messaging = getMessaging(app); // Initialize messaging

// Request permission and get the token for notifications
document.getElementById('create-alert').addEventListener('click', () => {
    const title = document.getElementById('title').value;
    const message = document.getElementById('message').value;
    const period = document.getElementById('period').value;

    createAlert(title, message, period).then(data => {
        console.log("Alert created:", data);
        fetchAlerts();  // Refresh the alert list after creating a new alert
        document.getElementById('alert-form').reset();  // Reset the form fields
    }).catch(error => {
        console.error("Error creating alert:", error);
    });

    // Request notification permission
    requestPermission()
        .then(() => {
            console.log("Notification permission granted.");
            return getToken(messaging);
        })
        .then((token) => {
            console.log("Device token:", token);
            document.getElementById('alert-status').innerText = "Device token: " + token; // Display the token on the page
            // Send this token to your server for further use
        })
        .catch((err) => {
            console.error("Unable to get permission to notify.", err);
            document.getElementById('alert-status').innerText = "Permission denied: " + err.message; // Display error message
        });
});

// Initial fetch of alerts when the page loads
document.addEventListener('DOMContentLoaded', function() {
    fetchAlerts();
});


// Function to establish a WebSocket connection
function connectWebSocket() {
    const socket = new WebSocket('ws://localhost:8000/ws/alerts/'); // Update with your server address

    socket.onopen = function(e) {
        console.log("WebSocket connection established.");
    };

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log("New alert received:", data);
        // Here you can update the UI with the new alert
        const alertsList = document.getElementById('alerts-list');
        alertsList.innerHTML += `
            <div>
                <h3>${data.title}</h3>
                <p>${data.message}</p>
                <p>Period: ${data.period} seconds</p>
                <button onclick="deleteAlert(${data.id})">Delete Alert</button>
            </div>
        `;
    };

    socket.onclose = function(e) {
        console.error("WebSocket connection closed:", e);
    };
}

// Call the WebSocket connection function when the page loads
document.addEventListener('DOMContentLoaded', function() {
    fetchAlerts(); // Fetch existing alerts
    connectWebSocket(); // Establish WebSocket connection
});