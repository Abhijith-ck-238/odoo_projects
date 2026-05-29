const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// --- SSE Endpoint for Notifications ---
app.get('/api/notifications', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    console.log('[SSE] Notifications client connected');

    const sendNotification = () => {
        const data = JSON.stringify({
            id: Date.now(),
            message: `Notification at ${new Date().toLocaleTimeString()}`
        });
        res.write(`data: ${data}\n\n`);
    };

    // Send initial notification
    sendNotification();

    // Send random notifications every 5 seconds
    const intervalId = setInterval(sendNotification, 5000);

    req.on('close', () => {
        console.log('[SSE] Notifications client disconnected');
        clearInterval(intervalId);
    });
});

// --- SSE Endpoint for Activity Feed ---
app.get('/api/activity', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    console.log('[SSE] Activity client connected');

    const activities = [
        "User logged in",
        "New post created",
        "Profile updated",
        "Comment added",
        "Photo uploaded"
    ];

    const sendActivity = () => {
        const randomIndex = Math.floor(Math.random() * activities.length);
        const data = JSON.stringify({
            id: Date.now(),
            text: `${activities[randomIndex]} at ${new Date().toLocaleTimeString()}`
        });
        res.write(`data: ${data}\n\n`);
    };

    // Send initial activity
    sendActivity();

    // Send activity updates every 3 seconds
    const intervalId = setInterval(sendActivity, 3000);

    req.on('close', () => {
        console.log('[SSE] Activity client disconnected');
        clearInterval(intervalId);
    });
});

app.listen(PORT, () => {
    console.log(`SSE Server running at http://localhost:${PORT}`);
});
