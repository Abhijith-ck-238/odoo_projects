import { useState, useCallback } from "react";
import { useSSE } from "../hooks/useSSE";

export default function ActivityFeed() {
    const [activities, setActivities] = useState([]);

    // Use useCallback to prevent unnecessary re-renders of the effect in useSSE
    const handleMessage = useCallback((data) => {
        setActivities((prev) => [data, ...prev].slice(0, 10)); // Keep last 10, newest first
    }, []);

    useSSE("http://localhost:3001/api/activity", handleMessage);

    return (
        <div className="card">
            <h2>Activity Feed (Custom Hook SSE)</h2>
            <div className="list">
                {activities.length === 0 && <p>Waiting for activities...</p>}
                {activities.map((activity) => (
                    <p key={activity.id} className="item activity">
                        {activity.text}
                    </p>
                ))}
            </div>
        </div>
    );
}
