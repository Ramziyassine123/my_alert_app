// Enhanced Long Polling Client - Complete Rewrite
// File: static/js/scriptlong.js

// PERSISTENT CLIENT ID - Key to realistic long polling
let persistentClientId = null;

// Initialize client ID once per session
function initializeClientId() {
    // Try to get from localStorage first (survives page refresh)
    persistentClientId = localStorage.getItem('longpoll_client_id');

    if (!persistentClientId) {
        // Generate new stable ID for this browser session
        const timestamp = Date.now();
        const randomPart = Math.random().toString(36).substr(2, 9);
        const browserFingerprint = getBrowserFingerprint();

        persistentClientId = `client_${timestamp}_${randomPart}_${browserFingerprint}`;

        // Store for session persistence
        localStorage.setItem('longpoll_client_id', persistentClientId);

        console.log(`🆔 New client ID generated: ${persistentClientId}`);
    } else {
        console.log(`🆔 Resuming with existing client ID: ${persistentClientId}`);
    }

    return persistentClientId;
}

// Generate browser fingerprint for uniqueness
function getBrowserFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('Browser fingerprint', 2, 2);

    const fingerprint = canvas.toDataURL().slice(-10);
    return fingerprint.replace(/[^a-zA-Z0-9]/g, '').substr(0, 6);
}

// Reset client position (for demo purposes)
function resetClientPosition() {
    if (persistentClientId) {
        console.log('🔄 Resetting client position...');

        fetch('http://127.0.0.1:8001/api/poll/reset/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `client_id=${persistentClientId}`
        })
            .then(response => response.json())
            .then(data => {
                console.log('✅ Client position reset:', data.message);
                updateConnectionStatus('reset', 'Position reset - will start from first alert');
            })
            .catch(error => {
                console.error('❌ Failed to reset position:', error);
            });
    }
}

// Long polling with persistent client ID
function longPollForAlerts(serverUrl) {
    // Ensure we have a client ID
    if (!persistentClientId) {
        initializeClientId();
    }

    // Build URL with persistent client ID
    const urlParams = new URLSearchParams({
        client_id: persistentClientId,
        timeout: 20  // 20 second timeout
    });

    const pollUrl = `${serverUrl}?${urlParams}`;

    console.log(`🔄 Long polling request: ${persistentClientId}`);

    const requestStart = performance.now();

    fetch(pollUrl, {
        method: 'GET',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    })
        .then(response => {
            const requestTime = (performance.now() - requestStart).toFixed(2);
            console.log(`📡 Response received in ${requestTime}ms`);

            if (response.ok) {
                return response.json();
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        })
        .then(data => {
            handleLongPollResponse(data, serverUrl);
        })
        .catch(error => {
            console.error('❌ Long polling error:', error);
            showErrorMessage(`Connection error: ${error.message}`);

            // Retry with exponential backoff
            const retryDelay = Math.min(5000, 1000 * Math.pow(2, getRetryCount()));
            setTimeout(() => {
                resetRetryCount();
                longPollForAlerts(serverUrl);
            }, retryDelay);
        });
}

// Handle long polling response
function handleLongPollResponse(data, serverUrl) {
    if (data.alert) {
        // Got a new alert!
        displayAlertEnhanced(data.alert);

        const sequence = data.alert.sequence || '?';
        const total = data.alert.total || '?';
        const immediate = data.immediate ? ' (immediate)' : ` (waited ${data.wait_time?.toFixed(2)}s)`;

        console.log(`✅ Alert ${sequence}/${total} received${immediate}`);

        updateConnectionStatus('connected',
            `Received alert ${sequence}/${total} - ${data.has_more ? 'more available' : 'caught up'}`);

        // Continue polling with shorter delay to catch any missed alerts
        if (data.has_more) {
            setTimeout(() => longPollForAlerts(serverUrl), 100); // Reduced delay for better sync
        } else {
            // Caught up! Now demonstrate true long polling (wait for new data)
            updateConnectionStatus('waiting', 'Caught up! Waiting for new alerts (20s timeout)...');
            setTimeout(() => longPollForAlerts(serverUrl), 1000); // Reduced delay
        }

    } else if (data.timeout) {
        // Server timeout - normal long polling behavior
        console.log('⏰ Long poll timeout - no new data');
        updateConnectionStatus('polling', 'No new alerts - continuing to poll...');

        // Continue polling with minimal delay to catch new data quickly
        setTimeout(() => longPollForAlerts(serverUrl), 50);

    } else if (data.error) {
        console.error('❌ Server error:', data.error);
        showErrorMessage(data.error);

        // Retry after delay
        setTimeout(() => longPollForAlerts(serverUrl), 3000);
    } else {
        console.warn('⚠️ Unexpected response format:', data);
        setTimeout(() => longPollForAlerts(serverUrl), 1000);
    }
}

// Display alert with enhanced information (renamed to avoid recursion)
function displayAlertEnhanced(alert) {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) {
        console.error('❌ Alerts container not found');
        return;
    }

    // Hide "no alerts" message
    const noAlertsMessage = document.getElementById('noAlertsMessage');
    if (noAlertsMessage) {
        noAlertsMessage.style.display = 'none';
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success';
    alertDiv.style.marginBottom = '10px';
    alertDiv.style.padding = '15px';
    alertDiv.style.border = '1px solid #d4edda';
    alertDiv.style.borderRadius = '5px';
    alertDiv.style.backgroundColor = '#d4edda';

    const timestamp = new Date().toLocaleTimeString();
    const sequence = alert.sequence ? `${alert.sequence}/${alert.total}` : '';
    const processingTime = alert.server_process_time ? ` (${alert.server_process_time.toFixed(2)}ms)` : '';

    alertDiv.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="flex: 1;">
                <div style="font-weight: bold; color: #155724; margin-bottom: 5px;">
                    📢 ${alert.title} ${sequence ? `[${sequence}]` : ''}
                </div>
                <div style="color: #155724; margin-bottom: 8px;">
                    ${alert.message}
                </div>
                <div style="font-size: 0.85em; color: #6c757d;">
                    Client: ${persistentClientId?.substr(-8) || 'unknown'} • 
                    Received: ${timestamp}${processingTime}
                </div>
            </div>
            <div style="margin-left: 15px; font-size: 1.2em;">
                🔔
            </div>
        </div>
    `;

    // Add to top of alerts
    alertsContainer.insertBefore(alertDiv, alertsContainer.firstChild);

    // Limit displayed alerts
    const allAlerts = alertsContainer.querySelectorAll('.alert');
    if (allAlerts.length > 10) {
        allAlerts[allAlerts.length - 1].remove();
    }

    // Highlight animation
    alertDiv.style.transform = 'scale(0.95)';
    alertDiv.style.transition = 'all 0.3s ease';

    setTimeout(() => {
        alertDiv.style.transform = 'scale(1)';
        alertDiv.style.backgroundColor = '#d4edda';
    }, 100);
}

// Connection status management
function updateConnectionStatus(status, message) {
    const statusElement = document.getElementById('connectionStatus');
    const timeElement = document.getElementById('statusTime');

    if (statusElement) {
        let icon = '🔄';
        let className = 'connection-status connecting';

        switch(status) {
            case 'connected':
                icon = '✅';
                className = 'connection-status connected';
                break;
            case 'waiting':
                icon = '⏳';
                className = 'connection-status waiting';
                break;
            case 'polling':
                icon = '🔄';
                className = 'connection-status polling';
                break;
            case 'reset':
                icon = '🔄';
                className = 'connection-status reset';
                break;
            case 'error':
                icon = '❌';
                className = 'connection-status error';
                break;
        }

        statusElement.className = className;
        statusElement.querySelector('.status-icon').textContent = icon;
        statusElement.querySelector('.status-text').textContent = message;
    }

    if (timeElement) {
        timeElement.textContent = new Date().toLocaleTimeString();
    }
}

// Error handling
function showErrorMessage(message) {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) return;

    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-error';
    errorDiv.style.backgroundColor = '#f8d7da';
    errorDiv.style.borderColor = '#f5c6cb';
    errorDiv.style.color = '#721c24';
    errorDiv.style.padding = '15px';
    errorDiv.style.marginBottom = '10px';
    errorDiv.style.borderRadius = '5px';

    errorDiv.innerHTML = `
        <div style="font-weight: bold; margin-bottom: 5px;">
            ⚠️ Connection Error
        </div>
        <div style="margin-bottom: 8px;">
            ${message}
        </div>
        <div style="font-size: 0.85em; opacity: 0.8;">
            Client: ${persistentClientId?.substr(-8) || 'unknown'} • 
            Time: ${new Date().toLocaleTimeString()}
        </div>
    `;

    alertsContainer.insertBefore(errorDiv, alertsContainer.firstChild);

    // Remove error after 10 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 10000);

    updateConnectionStatus('error', message);
}

// Retry logic
let retryCount = 0;
function getRetryCount() { return retryCount++; }
function resetRetryCount() { retryCount = 0; }

// Clear all alerts
function clearAlerts() {
    if (confirm('Are you sure you want to clear all alerts?')) {
        const alertsContainer = document.getElementById('alerts');
        if (alertsContainer) {
            alertsContainer.innerHTML = `
                <div class="no-alerts-message" id="noAlertsMessage">
                    <h3>🔄 Waiting for alerts...</h3>
                    <p>Long polling is active and waiting for new alerts from the server.</p>
                </div>
            `;
        }

        console.log('🗑️ All alerts cleared');
        updateConnectionStatus('reset', 'Alerts cleared - ready for new alerts');
    }
}

// Test server connection
function testServerConnection(url) {
    console.log('🧪 Testing server connection...');
    updateConnectionStatus('connecting', 'Testing server connection...');

    fetch(url, {
        method: 'GET',
        mode: 'cors',
        timeout: 5000
    })
        .then(response => {
            console.log('🧪 Test response status:', response.status);
            if (response.ok) {
                console.log('✅ Server is reachable');
                updateConnectionStatus('connected', 'Server connection verified');
                return response.json();
            } else {
                console.log('❌ Server returned error:', response.status);
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
            updateConnectionStatus('error', `Server test failed: ${error.message}`);
        });
}

// Store original displayAlert before we override it
const originalDisplayAlert = window.displayAlert;

// Enhanced displayAlert that integrates with existing HTML template
window.displayAlert = function(alert) {
    // Call our enhanced display function directly (avoid recursion)
    displayAlertEnhanced(alert);

    // Call original if it exists (for backward compatibility)
    if (originalDisplayAlert && typeof originalDisplayAlert === 'function' && originalDisplayAlert !== window.displayAlert) {
        try {
            originalDisplayAlert(alert);
        } catch(e) {
            console.warn('Original displayAlert function failed:', e);
        }
    }
};

// Simulate adding a new alert (for demo purposes)
function simulateNewAlert() {
    const titles = [
        'Breaking News Alert',
        'System Update',
        'Important Notice',
        'User Activity',
        'Security Alert',
        'Maintenance Window',
        'Performance Alert',
        'Network Status',
        'Database Update',
        'Server Migration',
        'New Feature Release',
        'Policy Update'
    ];

    const messages = [
        'This is a simulated alert to demonstrate long polling behavior.',
        'New data has been added to showcase real-time delivery.',
        'Testing the immediate delivery capability of long polling.',
        'Demonstrating server-push notification functionality.',
        'This alert was generated to show live updates.',
        'Real-time communication test in progress.',
        'Long polling demonstration alert.',
        'Showing how new data is immediately delivered to waiting clients.',
        'This alert proves that long polling works for real-time updates.',
        'New information has been added and delivered instantly.',
        'Live data update demonstrating long polling efficiency.',
        'Real-time alert delivery system working perfectly.'
    ];

    const title = titles[Math.floor(Math.random() * titles.length)];
    const message = messages[Math.floor(Math.random() * messages.length)];

    console.log('🎭 Simulating new alert via API...');
    updateConnectionStatus('connecting', 'Adding new alert to server...');

    fetch('http://127.0.0.1:8001/api/poll/simulate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: title,
            message: message
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('✅ New alert simulated:', data);
            updateConnectionStatus('connected', 'New alert added - should be delivered immediately to waiting client');

            // Show success message briefly
            setTimeout(() => {
                updateConnectionStatus('waiting', 'Waiting for next alert or 20s timeout...');
            }, 3000);
        })
        .catch(error => {
            console.error('❌ Failed to simulate alert:', error);
            updateConnectionStatus('error', `Failed to add alert: ${error.message}`);
        });
}

// Simulate multiple alerts with proper timing to prevent skipping
function simulateMultipleAlerts() {
    console.log('🎭 Adding multiple alerts with staggered timing...');
    updateConnectionStatus('connecting', 'Adding 3 new alerts...');

    // Add alerts with 2-second intervals to prevent server race conditions
    for (let i = 0; i < 3; i++) {
        setTimeout(() => {
            console.log(`Adding alert ${i + 1}/3...`);
            simulateNewAlert();
        }, i * 2000); // 2 seconds apart to ensure proper processing
    }
}

// Alert stream functionality
let alertStreamInterval = null;

function startAlertStream() {
    if (alertStreamInterval) {
        console.log('🔄 Alert stream already running');
        return;
    }

    console.log('🚀 Starting continuous alert stream...');
    updateConnectionStatus('connected', 'Alert stream started - new alerts every 8 seconds');

    alertStreamInterval = setInterval(() => {
        simulateNewAlert();
    }, 8000); // Increased to 8 seconds to prevent server overload

    // Update button states
    const startBtn = document.querySelector('button[onclick="startAlertStream()"]');
    const stopBtn = document.querySelector('button[onclick="stopAlertStream()"]');

    if (startBtn) {
        startBtn.disabled = true;
        startBtn.style.opacity = '0.6';
        startBtn.textContent = '🔄 Stream Running';
    }

    if (stopBtn) {
        stopBtn.disabled = false;
        stopBtn.style.opacity = '1';
    }
}

function stopAlertStream() {
    if (alertStreamInterval) {
        clearInterval(alertStreamInterval);
        alertStreamInterval = null;

        console.log('⏹️ Alert stream stopped');
        updateConnectionStatus('waiting', 'Alert stream stopped - waiting for manual alerts or 20s timeout');

        // Update button states
        const startBtn = document.querySelector('button[onclick="startAlertStream()"]');
        const stopBtn = document.querySelector('button[onclick="stopAlertStream()"]');

        if (startBtn) {
            startBtn.disabled = false;
            startBtn.style.opacity = '1';
            startBtn.textContent = '🔄 Start Alert Stream';
        }

        if (stopBtn) {
            stopBtn.disabled = true;
            stopBtn.style.opacity = '0.6';
        }
    }
}

// Global functions for HTML template
window.clearAlerts = clearAlerts;
window.resetClientPosition = resetClientPosition;
window.simulateNewAlert = simulateNewAlert;
window.simulateMultipleAlerts = simulateMultipleAlerts;
window.startAlertStream = startAlertStream;
window.stopAlertStream = stopAlertStream;
window.testServerConnection = testServerConnection;

// Start long polling (called from HTML template)
window.startLongPolling = function(url) {
    const serverUrl = url || 'http://127.0.0.1:8001/api/poll/alerts/';
    console.log(`🚀 Starting realistic long polling with persistent client: ${persistentClientId}`);
    longPollForAlerts(serverUrl);
};

// Override global serverUrl variable for HTML template compatibility
window.serverUrl = 'http://127.0.0.1:8001/api/poll/alerts/';

// Initialize when page loads - ONLY initialize, don't auto-start
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the long polling page
    const isLongPollingPage = window.location.pathname.includes('/poll/') ||
        window.location.pathname.includes('/longpolling') ||
        document.querySelector('#connectionStatus');

    if (!isLongPollingPage) {
        console.log('Not on long polling page - skipping initialization');
        return;
    }

    // Initialize persistent client ID
    initializeClientId();

    console.log('=== REALISTIC LONG POLLING CLIENT ===');
    console.log(`Client ID: ${persistentClientId}`);
    console.log('Features: Persistent identity, progressive alerts, true long polling');
    console.log('=====================================');

    // Show client info in UI
    updateConnectionStatus('connecting', `Initializing client ${persistentClientId.substr(-8)}...`);

    // Test server connection
    setTimeout(() => {
        testServerConnection(window.serverUrl);
    }, 1000);

    // Show initial status
    const alertsContainer = document.getElementById('alerts');
    if (alertsContainer && !alertsContainer.querySelector('.alert')) {
        const statusDiv = document.createElement('div');
        statusDiv.className = 'alert status-alert';
        statusDiv.style.backgroundColor = '#e3f2fd';
        statusDiv.style.borderColor = '#bbdefb';
        statusDiv.style.color = '#0d47a1';
        statusDiv.style.padding = '15px';
        statusDiv.style.marginBottom = '10px';
        statusDiv.style.borderRadius = '5px';

        statusDiv.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 5px;">
                🔄 Long Polling Ready
            </div>
            <div style="margin-bottom: 8px;">
                Client initialized with persistent ID. Ready to receive alerts progressively.
            </div>
            <div style="font-size: 0.85em; color: #6c757d;">
                Client: ${persistentClientId?.substr(-8) || 'unknown'} • 
                Target: ${window.serverUrl}
            </div>
        `;

        alertsContainer.appendChild(statusDiv);

        // Remove status after 5 seconds
        setTimeout(() => {
            if (statusDiv.parentNode) {
                statusDiv.remove();
            }
        }, 5000);
    }
});

// Auto-start polling ONLY on the long polling page
window.addEventListener('load', function() {
    // Only auto-start if we're on the long polling page
    const isLongPollingPage = window.location.pathname.includes('/poll/') ||
        window.location.pathname.includes('/longpolling') ||
        document.querySelector('#connectionStatus'); // Has long polling elements

    if (!isLongPollingPage) {
        console.log('Not on long polling page - skipping auto-start');
        return;
    }

    // Check if HTML template wants to auto-start
    const autoStart = document.querySelector('[data-auto-start-polling]');
    const hashAutoStart = window.location.hash === '#autostart';
    const shouldAutoStart = autoStart || hashAutoStart || true; // Default to auto-start only on this page

    if (shouldAutoStart) {
        setTimeout(() => {
            console.log('🔄 Auto-starting long polling on correct page...');
            updateConnectionStatus('connecting', 'Starting long polling requests...');
            window.startLongPolling();
        }, 3000); // Give time for initialization
    }
});

// Add CSS styles for connection status
const style = document.createElement('style');
style.textContent = `
.connection-status {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    margin: 10px 0;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.connection-status .status-icon {
    margin-right: 10px;
    font-size: 1.2em;
}

.connection-status .status-text {
    flex: 1;
}

.connection-status .status-time {
    font-size: 0.9em;
    opacity: 0.7;
    margin-left: 10px;
}

.connection-status.connecting {
    background-color: #e3f2fd;
    border: 1px solid #bbdefb;
    color: #0d47a1;
}

.connection-status.connected {
    background-color: #e8f5e8;
    border: 1px solid #c8e6c9;
    color: #2e7d32;
}

.connection-status.waiting {
    background-color: #fff3e0;
    border: 1px solid #ffcc02;
    color: #f57c00;
}

.connection-status.polling {
    background-color: #f3e5f5;
    border: 1px solid #ce93d8;
    color: #7b1fa2;
}

.connection-status.reset {
    background-color: #e1f5fe;
    border: 1px solid #81d4fa;
    color: #0277bd;
}

.connection-status.error {
    background-color: #ffebee;
    border: 1px solid #ffcdd2;
    color: #c62828;
}

.alert {
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.no-alerts-message {
    text-align: center;
    padding: 40px 20px;
    color: #6c757d;
    background-color: #f8f9fa;
    border: 2px dashed #dee2e6;
    border-radius: 10px;
    margin: 20px 0;
}

.no-alerts-message h3 {
    margin-bottom: 10px;
    color: #495057;
}
`;
document.head.appendChild(style);

// Export for external use
window.longPollForAlerts = longPollForAlerts;
