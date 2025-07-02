import React from 'react';

const mockOrders = [
  { id: 1, customer: 'Alice', product: 'Widget A', status: 'Picking', bot: 'Bot-1', time: '10:01' },
  { id: 2, customer: 'Bob', product: 'Widget B', status: 'Delivered', bot: 'Bot-2', time: '10:05' },
  { id: 3, customer: 'Charlie', product: 'Widget C', status: 'Queued', bot: 'Bot-3', time: '10:10' },
];

export default function LiveOrderTable() {
  return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <h2 className="text-xl font-bold mb-4 text-blue-700">Live Orders</h2>
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-blue-100 text-blue-700">
            <th className="py-2 px-3 text-left">Order ID</th>
            <th className="py-2 px-3 text-left">Customer</th>
            <th className="py-2 px-3 text-left">Product</th>
            <th className="py-2 px-3 text-left">Status</th>
            <th className="py-2 px-3 text-left">Bot</th>
            <th className="py-2 px-3 text-left">Time</th>
          </tr>
        </thead>
        <tbody>
          {mockOrders.map(order => (
            <tr key={order.id} className="border-b hover:bg-blue-50">
              <td className="py-2 px-3">{order.id}</td>
              <td className="py-2 px-3">{order.customer}</td>
              <td className="py-2 px-3">{order.product}</td>
              <td className="py-2 px-3">
                <span className={`px-2 py-1 rounded text-xs font-semibold ${order.status === 'Delivered' ? 'bg-green-100 text-green-700' : order.status === 'Picking' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'}`}>{order.status}</span>
              </td>
              <td className="py-2 px-3">{order.bot}</td>
              <td className="py-2 px-3">{order.time}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 