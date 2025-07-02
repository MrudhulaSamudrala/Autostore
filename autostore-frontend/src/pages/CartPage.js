import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function CartPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const product = location.state?.product;
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const handlePlaceOrder = async () => {
    if (!product) return;
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post('http://localhost:8000/orders/', null, {
        params: {
          customer_name: 'Customer', // You can make this dynamic
          product_id: product.product_id,
        },
      });
      navigate(`/order-status/${res.data.order_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Order failed');
    } finally {
      setLoading(false);
    }
  };

  if (!product) return <div className="text-red-600">No product in cart.</div>;

  return (
    <div className="max-w-md mx-auto p-4 border rounded shadow">
      <h2 className="text-xl font-bold mb-2">Cart</h2>
      <div className="mb-2">Product: <span className="font-semibold">{product.product_name}</span></div>
      <div className="mb-4">Price: ${product.price}</div>
      <button
        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
        onClick={handlePlaceOrder}
        disabled={loading}
      >
        {loading ? 'Placing Order...' : 'Place Order'}
      </button>
      {error && <div className="text-red-600 mt-2">{error}</div>}
    </div>
  );
} 