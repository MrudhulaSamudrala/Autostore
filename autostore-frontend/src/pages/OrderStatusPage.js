import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

export default function OrderStatusPage() {
  const { orderId } = useParams();
  const [status, setStatus] = useState('pending');
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;
    if (orderId) {
      interval = setInterval(() => {
        axios.get(`http://localhost:8000/orders/`).then(res => {
          const order = res.data.find(o => o.order_id === Number(orderId));
          if (order) setStatus(order.status);
        }).catch(() => setError('Failed to fetch order status'));
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [orderId]);

  return (
    <div className="max-w-md mx-auto p-4 border rounded shadow">
      <h2 className="text-xl font-bold mb-2">Order Status</h2>
      <div className="mb-2">Order ID: <span className="font-semibold">{orderId}</span></div>
      <div className="mb-2">Status: <span className="font-semibold text-blue-600">{status}</span></div>
      {error && <div className="text-red-600 mt-2">{error}</div>}
    </div>
  );
} 