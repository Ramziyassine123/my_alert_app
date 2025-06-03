
// Import Firebase scripts for service worker
importScripts('https://www.gstatic.com/firebasejs/9.15.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.15.0/firebase-messaging-compat.js');

// Firebase configuration - must match your main app config
const firebaseConfig = {
    apiKey: "AIzaSyD1C5ob3B7L2N57vrlC-3siYRMwUgGLL7M",
    authDomain: "myalertappproject.firebaseapp.com",
    projectId: "myalertappproject",
    storageBucket: "myalertappproject.firebasestorage.app",
    messagingSenderId: "628710969002",
    appId: "1:628710969002:web:735611410af3e440d5cad3",
    measurementId: "G-S9HE2VRY8T"
};

// Initialize Firebase in service worker
firebase.initializeApp(firebaseConfig);

// Get messaging instance
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage(function(payload) {
    console.log('Received background message:', payload);

    const notificationTitle = payload.notification?.title || 'New Alert';
    const notificationOptions = {
        body: payload.notification?.body || 'You have a new alert',
        icon: '/static/icon-192x192.png',
        badge: '/static/badge-72x72.png',
        tag: 'alert-notification',
        requireInteraction: true,
        data: payload.data || {}
    };

    return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification clicks
self.addEventListener('notificationclick', function(event) {
    console.log('Notification clicked:', event);
    event.notification.close();

    // Open or focus the app window
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(function(clientList) {
            for (let i = 0; i < clientList.length; i++) {
                const client = clientList[i];
                if (client.url.includes(self.location.origin) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow('/');
            }
        })
    );
});