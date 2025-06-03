// Firebase configuration - Replace with your project's config
const firebaseConfig = {
    apiKey: "AIzaSyD1C5ob3B7L2N57vrlC-3siYRMwUgGLL7M",
    authDomain: "myalertappproject.firebaseapp.com",
    projectId: "myalertappproject",
    storageBucket: "myalertappproject.firebasestorage.app",
    messagingSenderId: "628710969002",
    appId: "1:628710969002:web:735611410af3e440d5cad3",
    measurementId: "G-S9HE2VRY8T"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

// API endpoints - Server runs on port 8000, client on 8001
const API_BASE_URL = 'http://localhost:8000/api';
const REGISTER_TOKEN_URL = `${API_BASE_URL}/register-token/`;
const GET_ALERTS_URL = `${API_BASE_URL}/alerts/`;

// DOM elements
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const alertsContainer = document.getElementById('alertsContainer');
const noAlertsMessage = document.getElementById('noAlertsMessage');

// Alert storage
let receivedAlerts = [];
let alertCounter = 0;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Alert Handler initialized');

    // Register service worker first
    registerServiceWorker().then(() => {
        // Don't automatically request permission - wait for user action
        loadExistingAlerts();
        updateStatus('disconnected', 'Click "Enable Notifications" to start');
    });
});

/**
 * Register service worker for background notifications
 */
async function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
            console.log('Service Worker registered successfully:', registration);
            return registration;
        } catch (error) {
            console.error('Service Worker registration failed:', error);
            throw error;
        }
    } else {
        throw new Error('Service Worker not supported');
    }
}

/**
 * Initialize Firebase Cloud Messaging (called by user action)
 */
async function initializeFirebaseMessaging() {
    try {
        updateStatus('disconnected', 'Requesting notification permission...');

        // Request notification permission (must be called from user action)
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            console.log('Notification permission granted');
            await setupMessaging();
        } else {
            updateStatus('disconnected', 'Notification permission denied - Click "Enable Notifications" to try again');
            console.log('Notification permission denied');
        }
    } catch (error) {
        console.error('Error initializing Firebase messaging:', error);
        updateStatus('disconnected', 'Failed to initialize Firebase: ' + error.message);
    }
}

/**
 * Setup Firebase messaging and token registration
 */
async function setupMessaging() {
    try {
        // IMPORTANT: Replace with your actual VAPID key from Firebase Console
        // Go to Firebase Console > Project Settings > Cloud Messaging > Web configuration
        const token = await messaging.getToken({
            vapidKey: 'BE6ICAm5uvt9ZjqJ9CkLf6r8MMwFgNA4BxW_g0Y9mQ2tpKc3X93N3QFnq3X0fVTLEMTvpgfh9Z5lBcg8qLmMZcQ' // Replace with actual VAPID key
        });

        if (token) {
            console.log('FCM Token:', token);
            await registerToken(token);
            updateStatus('connected', 'Connected - Ready to receive alerts');

            // Handle foreground messages
            messaging.onMessage((payload) => {
                console.log('Message received in foreground:', payload);
                handleNotification(payload);
            });

        } else {
            console.log('No registration token available');
            updateStatus('disconnected', 'Failed to get FCM token');
        }
    } catch (error) {
        console.error('Error setting up messaging:', error);
        updateStatus('disconnected', 'Setup failed: ' + error.message);
    }
}

/**
 * Register FCM token with Django backend
 */
async function registerToken(token) {
    try {
        const response = await fetch(REGISTER_TOKEN_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ token: token })
        });

        if (response.ok) {
            const data = await response.json();
            console.log('Token registered successfully:', data);
        } else {
            const errorText = await response.text();
            console.error('Failed to register token:', response.status, errorText);
        }
    } catch (error) {
        console.error('Error registering token:', error);
    }
}

/**
 * Handle incoming notifications
 */
function handleNotification(payload) {
    console.log('Handling notification:', payload);

    const notification = payload.notification || {};
    const data = payload.data || {};

    const alert = {
        id: ++alertCounter,
        title: notification.title || 'Alert',
        message: notification.body || 'No message',
        timestamp: new Date(),
        alertIndex: data.alert_index || null,
        isNew: true
    };

    // Add to alerts array
    receivedAlerts.unshift(alert);

    // Display the alert
    displayAlert(alert);

    // Show browser notification if page is not focused
    if (document.hidden) {
        showBrowserNotification(alert);
    }

    // Update local storage
    saveAlertsToStorage();

    // Remove 'new' status after 5 seconds
    setTimeout(() => {
        alert.isNew = false;
        updateAlertDisplay(alert.id);
    }, 5000);
}

/**
 * Display alert in the UI
 */
function displayAlert(alert) {
    // Hide no alerts message
    noAlertsMessage.style.display = 'none';

    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert-item ${alert.isNew ? 'new' : ''}`;
    alertElement.id = `alert-${alert.id}`;

    alertElement.innerHTML = `
        <div class="alert-title">
            <span class="alert-icon">${getAlertIcon(alert.title)}</span>
            ${escapeHtml(alert.title)}
        </div>
        <div class="alert-message">
            ${escapeHtml(alert.message)}
        </div>
        <div class="alert-meta">
            <span class="alert-time">${formatTime(alert.timestamp)}</span>
            <span class="alert-badge ${alert.isNew ? 'new' : ''}">
                ${alert.isNew ? 'NEW' : 'Alert #' + alert.id}
            </span>
        </div>
    `;

    // Insert at the beginning
    alertsContainer.insertBefore(alertElement, alertsContainer.firstChild);

    // Limit displayed alerts to 50
    const alertElements = alertsContainer.querySelectorAll('.alert-item');
    if (alertElements.length > 50) {
        alertElements[alertElements.length - 1].remove();
        receivedAlerts = receivedAlerts.slice(0, 50);
    }
}

/**
 * Update existing alert display
 */
function updateAlertDisplay(alertId) {
    const alertElement = document.getElementById(`alert-${alertId}`);
    if (alertElement) {
        alertElement.classList.remove('new');
        const badge = alertElement.querySelector('.alert-badge');
        if (badge) {
            badge.classList.remove('new');
            badge.textContent = `Alert #${alertId}`;
        }
    }
}

/**
 * Show browser notification
 */
function showBrowserNotification(alert) {
    if (Notification.permission === 'granted') {
        const notification = new Notification(alert.title, {
            body: alert.message,
            icon: '/static/icon-192x192.png', // Add your icon path
            badge: '/static/badge-72x72.png', // Add your badge path
            tag: `alert-${alert.id}`,
            requireInteraction: true
        });

        notification.onclick = function() {
            window.focus();
            notification.close();
        };

        // Auto close after 10 seconds
        setTimeout(() => notification.close(), 10000);
    }
}

/**
 * Load existing alerts from server
 */
async function loadExistingAlerts() {
    try {
        const response = await fetch(GET_ALERTS_URL);
        if (response.ok) {
            const data = await response.json();
            console.log('Loaded alerts from server:', data);
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }

    // Load from local storage
    loadAlertsFromStorage();
}

/**
 * Save alerts to local storage
 */
function saveAlertsToStorage() {
    try {
        const alertsToSave = receivedAlerts.map(alert => ({
            ...alert,
            timestamp: alert.timestamp.toISOString()
        }));
        localStorage.setItem('receivedAlerts', JSON.stringify(alertsToSave));
    } catch (error) {
        console.error('Error saving alerts to storage:', error);
    }
}

/**
 * Load alerts from local storage
 */
function loadAlertsFromStorage() {
    try {
        const savedAlerts = localStorage.getItem('receivedAlerts');
        if (savedAlerts) {
            const alerts = JSON.parse(savedAlerts);
            alerts.forEach(alert => {
                alert.timestamp = new Date(alert.timestamp);
                alert.isNew = false;
                receivedAlerts.push(alert);
                displayAlert(alert);
            });

            if (alerts.length > 0) {
                alertCounter = Math.max(...alerts.map(a => a.id));
            }
        }
    } catch (error) {
        console.error('Error loading alerts from storage:', error);
    }
}

/**
 * Update connection status
 */
function updateStatus(status, message) {
    statusIndicator.className = `status-indicator ${status}`;
    statusText.textContent = message;
}

/**
 * Request notification permission (triggered by user button click)
 */
async function requestNotificationPermission() {
    try {
        updateStatus('disconnected', 'Requesting notification permission...');
        await initializeFirebaseMessaging();
    } catch (error) {
        console.error('Error requesting permission:', error);
        updateStatus('disconnected', 'Permission request failed: ' + error.message);
    }
}

/**
 * Clear all alerts
 */
function clearAlerts() {
    if (confirm('Are you sure you want to clear all alerts?')) {
        receivedAlerts = [];
        alertCounter = 0;
        alertsContainer.innerHTML = '';
        noAlertsMessage.style.display = 'block';
        alertsContainer.appendChild(noAlertsMessage);
        localStorage.removeItem('receivedAlerts');
        console.log('All alerts cleared');
    }
}

/**
 * Get appropriate icon for alert type
 */
function getAlertIcon(title) {
    const titleLower = title.toLowerCase();
    if (titleLower.includes('emergency')) return '🚨';
    if (titleLower.includes('warning')) return '⚠️';
    if (titleLower.includes('info')) return 'ℹ️';
    if (titleLower.includes('success')) return '✅';
    if (titleLower.includes('fire')) return '🔥';
    if (titleLower.includes('weather')) return '🌦️';
    return '📢';
}

/**
 * Format timestamp for display
 */
function formatTime(timestamp) {
    const now = new Date();
    const diff = now - timestamp;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;

    return timestamp.toLocaleDateString() + ' ' + timestamp.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}