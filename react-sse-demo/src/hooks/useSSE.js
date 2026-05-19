import { useEffect, useRef } from "react";

export function useSSE(url, onMessage) {
    const eventSourceRef = useRef(null);

    useEffect(() => {
        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            onMessage(data);
        };

        eventSource.onerror = (error) => {
            console.error("SSE Error:", error);
            eventSource.close();
        };

        return () => {
            eventSource.close();
        };
    }, [url, onMessage]);
}
