import React, { useState, useEffect, useRef } from 'react';

function PlaceOrder({ selectedProductIds }) {
  const [orderInfo, setOrderInfo] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [polling, setPolling] = useState(false);
  const pollingRef = useRef(null);
  const wsRef = useRef(null);

  const handlePlaceOrder = async () => {
    setError(null);
    setOrderInfo(null);
    setSuccess(false);
    setPolling(false);
    try {
      const response = await fetch("http://127.0.0.1:8000/orders/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: selectedProductIds.map(id => ({ product_id: id, quantity: 1 })) }),
      });
      if (!response.ok) {
        throw new Error("Order failed");
      }
      const data = await response.json();
      setOrderInfo(data);
      setSuccess(true);
      setPolling(true);
    } catch (err) {
      setError(err.message);
    }
  };

  // WebSocket for real-time order status updates
  useEffect(() => {
    if (orderInfo && orderInfo.order_id) {
      wsRef.current = new window.WebSocket("ws://127.0.0.1:8000/ws/orders");
      wsRef.current.onopen = () => {
        // Optionally send a ping or handshake
      };
      wsRef.current.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.event === "status_update" && msg.order_id === orderInfo.order_id && msg.order_status) {
            setOrderInfo(prev => ({ ...prev, status: msg.order_status }));
            if (msg.order_status === 'packed') {
              setPolling(false);
              clearInterval(pollingRef.current);
              wsRef.current && wsRef.current.close();
            }
          }
        } catch (e) {
          // Ignore parse errors
        }
      };
      wsRef.current.onerror = () => {
        // Optionally handle errors
      };
      wsRef.current.onclose = () => {
        // Optionally handle close
      };
      return () => {
        wsRef.current && wsRef.current.close();
      };
    }
  }, [orderInfo && orderInfo.order_id]);

  // Poll for order status every 1 second after placing order (fallback)
  useEffect(() => {
    if (polling && orderInfo && orderInfo.order_id) {
      pollingRef.current = setInterval(async () => {
        try {
          const res = await fetch("http://127.0.0.1:8000/orders/");
          if (!res.ok) return;
          const orders = await res.json();
          const thisOrder = orders.find(o => o.id === orderInfo.order_id);
          if (thisOrder) {
            setOrderInfo(prev => ({ ...prev, status: thisOrder.status, assigned_bot_id: thisOrder.assigned_bot_id }));
            if (thisOrder.status === 'packed') {
              setPolling(false);
              clearInterval(pollingRef.current);
              wsRef.current && wsRef.current.close();
            }
          }
        } catch (e) {
          // ignore polling errors
        }
      }, 1000);
      return () => clearInterval(pollingRef.current);
    }
  }, [polling, orderInfo]);

  return (
    <div>
      <button onClick={handlePlaceOrder}>Place Order</button>
      {success && orderInfo && (
        <div className="mt-2 p-2 border rounded bg-green-50">
          <div>Order placed!</div>
          <div>Order ID: {orderInfo.order_id}</div>
          <div>Status: <span className={orderInfo.status === 'packed' ? 'text-green-600' : 'text-yellow-600'}>{orderInfo.status === 'ready' ? 'packing' : orderInfo.status}</span></div>
          <div>
            Assigned Bot: {orderInfo.assigned_bot_id ? orderInfo.assigned_bot_id : "Not assigned yet"}
          </div>
          {orderInfo.status !== 'packed' && <div className="animate-pulse text-blue-500">Processing...</div>}
        </div>
      )}
      {error && <div className="text-red-500">{error}</div>}
    </div>
  );
}

export default function OrderStatusPage() {
  // Replace with actual selected product IDs from your cart or selection logic
  const selectedProductIds = [1, 2];
  return (
    <div className="max-w-md mx-auto p-4 border rounded shadow">
      <h2 className="text-xl font-bold mb-2">Place an Order</h2>
      <PlaceOrder selectedProductIds={selectedProductIds} />
    </div>
  );
} 