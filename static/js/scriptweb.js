
let socket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectInterval = 3000; // 3 seconds
let alertsStarted = false; // Flag to prevent duplicate alert requests
let receivedAlertIds = new Set(); // Track received alert IDs to prevent duplicates

// Use unified server WebSocket URL
const WEBSOCKET_URL = 'ws://127.0.0.1:8001/ws/alerts/';

// Function to establish a WebSocket connection
function connectWebSocket() {
    try {
        console.log(`Connecting to WebSocket: ${WEBSOCKET_URL}`);
        socket = new WebSocket(WEBSOCKET_URL);

        socket.onopen = function(e) {
            console.log("WebSocket connection established");
            reconnectAttempts = 0;
            showConnectionStatus('connected', 'Connected to Alert Server');
            hideLoadingSpinner();

            // Start alerts only once per connection
            if (!alertsStarted) {
                alertsStarted = true;
                console.log('Requesting alerts from server...');
                socket.send(JSON.stringify({
                    type: 'start_alerts',
                    message: 'Client ready to receive alerts'
                }));
            }
        };

        socket.onmessage = function(e) {
            try {
                const data = JSON.parse(e.data);
                console.log('Received WebSocket message:', data);

                if (data.type === 'alert') {
                    // Check for duplicate alerts using unique ID
                    const alertId = data.alert_id || `${data.title}_${data.sequence}`;

                    if (!receivedAlertIds.has(alertId)) {
                        receivedAlertIds.add(alertId);
                        displayAlert(data);
                    } else {
                        console.log('Duplicate alert ignored:', alertId);
                    }
                } else if (data.type === 'error') {
                    showErrorMessage(data.message);
                } else if (data.type === 'status') {
                    console.log('Status message:', data.message);
                    showStatusMessage(data.message);
                } else {
                    // Handle legacy format (direct alert without type)
                    const alertId = `legacy_${data.title}_${Date.now()}`;
                    if (!receivedAlertIds.has(alertId)) {
                        receivedAlertIds.add(alertId);
                        displayAlert(data);
                    }
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        socket.onclose = function(e) {
            console.log("WebSocket connection closed:", e.code, e.reason);
            showConnectionStatus('disconnected', `Connection closed (Code: ${e.code})`);
            alertsStarted = false; // Reset flag for reconnection

            // Attempt to reconnect if not manually closed
            if (e.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts++;
                console.log(`Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts})...`);
                showConnectionStatus('reconnecting', `Reconnecting... (${reconnectAttempts}/${maxReconnectAttempts})`);
                setTimeout(connectWebSocket, reconnectInterval);
            } else if (reconnectAttempts >= maxReconnectAttempts) {
                showErrorMessage('Failed to reconnect after multiple attempts. Please refresh the page.');
            }
        };

        socket.onerror = function(error) {
            console.error("WebSocket error:", error);
            showConnectionStatus('error', 'Connection error occurred');
            showErrorMessage('WebSocket connection error. Please check if the server is running.');
        };

    } catch (error) {
        console.error("Failed to create WebSocket connection:", error);
        showErrorMessage('Failed to create WebSocket connection: ' + error.message);
    }
}

function displayAlert(data) {
    const alertsList = document.getElementById('alerts-list');
    if (!alertsList) {
        console.error('alerts-list element not found');
        return;
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert websocket-alert';
    alertDiv.id = `alert-${data.alert_id || Date.now()}`; // Add unique ID to prevent duplicates

    // Create timestamp
    const timestamp = new Date().toLocaleTimeString();

    // Enhanced alert display with sequence info
    let sequenceInfo = '';
    if (data.sequence && data.total) {
        sequenceInfo = ` <span class="sequence-info">(${data.sequence}/${data.total})</span>`;
    }

    // Handle both new format (data.title) and legacy format
    const title = data.title || 'Alert';
    const message = data.message || 'No message';

    alertDiv.innerHTML = `
        <div class="alert-header">
            <strong>⚡ ${title}</strong>${sequenceInfo}
            <span class="alert-timestamp">${timestamp}</span>
        </div>
        <p class="alert-message">${message}</p>
        <div class="alert-meta">
            <span class="delivery-method">📡 WebSocket</span>
        </div>
    `;

    // Add slide-in animation
    alertDiv.style.transform = 'translateX(-100%)';
    alertDiv.style.opacity = '0';
    alertsList.insertBefore(alertDiv, alertsList.firstChild);

    // Animate in
    setTimeout(() => {
        alertDiv.style.transition = 'all 0.5s ease-out';
        alertDiv.style.transform = 'translateX(0)';
        alertDiv.style.opacity = '1';
    }, 10);

    // Limit to 10 alerts displayed
    const allAlerts = alertsList.querySelectorAll('.alert');
    if (allAlerts.length > 10) {
        allAlerts[allAlerts.length - 1].remove();
    }

    // Add highlight effect
    alertDiv.style.backgroundColor = '#e8f5e8';
    setTimeout(() => {
        alertDiv.style.backgroundColor = '';
    }, 3000);
}

function showStatusMessage(message) {
    const alertsList = document.getElementById('alerts-list');
    if (!alertsList) return;

    const statusDiv = document.createElement('div');
    statusDiv.className = 'alert status-alert';
    statusDiv.innerHTML = `
        <div class="alert-header">
            <strong>ℹ️ Server Status</strong>
            <span class="alert-timestamp">${new Date().toLocaleTimeString()}</span>
        </div>
        <p class="alert-message">${message}</p>
    `;

    alertsList.insertBefore(statusDiv, alertsList.firstChild);

    // Remove status message after 5 seconds
    setTimeout(() => {
        if (statusDiv.parentNode) {
            statusDiv.remove();
        }
    }, 5000);
}

function showConnectionStatus(status, message) {
    let statusElement = document.getElementById('connection-status');

    if (!statusElement) {
        statusElement = document.createElement('div');
        statusElement.id = 'connection-status';
        statusElement.className = 'connection-status';

        const alertsList = document.getElementById('alerts-list');
        if (alertsList && alertsList.parentNode) {
            alertsList.parentNode.insertBefore(statusElement, alertsList);
        }
    }

    statusElement.className = `connection-status ${status}`;

    const statusIcons = {
        connected: '🟢',
        disconnected: '🔴',
        reconnecting: '🟡',
        error: '🔴'
    };

    statusElement.innerHTML = `
        <span class="status-icon">${statusIcons[status] || '⚪'}</span>
        <span class="status-text">${message}</span>
        <span class="status-time">${new Date().toLocaleTimeString()}</span>
    `;
}

function showErrorMessage(message) {
    const alertsList = document.getElementById('alerts-list');
    if (!alertsList) return;

    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert error-alert';
    errorDiv.innerHTML = `
        <div class="alert-header">
            <strong>❌ WebSocket Error</strong>
            <span class="alert-timestamp">${new Date().toLocaleTimeString()}</span>
        </div>
        <p class="alert-message">${message}</p>
    `;

    alertsList.insertBefore(errorDiv, alertsList.firstChild);

    // Remove error after 15 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 15000);
}

function showLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = 'block';
    }
}

function hideLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

function stopAlerts() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: 'stop_alerts',
            message: 'Stop sending alerts'
        }));
        alertsStarted = false;
        console.log('Requested to stop alerts');
    }
}

function restartAlerts() {
    if (socket && socket.readyState === WebSocket.OPEN && !alertsStarted) {
        alertsStarted = true;
        receivedAlertIds.clear(); // Clear duplicates tracker
        socket.send(JSON.stringify({
            type: 'start_alerts',
            message: 'Restart alert sequence'
        }));
        console.log('Requested to restart alerts');
    }
}

// Establish WebSocket connection when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('WebSocket client initialized');
    console.log('Target WebSocket URL:', WEBSOCKET_URL);

    showLoadingSpinner();
    showConnectionStatus('connecting', 'Connecting to Alert Server...');

    // Start connection
    connectWebSocket();
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (socket) {
        socket.close(1000, 'Page unloading');
    }
});
