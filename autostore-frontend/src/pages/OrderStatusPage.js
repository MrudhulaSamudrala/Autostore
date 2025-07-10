import React, { useState } from 'react';

function PlaceOrder({ selectedProductIds }) {
  const [orderInfo, setOrderInfo] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handlePlaceOrder = async () => {
    setError(null);
    setOrderInfo(null);
    setSuccess(false);
    try {
      const response = await fetch("http://localhost:8000/orders/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_ids: selectedProductIds }),
      });
      if (!response.ok) {
        throw new Error("Order failed");
      }
      const data = await response.json();
      setOrderInfo(data);
      setSuccess(true);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <button onClick={handlePlaceOrder}>Place Order</button>
      {success && orderInfo && (
        <div className="mt-2 p-2 border rounded bg-green-50">
          <div>Order placed!</div>
          <div>Order ID: {orderInfo.order_id}</div>
          <div>Status: {orderInfo.status}</div>
          <div>
            Assigned Bot: {orderInfo.assigned_bot_id ? orderInfo.assigned_bot_id : "Not assigned yet"}
          </div>
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