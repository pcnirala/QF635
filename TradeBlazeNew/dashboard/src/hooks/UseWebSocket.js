import {useEffect, useRef, useState} from "react";

export default function useWebSocket(url) {
    const [data, setData] = useState(null);
    const ws = useRef(null);

    useEffect(() => {
        ws.current = new WebSocket(url);
        ws.current.onmessage = (evt) => {
            setData(JSON.parse(evt.data));
        };
        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [url]);

    return data;
}
