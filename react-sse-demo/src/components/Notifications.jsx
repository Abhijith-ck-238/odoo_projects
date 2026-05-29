import { useEffect, useState } from "react";

export default function Notifications() {
    const [notifications, setNotifications] = useState([]);

    useEffect(() => {
        // Note: In a real app, you might need the full URL if the proxy isn't set up.
        // For this demo, we'll use the full URL to ensure it works.
        const eventSource = new EventSource("http://localhost:3001/api/notifications");

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setNotifications((prev) => [data, ...prev].slice(0, 10)); // Keep last 10, newest first
        };

        eventSource.onerror = (error) => {
            console.error("SSE connection error:", error);
            eventSource.close();
        };

        return () => {
            eventSource.close();
        };
    }, []);

    return (
        <div className="card">
            <h2>Notifications (Basic SSE)</h2>
            <div className="list">
                {notifications.length === 0 && <p>Waiting for notifications...</p>}
                {notifications.map((item) => (
                    <p key={item.id} className="item notification">
                        {item.message}
                    </p>
                ))}
            </div>
        </div>
    );
}
