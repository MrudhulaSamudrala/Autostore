import React, { useEffect, useState } from 'react';
import { FaRobot } from 'react-icons/fa';

const gridSize = 10;
const mockBots = [
  { id: 'Bot-1', x: 2, y: 3, status: 'idle' },
  { id: 'Bot-2', x: 5, y: 7, status: 'busy' },
  { id: 'Bot-3', x: 8, y: 1, status: 'charging' },
];

function statusColorClass(status) {
  switch (status?.toLowerCase()) {
    case 'idle': return 'bg-green-100 text-green-700';
    case 'busy': return 'bg-yellow-100 text-yellow-700';
    case 'charging': return 'bg-blue-100 text-blue-700';
    case 'moving': return 'bg-purple-100 text-purple-700';
    case 'packing': return 'bg-pink-100 text-pink-700';
    default: return 'bg-gray-100 text-gray-700';
  }
}

function BotPathPreview({ path }) {
  return (
    <svg width={80} height={40}>
      {path.map((p, i) =>
        <circle key={i} cx={p[0]*10+10} cy={p[1]*10+10} r={4} fill="#6366f1" />
      )}
      {path.length > 1 && path.map((p, i) =>
        i < path.length-1
          ? <line key={i} x1={p[0]*10+10} y1={p[1]*10+10} x2={path[i+1][0]*10+10} y2={path[i+1][1]*10+10} stroke="#6366f1" strokeWidth={2} />
          : null
      )}
    </svg>
  );
}

function getOrderDetails(orderId, orders) {
  return orders.find(order => order.id === orderId);
}

export default function BotGridView() {
  const [bots, setBots] = useState([]);
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    // Fetch bots
    fetch('http://localhost:8000/bots')
      .then(res => res.json())
      .then(setBots);

    // Fetch orders for order details
    fetch('http://localhost:8000/orders/')
      .then(res => res.json())
      .then(setOrders);

    // const ws = new window.WebSocket('ws://localhost:8000/ws/bots');
    // ws.onmessage = (event) => setBots(JSON.parse(event.data));
    // return () => ws.close();
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-blue-700">Bot Status</h2>
      
      {/* Bot Statistics */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <div className="text-sm text-gray-600">Total Bots</div>
          <div className="text-2xl font-bold text-green-600">{bots.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <div className="text-sm text-gray-600">Idle Bots</div>
          <div className="text-2xl font-bold text-blue-600">{bots.filter(bot => bot.status === 'idle').length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
          <div className="text-sm text-gray-600">Active Bots</div>
          <div className="text-2xl font-bold text-yellow-600">{bots.filter(bot => bot.status !== 'idle').length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <div className="text-sm text-gray-600">Assigned Orders</div>
          <div className="text-2xl font-bold text-purple-600">{bots.filter(bot => bot.assigned_order_id).length}</div>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-6 justify-start">
        {bots.map(bot => (
          <div
            key={bot.id}
            className="bg-white rounded-2xl shadow-lg p-6 min-w-[260px] max-w-xs transition-transform hover:scale-105 border-2 border-blue-100"
            style={{ boxShadow: '0 4px 24px 0 rgba(99,102,241,0.08)' }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="bg-blue-100 rounded-full p-2">
                <FaRobot className="text-2xl text-blue-500" />
              </div>
              <span className="text-lg font-bold text-blue-700">Bot #{bot.id}</span>
            </div>
            <div className="flex items-center gap-2 mb-2">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColorClass(bot.status)}`}>{bot.status}</span>
            </div>
            <div className="mb-1 text-gray-700"><b>Coordinates:</b> <span className="font-mono">({bot.x}, {bot.y}, {bot.z})</span></div>
            
            {/* Assigned Order Details */}
            {bot.assigned_order_id ? (
              <div className="mb-3 p-2 bg-blue-50 rounded border border-blue-200">
                <div className="mb-1 text-gray-700">
                  <b>Assigned Order:</b> <span className="font-mono text-blue-600">#{bot.assigned_order_id}</span>
                </div>
                {(() => {
                  const orderDetails = getOrderDetails(bot.assigned_order_id, orders);
                  return orderDetails ? (
                    <div className="text-xs text-gray-600">
                      <div><b>Status:</b> <span className={`px-1 py-0.5 rounded text-xs ${statusColorClass(orderDetails.status)}`}>{orderDetails.status}</span></div>
                      <div><b>Items:</b> {orderDetails.items?.length || 0} products</div>
                      {orderDetails.items && orderDetails.items.length > 0 && (
                        <div className="mt-1">
                          <div className="font-semibold text-xs text-gray-700">Order Items:</div>
                          {orderDetails.items.slice(0, 2).map((item, idx) => (
                            <div key={idx} className="text-xs text-gray-600 truncate">
                              • {item.name?.substring(0, 20)}... (x{item.quantity})
                            </div>
                          ))}
                          {orderDetails.items.length > 2 && (
                            <div className="text-xs text-gray-500">+{orderDetails.items.length - 2} more items</div>
                          )}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-xs text-gray-500">Loading order details...</div>
                  );
                })()}
              </div>
            ) : (
              <div className="mb-1 text-gray-700"><b>Assigned Order:</b> <span className="text-gray-400">None</span></div>
            )}
            
            <div className="mb-1 text-gray-700"><b>Destination Bin:</b> <span className="font-mono">{bot.destination_bin ? `(${bot.destination_bin.join(', ')})` : '-'}</span></div>
            <div className="mb-1 text-gray-700"><b>Path:</b> <BotPathPreview path={bot.path || []} /></div>
          </div>
        ))}
      </div>
    </div>
  );
} 