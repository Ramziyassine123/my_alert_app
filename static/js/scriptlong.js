function longPollForAlerts(serverUrl) {
    fetch(serverUrl)
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok.');
        })
        .then(data => {
            console.log('Received data:', data);  // Debugging line
            if (data.alert) {
                displayAlert(data.alert);
            } else if (data.error) {
                console.error('Server error:', data.error);
            }
            longPollForAlerts(serverUrl);
        })
        .catch(error => {
            console.error('Error:', error);
            setTimeout(() => longPollForAlerts(serverUrl), 5000);
        });
}

function displayAlert(alert) {
    const alertsContainer = document.getElementById('alerts');
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert';
    alertDiv.innerHTML = `<strong>${alert.title}</strong><p>${alert.message}</p>`;
    alertsContainer.appendChild(alertDiv);
}

document.addEventListener('DOMContentLoaded', () => {
    const serverUrl = 'http://127.0.0.1:8001/poll/alerts/';
    longPollForAlerts(serverUrl);
});
// function showLoadingSpinner() {
//     document.getElementById('loading-spinner').style.display = 'block';
// }
//
// // Function to hide the loading spinner
// function hideLoadingSpinner() {
//     document.getElementById('loading-spinner').style.display = 'none';
// }

