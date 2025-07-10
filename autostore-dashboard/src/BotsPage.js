import React, { useEffect, useState } from 'react';
import Bot3DVisualizer from './Bot3DVisualizer';

function BotPathPreview({ path }) {
  return (
    <svg width={60} height={60}>
      {path.map((p, i) =>
        <circle key={i} cx={p[0]*10+10} cy={p[1]*10+10} r={3} fill="blue" />
      )}
      {path.length > 1 && path.map((p, i) =>
        i < path.length-1
          ? <line key={i} x1={p[0]*10+10} y1={p[1]*10+10} x2={path[i+1][0]*10+10} y2={path[i+1][1]*10+10} stroke="gray" />
          : null
      )}
    </svg>
  );
}

export default function BotsPage() {
  const [bots, setBots] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/bots')
      .then(res => res.json())
      .then(setBots);
    // const ws = new window.WebSocket('ws://localhost:8000/ws/bots');
    // ws.onmessage = (event) => setBots(JSON.parse(event.data));
    // return () => ws.close();
  }, []);

  // Debug log to confirm BotsPage is rendering
  console.log('Rendering BotsPage with bots:', bots);

  return (
    <div>
      <h2>Bots</h2>
      <a
        href="/autostore_claude.html"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: 'inline-block',
          margin: '12px 0 24px 0',
          color: '#2196f3',
          fontWeight: 600,
          textDecoration: 'underline',
          fontSize: 16
        }}
      >
        Open 3D Visualization (Legacy)
      </a>
      <table>
        <thead>
          <tr>
            <th>Bot ID</th>
            <th>Status</th>
            <th>Coordinates</th>
            <th>Assigned Order</th>
            <th>Destination Bin</th>
            <th>Path</th>
          </tr>
        </thead>
        <tbody>
          {bots.map(bot => (
            <tr key={bot.id}>
              <td>{bot.id}</td>
              <td>{bot.status}</td>
              <td>({bot.x}, {bot.y}, {bot.z})</td>
              <td>{bot.assigned_order_id || '-'}</td>
              <td>{bot.destination_bin ? `(${bot.destination_bin.join(', ')})` : '-'}</td>
              <td><BotPathPreview path={bot.path || []} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 