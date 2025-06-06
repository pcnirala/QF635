import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

const ws = new WebSocket("ws://localhost:8000/ws/ticks");

function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      setData(prev => [...prev.slice(-29), msg]); // keep last 30
    };
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Live Tick Prices</h2>
      <LineChart width={600} height={300} data={data}>
        <XAxis dataKey="time" />
        <YAxis domain={['auto', 'auto']} />
        <Tooltip />
        <Line type="monotone" dataKey="price" stroke="#1976d2" strokeWidth={2}/>
      </LineChart>
    </div>
  );
}

export default App;
