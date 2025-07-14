import React, { useEffect, useState, useRef } from "react";

export default function BotStatusPage() {
  const [bots, setBots] = useState([]);
  const [orders, setOrders] = useState([]);
  const wsRef = useRef(null);

  // Fetch initial bots and orders
  useEffect(() => {
    fetch("http://127.0.0.1:8000/bots/").then(res => res.json()).then(setBots);
    fetch("http://127.0.0.1:8000/orders/").then(res => res.json()).then(setOrders);
  }, []);

  // WebSocket for real-time bot updates
  useEffect(() => {
    wsRef.current = new WebSocket("ws://127.0.0.1:8000/ws/bots");
    wsRef.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.event === "bot_move") {
        setBots(prev =>
          prev.map(bot =>
            bot.id === msg.bot_id
              ? { ...bot, x: msg.x, y: msg.y, current_location_z: msg.z }
              : bot
          )
        );
      }
      if (msg.event === 'status_update' && msg.bot_id && msg.bot_status) {
        setBots(prev =>
          prev.map(bot =>
            bot.id === msg.bot_id
              ? { ...bot, status: msg.bot_status }
              : bot
          )
        );
      }
    };
    return () => wsRef.current && wsRef.current.close();
  }, []);

  // Helper to get order details for a bot
  const getOrderForBot = (bot) =>
    orders.find(order => order.id === bot.assigned_order_id);

  // Summary stats
  const totalBots = bots.length;
  const idleBots = bots.filter(b => b.status === "idle").length;
  const activeBots = bots.filter(b => b.status !== "idle").length;
  const assignedOrders = bots.filter(b => b.assigned_order_id).length;

  // Helper to render SVG path
  const renderPathSVG = (path) => {
    if (!path || path.length < 2) return null;
    // Scale for SVG
    const scale = 30;
    const offset = 10;
    const points = path.map(([x, y]) => `${x * scale + offset},${y * scale + offset}`).join(" ");
    return (
      <svg width={200} height={200} style={{ background: "#f8fafc", borderRadius: 8 }}>
        <polyline points={points} fill="none" stroke="#2563eb" strokeWidth={3} />
        {path.map(([x, y], i) => (
          <circle key={i} cx={x * scale + offset} cy={y * scale + offset} r={5} fill={i === 0 ? "#22c55e" : i === path.length - 1 ? "#f59e42" : "#2563eb"} />
        ))}
      </svg>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <h2 className="text-2xl font-bold mb-6 text-blue-700">Bot Status</h2>
      <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <div className="text-sm text-gray-600">Total Bots</div>
          <div className="text-2xl font-bold text-blue-600">{totalBots}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <div className="text-sm text-gray-600">Idle Bots</div>
          <div className="text-2xl font-bold text-green-600">{idleBots}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
          <div className="text-sm text-gray-600">Active Bots</div>
          <div className="text-2xl font-bold text-yellow-600">{activeBots}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <div className="text-sm text-gray-600">Assigned Orders</div>
          <div className="text-2xl font-bold text-purple-600">{assignedOrders}</div>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {bots.map(bot => {
          const order = getOrderForBot(bot);
          return (
            <div key={bot.id} className="bg-blue-50 rounded-lg shadow p-5 mb-4">
              <div className="flex items-center mb-2">
                <span className="text-2xl mr-2">🤖</span>
                <span className="font-bold text-lg text-blue-800">Bot #{bot.id}</span>
                <span className={`ml-3 px-2 py-1 rounded-full text-xs font-semibold ${bot.status === "idle" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>{bot.status}</span>
              </div>
              <div className="mb-2 text-gray-700 font-mono">
                <b>Coordinates:</b> ({bot.x}, {bot.y}, {bot.current_location_z})
              </div>
              <div className="mb-2">
                <b>Assigned Order:</b> {order ? (
                  <span className="ml-1 text-blue-700 font-semibold">#{order.id}</span>
                ) : <span className="ml-1 text-gray-500">None</span>}
              </div>
              {order && (
                <div className="bg-white rounded p-3 mb-2 border border-blue-100">
                  <div className="mb-1 text-sm"><b>Status:</b> <span className="text-pink-600 font-semibold">{order.status}</span></div>
                  <div className="mb-1 text-sm"><b>Items:</b> {order.items?.length || 0} products</div>
                  <div className="mb-1 text-xs text-gray-600">Order Items:
                    <ul className="ml-4 list-disc">
                      {order.items?.map((item, idx) => (
                        <li key={idx}>{item.name} (x{item.quantity})</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
              <div className="mb-2 text-sm text-gray-700">
                <b>Destination Bin:</b> {bot.destination_bin ? (
                  <span className="ml-1">({bot.destination_bin[0]}, {bot.destination_bin[1]}, {bot.destination_bin[2]})</span>
                ) : <span className="ml-1 text-gray-500">None</span>}
              </div>
              <div className="mb-2 text-sm text-gray-700">
                <b>Path:</b>
                {bot.path && bot.path.length > 0 ? (
                  <div className="my-2 flex flex-row items-center gap-1">
                    {bot.path.map((_, i) => (
                      <span key={i} style={{ color: '#2563eb', fontSize: '1.5em', lineHeight: 1 }}>●</span>
                    ))}
                  </div>
                ) : (
                  <span className="ml-1 text-gray-500">No path</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
} 