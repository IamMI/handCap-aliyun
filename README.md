# Hand Capture base on Server

## Basic information
We suggest you to create an *Aliyun server* account and do

- Expose server's IP to access on Internet
- Open certain ports to accept stream and alert
- Make sure your server have configurate **Nginx** and **websocket**
- After finish three steps before, go into `scripts/` and run
    ```bash
    python gesture_cap.py
    ```

## Nginx config
Your could visit [**Nginx**'s web](https://nginx.org/en/) to know more info about it.

- Run the followed code to install and config.
    ```bash
    sudo apt-get install certbot python3-certbot-nginx
    sudo certbot --nginx -d yourdomain.com
    ```

- Place `app.txt` at `/etc/nginx/sites-available/`. Run
    ```bash
    sudo systemctl restart nginx
    ```
    to start **Nginx**.


## Websocket config
You should place `server.js` at `/opt/alert-server`, run
```bash
node server.js
```

## Scripts
Anytime when server received a video stream, it would:
- Using **Mediapipe** to extract keypoints of hands.
- Using **LinearSVC** to classify gesture.
- Select the most confident gesture to report.

