import React, { useEffect, useState } from "react";

export default function LiveOrderTable() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetchOrders();
    // Optionally, poll every few seconds for updates:
    // const interval = setInterval(fetchOrders, 2000);
    // return () => clearInterval(interval);
  }, []);

  const fetchOrders = async () => {
    const response = await fetch("http://localhost:8000/orders/");
    const data = await response.json();
    setOrders(data);
  };

  return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <h2 className="text-xl font-bold mb-4 text-blue-700">Live Orders</h2>
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
              <td className="py-2 px-3">{order.status}</td>
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