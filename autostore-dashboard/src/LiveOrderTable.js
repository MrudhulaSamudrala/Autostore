import React, { useEffect, useState, useRef } from "react";

export default function LiveOrderTable() {
  const [orders, setOrders] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    fetchOrders();
    wsRef.current = new WebSocket("ws://127.0.0.1:8000/ws/orders");

    wsRef.current.onopen = () => {
      console.log('[WS] Connected to /ws/orders');
    };
    wsRef.current.onclose = (event) => {
      console.log('[WS] Disconnected from /ws/orders', event);
    };
    wsRef.current.onerror = (err) => {
      console.error('[WS] Error on /ws/orders:', err);
    };
    wsRef.current.onmessage = (event) => {
      console.log('[WS] Message from /ws/orders:', event.data);
      try {
        const msg = JSON.parse(event.data);
        if (msg.event === 'status_update' && msg.order_id && msg.order_status) {
          setOrders(prev => prev.map(order =>
            order.id === msg.order_id ? { ...order, status: msg.order_status } : order
          ));
        } else if (msg.event === 'orders_update' && Array.isArray(msg.orders)) {
          setOrders(msg.orders);
        } else {
          console.warn('[WS] Unknown message format:', msg);
        }
      } catch (e) {
        console.error('[WS] Failed to parse message:', event.data, e);
      }
    };
    return () => wsRef.current && wsRef.current.close();
  }, []);

  const DUMMY_ORDERS = Array.from({ length: 38 }, (_, i) => ({
    id: 1000 + i,
    status: 'packed',
    assigned_bot_id: Math.floor(Math.random() * 5) + 1,
    items: [
      { name: `Product ${String.fromCharCode(65 + (i % 26))}`, quantity: (i % 5) + 1 },
      ...(i % 3 === 0 ? [{ name: `Product ${String.fromCharCode(90 - (i % 26))}`, quantity: (i % 4) + 1 }] : [])
    ]
  }));

  const fetchOrders = async () => {
    const response = await fetch("http://127.0.0.1:8000/orders/");
    let data = [];
    try {
      data = await response.json();
    } catch {}
    if (!Array.isArray(data) || data.length === 0) {
      setOrders(DUMMY_ORDERS);
    } else {
      setOrders(data);
    }
  };

  // Add clear orders handler
  const handleClearOrders = async () => {
    if (!window.confirm("Are you sure you want to clear all order history? This cannot be undone.")) return;
    const resp = await fetch("http://127.0.0.1:8000/admin/clear_orders/", { method: "POST" });
    if (resp.ok) {
      await fetchOrders();
      alert("All orders have been cleared.");
    } else {
      alert("Failed to clear orders.");
    }
  };

  return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold mb-4 text-blue-700">Live Orders</h2>
        <button
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm font-semibold ml-4"
          onClick={handleClearOrders}
        >
          Clear Orders
        </button>
      </div>
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-blue-100 text-blue-700">
            <th className="py-2 px-3 text-left">Order ID</th>
            <th className="py-2 px-3 text-left">Status</th>
            <th className="py-2 px-3 text-left">Assigned Bot</th>
            <th className="py-2 px-3 text-left">Products</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <tr key={order.id} className="border-b hover:bg-blue-50">
              <td className="py-2 px-3">{order.id}</td>
              <td className="py-2 px-3">
                {order.status === "pending" && "Pending"}
                {order.status === "packing" && "Packing"}
                {order.status === "packed" && "Packed"}
              </td>
              <td className="py-2 px-3">
                {order.assigned_bot_id ? order.assigned_bot_id : "Not assigned"}
              </td>
              <td className="py-2 px-3">
                {order.items && order.items.length > 0 ? (
                  order.items.map(item => `${item.name.length > 12 ? item.name.slice(0, 12) + '...' : item.name} (x${item.quantity})`).join(', ')
                ) : (
                  <span className="text-gray-400">No items</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 