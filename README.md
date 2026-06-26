# Real-Time Communication Protocols — Bachelor Thesis

**B.Sc. Applied Mathematics and Computer Science — FH Aachen**

A full-stack benchmarking application built to compare three real-time communication technologies: **HTTP Long Polling**, **WebSockets**, and **Push Notifications (Firebase FCM)**. The app delivers alerts from a server to a client dashboard using each method, enabling direct performance comparison across different scenarios.

---

## What This Project Does

Real-time communication is a core requirement in modern web applications — from live dashboards to chat systems to notification feeds. But not all approaches are equal. This project implements all three major techniques side by side, measures their behaviour under the same conditions, and draws conclusions about which works best for which use case.

The server sends alerts to the client UI using each method. The client displays them in real time and records timing data, allowing latency, reliability, and resource usage to be compared directly.

---

## Project Structure

```
├── client/     — Django frontend dashboard (port 8000) — receives and displays alerts
└── server/     — Django backend (port 8001) — sends alerts via all three protocols
```

---

## Tech Stack

**Both client and server**
- Python, Django, Django Channels, Daphne (ASGI)

**Server-side specifics**
- WebSocket server via Django Channels
- Long Polling via standard Django REST views
- Push Notifications via Firebase Admin SDK (FCM)
- SQLite database
- Performance testing suite: latency percentiles (p50/p95/p99), throughput, success rates, network condition simulation

**Client-side specifics**
- Django frontend serving the alert dashboard
- Firebase Messaging Service Worker for background push notification handling
- Selenium for end-to-end browser testing
- psutil for system resource monitoring during tests

---

## The Three Methods

**HTTP Long Polling** — The client sends a request and the server holds it open until an alert is ready, then responds. The client immediately sends a new request. Simple and compatible, but creates overhead from repeated connections.

**WebSockets** — A persistent two-way connection is established once. The server pushes alerts instantly over this open channel with minimal overhead. Best for high-frequency, low-latency scenarios.

**Push Notifications (FCM)** — The server sends alerts via Firebase Cloud Messaging even when the client tab is not active. Best for infrequent, high-importance alerts that need to reach the user regardless of browser state.

---

## Running Locally

**Server** (port 8001)
```bash
cd server
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

**Client** (port 8000)
```bash
cd client
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

Then open `http://127.0.0.1:8000` in your browser to access the alert dashboard.

---

## Performance Testing

The server includes a full Python-based performance testing suite:

```bash
cd server
python performance_tests.py          # Full test suite
python websocket_performance_test.py # WebSocket only
python longpolling_performance_test.py
python firebase_performance_test.py
python unified_performance_runner.py # All three with comparison report
```

Tests simulate multiple network conditions: perfect, local WiFi, good mobile, poor mobile, and satellite.

---

## Key Findings

| Method | Latency | Resource Usage | Best For |
|---|---|---|---|
| Long Polling | Medium | High (repeated requests) | Simple setups, low frequency |
| WebSockets | Low | Low (persistent connection) | High-frequency, real-time data |
| Push Notifications | Variable | Very low | Background, infrequent alerts |

---

## Author

**Yassine Ramzi** — [LinkedIn](https://www.linkedin.com/in/yassine-ramzi-471285267/) · [GitHub](https://github.com/Ramziyassine123)
