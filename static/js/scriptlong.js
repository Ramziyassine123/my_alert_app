
// Global variable that can be overridden by the HTML template
let serverUrl = 'http://127.0.0.1:8001/api/poll/alerts/'; // Default fallback

function longPollForAlerts(url) {
    console.log(`🔄 Making long polling request to: ${url}`);

    fetch(url, {
        method: 'GET',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
    })
        .then(response => {
            console.log(`📡 Response status: ${response.status} ${response.statusText}`);
            if (response.ok) {
                return response.json();
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText} - URL: ${url}`);
        })
        .then(data => {
            console.log('✅ Received data:', data);
            if (data.alert) {
                displayAlert(data.alert);
            } else if (data.error) {
                console.error('❌ Server error:', data.error);
                showErrorMessage(data.error);
            } else {
                console.warn('⚠️ Unexpected response format:', data);
            }
            // Continue polling with same URL
            setTimeout(() => longPollForAlerts(url), 1000);
        })
        .catch(error => {
            console.error('❌ Long polling error:', error);
            showErrorMessage(`Connection error: ${error.message}`);
            // Retry after 5 seconds
            setTimeout(() => longPollForAlerts(url), 5000);
        });
}

function displayAlert(alert) {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) {
        console.error('❌ Alerts container not found');
        return;
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert';

    // Create timestamp
    const timestamp = new Date().toLocaleTimeString();

    let sequenceInfo = '';
    if (alert.sequence && alert.total) {
        sequenceInfo = ` <span class="sequence-info">(${alert.sequence}/${alert.total})</span>`;
    }

    alertDiv.innerHTML = `
        <div class="alert-header">
            <strong>${alert.title}</strong>${sequenceInfo}
            <span class="alert-timestamp">${timestamp}</span>
        </div>
        <p class="alert-message">${alert.message}</p>
    `;

    // Add to top of alerts list
    alertsContainer.insertBefore(alertDiv, alertsContainer.firstChild);

    // Limit to 10 alerts displayed
    const allAlerts = alertsContainer.querySelectorAll('.alert');
    if (allAlerts.length > 10) {
        allAlerts[allAlerts.length - 1].remove();
    }

    // Add highlight animation
    alertDiv.style.backgroundColor = '#d4edda';
    setTimeout(() => {
        alertDiv.style.backgroundColor = '';
    }, 2000);
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
    `;

    alertsContainer.insertBefore(errorDiv, alertsContainer.firstChild);

    // Remove error after 15 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 15000);
}
function testServerConnection(url) {
    console.log('🧪 Testing server connection...');
    fetch(url, {
        method: 'GET',
        mode: 'cors',
    })
        .then(response => {
            console.log('🧪 Test response status:', response.status);
            if (response.ok) {
                console.log('✅ Server is reachable');
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
        });
}

// Initialize when page loads - DO NOT auto-start polling
document.addEventListener('DOMContentLoaded', () => {
    console.log('📡 Long Polling client initialized for Unified Server');
    console.log(`🎯 Default server URL: ${serverUrl}`);

    // Show initial status
    const alertsContainer = document.getElementById('alerts');
    if (alertsContainer) {
        const statusDiv = document.createElement('div');
        statusDiv.className = 'alert status-alert';
        statusDiv.innerHTML = `
            <div class="alert-header">
                <strong>🔄 Long Polling Ready</strong>
                <span class="alert-timestamp">${new Date().toLocaleTimeString()}</span>
            </div>
            <p class="alert-message">Long polling client initialized. Waiting for external trigger...</p>
            <p class="alert-message"><small>Target: ${serverUrl}</small></p>
        `;
        alertsContainer.appendChild(statusDiv);

        // Remove status after 3 seconds
        setTimeout(() => {
            if (statusDiv.parentNode) {
                statusDiv.remove();
            }
        }, 3000);
    }

    // Test server connection
    testServerConnection(serverUrl);

    console.log('=== UNIFIED SERVER LONG POLLING ===');
    console.log('Method: HTTP Long Polling');
    console.log('Status: Ready (waiting for external trigger)');
    console.log('=====================================');
});

// Export functions for external use
window.startLongPolling = function(url) {
    serverUrl = url || serverUrl;
    console.log(`🚀 Starting long polling with URL: ${serverUrl}`);
    longPollForAlerts(serverUrl);
};

window.longPollForAlerts = longPollForAlerts;