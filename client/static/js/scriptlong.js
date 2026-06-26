// scriptlong.js - Simple Long Polling Implementation for Alert Generator

// Global variables
let serverUrl = 'http://127.0.0.1:8001/api/poll/alerts/';
let isPolling = false;
let pollTimeout = 20000; // 20 seconds timeout
let reconnectDelay = 1000; // 1 second between reconnection attempts
let clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

console.log(`🔄 Long Polling Client initialized with ID: ${clientId}`);

function startLongPolling(url = null) {
    if (url) {
        serverUrl = url;
    }

    if (isPolling) {
        console.log('⚠️ Long polling is already active');
        return;
    }

    isPolling = true;
    console.log(`🚀 Starting long polling to: ${serverUrl}`);
    updateConnectionStatus('connecting', 'Starting long polling connection...');

    // Start the polling cycle
    longPollCycle();
}

function stopLongPolling() {
    isPolling = false;
    console.log('🛑 Long polling stopped');
    updateConnectionStatus('disconnected', 'Long polling stopped');
}

function longPollCycle() {
    if (!isPolling) {
        console.log('🛑 Polling cycle stopped');
        return;
    }

    console.log(`🔄 Making long polling request (timeout: ${pollTimeout}ms)`);
    updateConnectionStatus('polling', 'Waiting for alerts...');

    const pollUrl = `${serverUrl}?client_id=${clientId}&timeout=${Math.floor(pollTimeout / 1000)}`;
    const startTime = Date.now();

    fetch(pollUrl, {
        method: 'GET',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        // Add timeout slightly longer than server timeout
        signal: AbortSignal.timeout(pollTimeout + 5000)
    })
        .then(response => {
            const responseTime = Date.now() - startTime;
            console.log(`📡 Response received after ${responseTime}ms - Status: ${response.status}`);

            if (response.ok) {
                return response.json();
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        })
        .then(data => {
            const responseTime = Date.now() - startTime;
            console.log('✅ Long poll response:', data);

            if (data.alert) {
                // Alert received
                displayAlert(data.alert);
                updateConnectionStatus('connected', `Alert received: ${data.alert.title}`);

                // Continue polling immediately for next alert
                setTimeout(() => longPollCycle(), 100);

            } else if (data.timeout) {
                // Server timeout - this is normal, continue polling
                console.log(`⏰ Server timeout after ${responseTime}ms - continuing poll`);
                updateConnectionStatus('polling', 'No new alerts - restarting poll...');

                // Continue polling immediately after timeout
                setTimeout(() => longPollCycle(), 500);

            } else if (data.error) {
                // Server error
                console.error('❌ Server error:', data.error);
                showErrorMessage(`Server error: ${data.error}`);
                updateConnectionStatus('error', `Server error: ${data.error}`);

                // Retry after delay
                setTimeout(() => longPollCycle(), reconnectDelay);

            } else {
                // Unexpected response
                console.warn('⚠️ Unexpected response format:', data);
                updateConnectionStatus('warning', 'Unexpected response - continuing...');

                // Continue polling
                setTimeout(() => longPollCycle(), reconnectDelay);
            }
        })
        .catch(error => {
            const responseTime = Date.now() - startTime;
            console.error(`❌ Long polling error after ${responseTime}ms:`, error);

            if (error.name === 'AbortError') {
                console.log('⏰ Request timeout - retrying...');
                updateConnectionStatus('timeout', 'Request timeout - retrying...');
            } else if (error.message.includes('Failed to fetch')) {
                console.log('🔌 Connection error - server may be down');
                updateConnectionStatus('error', 'Connection error - server may be down');
            } else {
                updateConnectionStatus('error', `Error: ${error.message}`);
            }

            // Retry after delay if still polling
            if (isPolling) {
                setTimeout(() => longPollCycle(), reconnectDelay * 3); // Longer delay for errors
            }
        });
}

function displayAlert(alert) {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) {
        console.error('❌ Alerts container not found');
        return;
    }

    // Hide no alerts message
    const noAlertsMessage = document.getElementById('noAlertsMessage');
    if (noAlertsMessage) {
        noAlertsMessage.style.display = 'none';
    }

    // Update counter (handled by HTML page)
    if (window.updateAlertCount) {
        window.updateAlertCount();
    }

    const alertDiv = document.createElement('div');

    // Add source-specific styling
    const source = alert.source || 'file';
    alertDiv.className = source === 'dynamic' ? 'alert alert-source-dynamic' : 'alert';

    // Create timestamp
    const timestamp = new Date().toLocaleTimeString();

    let sequenceInfo = '';
    if (alert.sequence && alert.total) {
        sequenceInfo = ` <span class="sequence-info">(${alert.sequence}/${alert.total})</span>`;
    }

    let waitTimeInfo = '';
    if (alert.wait_time !== undefined) {
        waitTimeInfo = ` <span class="wait-time">Wait: ${Math.round(alert.wait_time * 1000)}ms</span>`;
    }

    let sourceBadge = '';
    if (source === 'dynamic') {
        sourceBadge = ` <span class="source-badge">generated</span>`;
    }

    // Build alert content
    alertDiv.innerHTML = `
        <div class="alert-header">
            <strong>${alert.title}${sourceBadge}</strong>${sequenceInfo}
            <span class="alert-timestamp">${timestamp}${waitTimeInfo}</span>
        </div>
        <p class="alert-message">${alert.message}</p>
        ${alert.immediate !== undefined ? `<p class="alert-meta">Immediate: ${alert.immediate}</p>` : ''}
        ${alert.poll_cycles !== undefined ? `<p class="alert-meta">Poll cycles: ${alert.poll_cycles}</p>` : ''}
        ${alert.alert_id ? `<p class="alert-meta">ID: ${alert.alert_id}</p>` : ''}
    `;

    // Add to top of alerts list
    alertsContainer.insertBefore(alertDiv, alertsContainer.firstChild);

    // Limit to 10 alerts displayed
    const allAlerts = alertsContainer.querySelectorAll('.alert');
    if (allAlerts.length > 10) {
        allAlerts[allAlerts.length - 1].remove();
    }

    // Add highlight animation based on source
    if (source === 'dynamic') {
        alertDiv.style.backgroundColor = '#e3f2fd'; // Light blue for generated
    } else {
        alertDiv.style.backgroundColor = '#d4edda'; // Light green for file
    }

    setTimeout(() => {
        alertDiv.style.backgroundColor = '';
    }, 2000);

    console.log(`✅ Alert displayed: ${alert.title} (source: ${source})`);
}

function showErrorMessage(message) {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) return;

    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert error-alert';
    errorDiv.innerHTML = `
        <div class="alert-header">
            <strong>⚠️ Connection Error</strong>
            <span class="alert-timestamp">${new Date().toLocaleTimeString()}</span>
        </div>
        <p class="alert-message">${message}</p>
        <p class="alert-message"><small>Target URL: ${serverUrl}</small></p>
        <p class="alert-message"><small>Client ID: ${clientId}</small></p>
    `;

    alertsContainer.insertBefore(errorDiv, alertsContainer.firstChild);

    // Remove error after 10 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 10000);
}

function updateConnectionStatus(status, message) {
    const statusElement = document.getElementById('connectionStatus');
    const timeElement = document.getElementById('statusTime');

    if (statusElement) {
        statusElement.className = `connection-status ${status}`;
        const statusTextElement = statusElement.querySelector('.status-text');
        if (statusTextElement) {
            statusTextElement.textContent = message;
        }
    }

    if (timeElement) {
        timeElement.textContent = new Date().toLocaleTimeString();
    }

    // Also update the status icon based on status
    const statusIcon = statusElement?.querySelector('.status-icon');
    if (statusIcon) {
        switch (status) {
            case 'connecting':
                statusIcon.textContent = '🔄';
                break;
            case 'connected':
                statusIcon.textContent = '✅';
                break;
            case 'polling':
                statusIcon.textContent = '🔍';
                break;
            case 'error':
                statusIcon.textContent = '❌';
                break;
            case 'timeout':
                statusIcon.textContent = '⏰';
                break;
            case 'disconnected':
                statusIcon.textContent = '🔌';
                break;
            default:
                statusIcon.textContent = '🔄';
        }
    }
}

function resetClientPosition() {
    console.log('🔄 Resetting client position on server...');

    const resetUrl = serverUrl.replace('/alerts/', '/reset/');
    const formData = new FormData();
    formData.append('client_id', clientId);

    fetch(resetUrl, {
        method: 'POST',
        mode: 'cors',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log('✅ Client position reset:', data);
            updateConnectionStatus('connected', 'Position reset - ready for alerts');

            // Update counter on page if function exists
            if (window.resetAlertCount) {
                window.resetAlertCount();
            }
        })
        .catch(error => {
            console.error('❌ Failed to reset client position:', error);
            updateConnectionStatus('error', 'Failed to reset position');
        });
}

function testServerConnection() {
    console.log('🧪 Testing server connection...');
    updateConnectionStatus('connecting', 'Testing server connection...');

    fetch(serverUrl.replace('/alerts/', '/status/'), {
        method: 'GET',
        mode: 'cors',
    })
        .then(response => {
            console.log('🧪 Test response status:', response.status);
            if (response.ok) {
                console.log('✅ Server is reachable');
                updateConnectionStatus('connected', 'Server connection OK');
                return response.json();
            } else {
                console.log('❌ Server returned error:', response.status);
                updateConnectionStatus('error', `Server error: ${response.status}`);
                throw new Error(`HTTP ${response.status}`);
            }
        })
        .then(data => {
            if (data) {
                console.log('✅ Server test data:', data);
            }
        })
        .catch(error => {
            console.log('❌ Server test failed:', error);
            updateConnectionStatus('error', 'Server connection failed');
        });
}

// Auto-start polling when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('📡 Simple Long Polling client initialized');
    console.log(`🎯 Server URL: ${serverUrl}`);
    console.log(`⏰ Poll timeout: ${pollTimeout}ms`);
    console.log(`👤 Client ID: ${clientId}`);

    // Test server connection first
    testServerConnection();

    // Start long polling automatically after a short delay
    setTimeout(() => {
        startLongPolling();
    }, 2000);

    console.log('=== SIMPLE LONG POLLING CLIENT ===');
    console.log('Features: Auto-start, 20s timeout, generated alerts support');
    console.log('Auto-starting in 2 seconds...');
    console.log('===================================');
});

// Export functions for global access
window.startLongPolling = startLongPolling;
window.stopLongPolling = stopLongPolling;
window.resetClientPosition = resetClientPosition;
window.testServerConnection = testServerConnection;

// Export for HTML page integration
window.longPollForAlerts = startLongPolling;
