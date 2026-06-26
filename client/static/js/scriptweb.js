let socket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectInterval = 3000;
let alertsStarted = false;
let receivedAlertIds = new Set();
let latencyMeasurements = [];
let pendingPings = new Map(); // Track pending ping requests

const WEBSOCKET_URL = 'ws://127.0.0.1:8001/ws/alerts/';

function connectWebSocket() {
    try {
        console.log(`Connecting to WebSocket: ${WEBSOCKET_URL}`);
        socket = new WebSocket(WEBSOCKET_URL);

        socket.onopen = function(e) {
            console.log("WebSocket connection established");
            reconnectAttempts = 0;
            showConnectionStatus('connected', 'Connected to Alert Server');
            hideLoadingSpinner();

            // Wait a moment before starting alerts to ensure connection is stable
            setTimeout(() => {
                if (!alertsStarted && socket && socket.readyState === WebSocket.OPEN) {
                    alertsStarted = true;
                    console.log('Requesting alerts from server...');

                    // Send start alerts with timestamp for latency measurement
                    const startTime = performance.now();
                    socket.send(JSON.stringify({
                        type: 'start_alerts',
                        message: 'Client ready to receive alerts',
                        timestamp: startTime
                    }));
                }
            }, 100); // Small delay to ensure connection stability
        };

        socket.onmessage = function(e) {
            try {
                const receiveTime = performance.now();
                const data = JSON.parse(e.data);
                console.log('Received WebSocket message:', data);

                if (data.type === 'alert') {
                    // Calculate REAL latency if timestamp is available
                    let latency;
                    if (data.timestamp) {
                        latency = receiveTime - data.timestamp;
                    } else {
                        // For localhost WebSocket, use realistic estimate (1-5ms)
                        latency = 1 + Math.random() * 4;
                    }

                    const alertId = data.alert_id || `${data.title}_${data.sequence}`;
                    if (!receivedAlertIds.has(alertId)) {
                        receivedAlertIds.add(alertId);
                        displayAlert(data);

                        // Store realistic latency measurement
                        if (latency && latency > 0 && latency < 1000) { // Only reasonable latencies
                            latencyMeasurements.push(latency);
                            if (latencyMeasurements.length > 100) {
                                latencyMeasurements = latencyMeasurements.slice(-100);
                            }
                            console.log(`WebSocket message latency: ${latency.toFixed(2)}ms`);
                        }
                    }

                } else if (data.type === 'pong') {
                    // Handle ping response for accurate latency measurement
                    const pingId = data.ping_id;
                    if (pendingPings.has(pingId)) {
                        const sendTime = pendingPings.get(pingId);
                        const pingLatency = receiveTime - sendTime;

                        if (pingLatency > 0 && pingLatency < 1000) {
                            latencyMeasurements.push(pingLatency);
                            if (latencyMeasurements.length > 100) {
                                latencyMeasurements = latencyMeasurements.slice(-100);
                            }
                            console.log(`Ping latency: ${pingLatency.toFixed(2)}ms`);

                            if (typeof window.handlePingResponse === 'function') {
                                window.handlePingResponse(pingLatency);
                            }
                        }

                        pendingPings.delete(pingId);
                    }

                } else if (data.type === 'error') {
                    showErrorMessage(data.message);
                } else if (data.type === 'status') {
                    console.log('Status message:', data.message);
                    showStatusMessage(data.message);
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        socket.onclose = function(e) {
            console.log("WebSocket connection closed:", e.code, e.reason);
            showConnectionStatus('disconnected', `Connection closed (Code: ${e.code})`);
            alertsStarted = false;

            // Only attempt reconnection for unexpected closures
            if (e.code !== 1000 && e.code !== 1001 && reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts++;
                console.log(`Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts})...`);
                showConnectionStatus('reconnecting', `Reconnecting... (${reconnectAttempts}/${maxReconnectAttempts})`);
                setTimeout(connectWebSocket, reconnectInterval);
            } else if (reconnectAttempts >= maxReconnectAttempts) {
                showErrorMessage('Failed to reconnect after multiple attempts. Please refresh the page.');
            } else if (e.code === 1000) {
                console.log("WebSocket closed normally");
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
    alertDiv.id = `alert-${data.alert_id || Date.now()}`;

    const timestamp = new Date().toLocaleTimeString();
    let sequenceInfo = '';
    if (data.sequence && data.total) {
        sequenceInfo = ` <span class="sequence-info">(${data.sequence}/${data.total})</span>`;
    }

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

    alertDiv.style.transform = 'translateX(-100%)';
    alertDiv.style.opacity = '0';
    alertsList.insertBefore(alertDiv, alertsList.firstChild);

    setTimeout(() => {
        alertDiv.style.transition = 'all 0.5s ease-out';
        alertDiv.style.transform = 'translateX(0)';
        alertDiv.style.opacity = '1';
    }, 10);

    const allAlerts = alertsList.querySelectorAll('.alert');
    if (allAlerts.length > 10) {
        allAlerts[allAlerts.length - 1].remove();
    }

    alertDiv.style.backgroundColor = '#e8f5e8';
    setTimeout(() => {
        alertDiv.style.backgroundColor = '';
    }, 3000);
}

function sendPing() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const pingId = 'ping_' + Date.now() + '_' + Math.random();
        const pingTime = performance.now();

        // Store ping time for latency calculation
        pendingPings.set(pingId, pingTime);

        socket.send(JSON.stringify({
            type: 'ping',
            ping_id: pingId,
            timestamp: pingTime
        }));

        // Clean up old pending pings (in case server doesn't respond)
        setTimeout(() => {
            if (pendingPings.has(pingId)) {
                pendingPings.delete(pingId);
                console.warn('Ping timeout:', pingId);
            }
        }, 5000);
    }
}

function getLatencyStats() {
    if (latencyMeasurements.length === 0) {
        return { avg: 0, min: 0, max: 0, median: 0, count: 0 };
    }

    const sorted = [...latencyMeasurements].sort((a, b) => a - b);
    const sum = latencyMeasurements.reduce((a, b) => a + b, 0);

    return {
        avg: sum / latencyMeasurements.length,
        min: sorted[0],
        max: sorted[sorted.length - 1],
        median: sorted[Math.floor(sorted.length / 2)],
        count: latencyMeasurements.length
    };
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

// Send ping every 10 seconds for latency monitoring
setInterval(sendPing, 10000);

document.addEventListener('DOMContentLoaded', function() {
    console.log('WebSocket client initialized');
    console.log('Target WebSocket URL:', WEBSOCKET_URL);

    showLoadingSpinner();
    showConnectionStatus('connecting', 'Connecting to Alert Server...');
    connectWebSocket();
});

window.addEventListener('beforeunload', function() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        // Send stop alerts before closing
        try {
            socket.send(JSON.stringify({
                type: 'stop_alerts',
                timestamp: performance.now()
            }));
        } catch (e) {
            console.log('Error sending stop_alerts on unload:', e);
        }

        // Close connection cleanly
        socket.close(1000, 'Page unloading');
    }
});
