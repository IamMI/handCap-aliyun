# ✋ Gesture Recognition & Alert WebSocket Server

This is a **Node.js-based WebSocket server** designed to handle gesture recognition data and forward alerts from an embedded board. It supports real-time broadcasting, alert scheduling, multiple clients, and basic health checks.

---

## 📌 Use Cases

- Real-time gesture recognition broadcasting
- Receiving alerts from embedded devices (via HTTP POST)
- Alert handling within allowed time windows
- Supporting multiple WebSocket client connections

---

## 🚀 Features

### 1. WebSocket Gesture Broadcasting

- Communicates with clients over WebSocket protocol
- Default connection endpoint: `ws://0.0.0.0:3000`
- Sends the last known gesture to each new client
- Prevents frequent duplicate broadcasts (configurable minimum interval)

### 2. HTTP Alert Interface

- Provides `/alert` endpoint (POST) for embedded boards to report events
- Only forwards alerts if the request is within the configured time window
- Responds with status message to indicate success or ignored alert

### 3. Alert Time Window Control

- Clients can set allowed alert time ranges
- Format: `{ startHour, startMin, endHour, endMin }`
- Example: Only allow alerts between 9:00 AM – 6:00 PM

### 4. Health Check Support

- `/ping` endpoint returns simple status for clients to verify server is alive

---

## 🛠️ Tech Stack

- **Node.js**: runtime environment  
- **Express**: handles HTTP requests  
- **ws**: WebSocket communication  
- **cors**: CORS support for cross-origin requests  
- **JSON**: standard message format  

---

## 🚦 Running the Server

To start the server:

~~~bash
node server.js
~~~

- The server listens on port `3000` by default.
- You can edit `server.js` to change host or port.

---

## 🧾 Logs & Output

- Logs gesture input, alert triggers, and client connections
- Displays configured alert time window and minimum gesture interval

---

## 📡 API Documentation

### 🔄 WebSocket Message Types

| Type     | Format Example | Description |
|----------|----------------|-------------|
| `gesture` | `{ "type": "gesture", "data": "hand_open" }` | Gesture recognition result |  
| `alert`   | `{"type": "alert","data": { "sensor_id": "123", "value": 98 }, "timestamp": "2025-07-09T12:00:00Z"}` | Incoming alert data |
---

### 🌐 HTTP Endpoints

#### `POST /alert`

- **Usage:** Submit alert from embedded board
- **Body:** Any valid JSON object
- **Response:**
  - `200 OK`: Alert accepted or ignored based on time window
  - Body: `"Alert received"` or `"Outside alert time window. Ignored"`

#### `GET /ping`

- **Usage:** Health check endpoint
- **Response:** `"Server is alive"`

---

## 💬 Client Interaction Examples

### Set Alert Time Window (WebSocket message)

~~~json
{
  "type": "set_alert_time",
  "data": {
    "startHour": 9,
    "startMin": 0,
    "endHour": 17,
    "endMin": 30
  }
}
~~~

### Receive Gesture Broadcast

~~~json
{
  "type": "gesture",
  "data": "fist"
}
~~~

### Receive Alert Data

~~~json
{
  "type": "alert",
  "data": {
    "sensor": "gyro",
    "value": 123
  },
  "timestamp": "2025-07-09T12:34:56.789Z"
}
~~~

---

## ⚙️ Configurable Parameters

| Parameter                | Default      | Description                           |
|--------------------------|--------------|---------------------------------------|
| `MIN_BROADCAST_INTERVAL` | `800 ms`     | Minimum interval between gesture broadcasts |
| `alertTimeRange`         | `00:00-23:59`| Allowed time window for alert handling |

---

## ⚠️ Notes

- All clients share the latest gesture state
- New clients receive the last known gesture upon connection
- Time window settings are not persisted — you must implement persistence if needed
- Easily extensible to support additional message types (e.g. device status, heartbeats)

---

## 📬 Contact & Maintenance

For questions or issues, please contact the project maintainer or open an issue in the repository.
