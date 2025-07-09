# 🌐 Nginx Configuration for Frontend Deployment & Proxy Services

This configuration file is used to deploy a frontend single-page application (SPA) on the server using Nginx. It provides static file hosting, reverse proxying, WebSocket support, and cache optimization.

---

## ✅ Key Features

- SPA routing support  
- Static asset caching control  
- Public access to video history directory  
- Reverse proxy for both HTTP and WebSocket connections to a local Node.js service (used for gesture recognition and alerting)

---

## ⚙️ Basic Configuration

~~~nginx
listen 80;
server_name `Your server IP`;
~~~

- Listens on port 80 (HTTP)
- Binds to the IP address or domain name 

---

## 🗂️ Static Site Hosting

~~~nginx
root /var/www/html/myapp;
index index.html;

location / {
    try_files $uri $uri/ /index.html;
}
~~~

- Sets the web root to `/var/www/html/myapp`
- Supports SPA routing by falling back to `index.html` for unmatched paths

---

## 🚀 Static Asset Optimization

### 1. Special handling for `/assets/`

~~~nginx
location /assets/ {
    try_files $uri =404;
    expires max;
    add_header Cache-Control "public";
}
~~~

- Prevents redirection for `/assets/`
- Enables long-term caching for rarely changing files

### 2. General static assets (JS, CSS, images, etc.)

~~~nginx
location ~ \.(js|css|png|jpg|gif|ico|svg)$ {
    try_files $uri =404;
    expires 1d;
    add_header Cache-Control "public";
}
~~~

- Sets a 1-day cache duration for common static file types
- Helps improve load performance and reduce server requests

---

## 🎥 Accessing Video History

~~~nginx
location /history/ {
    alias /var/mediamtx/recordings/history/;
    try_files $uri =404;
    expires max;
    add_header Cache-Control "public";
}
~~~

- Maps `/history/` to the local video recording directory
- Enables browser-based access to recorded video files  
  _Example: `/history/2025-07-09.mp4`_

---

## 🔁 Reverse Proxy for Alert Service

~~~nginx
location /alert/ {
    proxy_pass http://localhost:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
~~~

- Proxies requests to the local Node.js service at `localhost:3000`
- Supports both HTTP and WebSocket connections
- Adds headers to preserve original client information

---

## 📖 How to Use

### 🔗 Access URLs

| Function             | URL                                 |
|----------------------|--------------------------------------|
| Frontend Web Page    | `http://YOUR_SERVER_IP`                  |
| Video History        | `http://YOUR_SERVER_IP/history/`         |
| Alert HTTP API       | `POST http://YOUR_SERVER_IP/alert`       |
| WebSocket Alert Feed | `ws://YOUR_SERVER_IP/alert/`             |

---

## ⚠️ Notes

- Make sure `/var/www/html/myapp` exists and contains `index.html`
- Ensure video files are available under `/var/mediamtx/recordings/history/`
- The Node.js service must be running at `localhost:3000`
- For HTTPS support, configure an SSL certificate and listen on port `443`

---


