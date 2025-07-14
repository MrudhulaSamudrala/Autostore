import React, { useEffect, useState, useRef } from 'react';

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const wsRef = useRef(null);

  // Fetch orders from backend
  useEffect(() => {
    fetch('http://127.0.0.1:8000/orders/')
      .then(res => res.json())
      .then(data => setOrders(data));
  }, []);

  // Subscribe to /ws/orders for real-time status updates
  useEffect(() => {
    wsRef.current = new WebSocket('ws://127.0.0.1:8000/ws/orders');
    wsRef.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.event === 'status_update' && msg.order_id && msg.order_status) {
        setOrders(prev => prev.map(order =>
          order.id === msg.order_id ? { ...order, status: msg.order_status } : order
        ));
      }
    };
    return () => wsRef.current && wsRef.current.close();
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-xl font-bold mb-4">Orders</h2>
      <table className="min-w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th className="border px-2 py-1">Order ID</th>
            <th className="border px-2 py-1">Bot ID</th>
            <th className="border px-2 py-1">Items</th>
            <th className="border px-2 py-1">Status</th>
          </tr>
        </thead>
        <tbody>
          {orders.map(order => (
            <tr key={order.id}>
              <td className="border px-2 py-1">{order.id}</td>
              <td className="border px-2 py-1">{order.assigned_bot_id || '-'}</td>
              <td className="border px-2 py-1">
                <ul>
                  {order.items.map(item => (
                    <li key={item.product_id}>{item.name} x{item.quantity}</li>
                  ))}
                </ul>
              </td>
              <td className="border px-2 py-1">{order.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 