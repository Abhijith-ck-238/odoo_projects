const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Mock data storage
let notifications = [
    { id: 1, message: "Welcome to the Polling Demo!" },
    { id: 2, message: "This is a short polling test." }
];

let messages = [
    { text: "Hello! This is long polling." }
];

// For long polling waiting list
let messageWaiters = [];

// --- Short Polling Endpoints ---

// Get notifications
app.get('/api/notifications', (req, res) => {
    console.log('[Short Polling] Fetching notifications...');
    res.json(notifications);
});

// Trigger a new notification
app.post('/api/trigger-notification', (req, res) => {
    const newNotification = {
        id: Date.now(),
        message: req.body.message || `New Alert at ${new Date().toLocaleTimeString()}`
    };
    notifications.push(newNotification);
    // Keep only last 10
    if (notifications.length > 10) notifications.shift();
    res.status(201).json(newNotification);
});

// --- Long Polling Endpoints ---

// Subscribe to messages (Long Polling)
app.get('/api/messages/subscribe', (req, res) => {
    console.log('[Long Polling] New subscriber waiting...');

    // Create a promise that resolves when a new message is available
    const waitForMessage = new Promise((resolve) => {
        messageWaiters.push(resolve);
    });

    // Timeout after 30 seconds to avoid hanging forever
    const timeoutId = setTimeout(() => {
        const index = messageWaiters.indexOf(waitForMessage);
        if (index !== -1) {
            messageWaiters.splice(index, 1);
            res.status(204).end(); // No Content (re-poll)
        }
    }, 30000);

    waitForMessage.then((msg) => {
        clearTimeout(timeoutId);
        res.json(msg);
    });
});

// Trigger a new message
app.post('/api/trigger-message', (req, res) => {
    const newMessage = {
        text: req.body.text || `Live update: ${new Date().toLocaleTimeString()}`
    };
    messages.push(newMessage);

    console.log(`[Long Polling] Notifying ${messageWaiters.length} waiters...`);

    // Notify all waiters
    const currentWaiters = [...messageWaiters];
    messageWaiters = [];
    currentWaiters.forEach(resolve => resolve(newMessage));

    res.status(201).json({ status: 'sent' });
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
