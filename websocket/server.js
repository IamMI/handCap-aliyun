const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let clients = [];

// ======================
// 报警时间段控制
// ======================
let alertTimeRange = { startHour: 0, startMin: 0, endHour: 23, endMin: 59 };

function isWithinAlertTime() {
    const now = new Date();
    const hour = now.getHours();
    const minute = now.getMinutes();

    const startTotal = alertTimeRange.startHour * 60 + alertTimeRange.startMin;
    const endTotal = alertTimeRange.endHour * 60 + alertTimeRange.endMin;
    const nowTotal = hour * 60 + minute;

    return nowTotal >= startTotal && nowTotal < endTotal;
}

// ==============================
// 记录最后广播的手势
// ==============================
let latestGesture = null; // 存储最后广播的手势
const MIN_BROADCAST_INTERVAL = 800; // 防止太频繁广播，单位：毫秒
let lastBroadcastTime = 0;

// ==============================
// 广播手势指令函数
// ==============================
function broadcastGesture(gestureName) {
    const now = Date.now();

    if (gestureName === latestGesture && now - lastBroadcastTime < MIN_BROADCAST_INTERVAL) {
        // 手势未变且时间间隔过短，忽略
        return;
    }

    latestGesture = gestureName;
    lastBroadcastTime = now;

    console.log(`[Gesture] 广播手势指令: ${gestureName}`);

    clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({
                type: 'gesture',
                data: gestureName
            }));
        }
    });
}

// ==============================
// 处理客户端连接
// ==============================
wss.on('connection', (ws) => {
    console.log('[WS] 新客户端连接');

    // 如果已经有最新手势，就主动推送一次
    if (latestGesture) {
        ws.send(JSON.stringify({
            type: 'gesture',
            data: latestGesture
        }));
    }

    clients.push(ws);

    ws.on('message', (message) => {
        try {
            const msg = JSON.parse(message.toString());

            // 处理设置报警时间消息
            if (msg.type === 'set_alert_time') {
                const { startHour, startMin, endHour, endMin } = msg.data;

                alertTimeRange.startHour = parseInt(startHour);
                alertTimeRange.startMin = parseInt(startMin);
                alertTimeRange.endHour = parseInt(endHour);
                alertTimeRange.endMin = parseInt(endMin);

                console.log(`[WS] 报警时间段更新为 ${startHour}:${startMin} - ${endHour}:${endMin}`);
            }

            // 转发手势指令
            if (msg.type === 'gesture') {
                broadcastGesture(msg.data);
            }

        } catch (e) {
            console.error('消息解析失败:', e);
        }
    });

    ws.on('close', () => {
        clients = clients.filter(c => c !== ws);
    });
});

// 接收来自开发板的 HTTP POST 报警
app.post('/alert', (req, res) => {
    const alertData = req.body;

    if (!isWithinAlertTime()) {
        return res.status(200).send('非报警时间段，已忽略');
    }

    console.log('[ALERT] 收到报警:', alertData);

    clients.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'alert',
                data: alertData,
                timestamp: new Date().toISOString()
            }));
        }
    });

    res.status(200).send('已接收报警');
});

app.get('/ping', (req, res) => {
    res.send('服务正常');
});

server.listen(3000, '0.0.0.0', () => {
    console.log('WebSocket 服务运行在 ws://0.0.0.0:3000');
});