import React, { useState } from 'react';
import { useCart } from '../contexts/CartContext';
import { FaTimes } from 'react-icons/fa';
import OrderConfirmationCard from './OrderConfirmationCard';

export default function CartDrawer({ open, onClose }) {
  const { cart, addToCart, removeFromCart, cartTotal, clearCart } = useCart();
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [orderInfo, setOrderInfo] = useState({ orderId: '', status: 'Picking' });
  if (!open && !showConfirmation) return null;

  // Bill details
  const itemsTotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const deliveryCharge = itemsTotal >= 100 ? 0 : 25;
  const handlingCharge = cart.length > 0 ? 2 : 0;
  const grandTotal = itemsTotal + deliveryCharge + handlingCharge;

  const handlePlaceOrder = async () => {
    // Prepare items array for new backend format
    const items = cart.map(item => ({ product_id: item.id, quantity: item.quantity }));
    try {
      const response = await fetch('http://localhost:8000/orders/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items })
      });
      const data = await response.json();
      setOrderInfo({ orderId: data.order_id, status: data.status });
      setShowConfirmation(true);
      clearCart();
    } catch (error) {
      alert('Failed to place order. Please try again.');
    }
  };

  return (
    <>
      {(open || showConfirmation) && (
        <div className="fixed inset-0 z-50 flex">
          <div className="flex-1 bg-black bg-opacity-40" onClick={onClose}></div>
          <div className="w-full max-w-md bg-white h-full shadow-lg flex flex-col relative">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h2 className="text-xl font-bold text-gray-800">My Cart</h2>
              <button onClick={onClose} className="text-gray-500 text-xl"><FaTimes /></button>
            </div>
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
              {cart.length === 0 ? (
                <div className="text-gray-500">Cart is empty.</div>
              ) : (
                cart.map(item => (
                  <div key={item.id} className="flex items-center bg-white rounded-lg shadow-sm p-3 gap-3">
                    <img src={item.image_url || item.img || 'https://via.placeholder.com/60'} alt={item.name || item.product_name} className="h-16 w-16 object-cover rounded" />
                    <div className="flex-1">
                      <div className="font-semibold text-gray-600 truncate w-60" title={item.name || item.product_name}>
                        {item.name || item.product_name}
                      </div>
                      <div className="font-bold text-gray-500">₹{item.price}</div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <div className="flex items-center border border-green-600 bg-white rounded overflow-hidden max-w-[100px]">
                        <button
                          className="text-green-600 px-2 py-1 text-lg font-bold hover:bg-green-50"
                          onClick={() => removeFromCart(item.id)}
                        >-</button>
                        <span className="font-semibold text-lg select-none px-2">{item.quantity}</span>
                        <button
                          className="text-green-600 px-2 py-1 text-lg font-bold hover:bg-green-50"
                          onClick={() => addToCart(item)}
                        >+</button>
                      </div>
                      <button className="text-gray-400 text-xs hover:text-pink-500" onClick={() => removeFromCart(item.id)}><FaTimes /></button>
                    </div>
                  </div>
                ))
              )}
            </div>
            {/* Bill details */}
            <div className="bg-blue-50 rounded-lg mx-4 my-4 p-4">
              <div className="font-bold text-gray-700 mb-2">Bill details</div>
              <div className="flex justify-between text-sm mb-1">
                <span>Items total</span>
                <span>₹{itemsTotal}</span>
              </div>
              <div className="flex justify-between text-sm mb-1">
                <span>Delivery charge <span className="inline-block align-middle" title="Free delivery for orders above ₹200">🛵</span></span>
                <span>{deliveryCharge === 0 ? <span className="line-through text-gray-400">₹25</span> : `₹${deliveryCharge}`} <span className="text-green-600 font-bold">{deliveryCharge === 0 ? 'FREE' : ''}</span></span>
              </div>
              <div className="flex justify-between text-sm mb-1">
                <span>Handling charge <span className="inline-block align-middle" title="Small handling fee">ℹ️</span></span>
                <span>₹{handlingCharge}</span>
              </div>
              <div className="flex justify-between font-bold text-base mt-2">
                <span>Grand total</span>
                <span>₹{grandTotal}</span>
              </div>
            </div>
            {/* Cancellation Policy */}
            <div className="bg-blue-50 rounded-lg mx-4 mb-4 p-4 text-xs text-gray-600">
              <div className="font-bold mb-1 text-gray-700">Cancellation Policy</div>
              Orders cannot be cancelled once packed for delivery. In case of unexpected delays, a refund will be provided, if applicable.
            </div>
            {/* Sticky bottom bar */}
            <div className="absolute bottom-0 left-0 w-full bg-white border-t p-4 flex items-center justify-between gap-2">
              <div className="font-bold text-green-700 text-lg">₹{grandTotal}<span className="block text-xs text-gray-500 font-normal">TOTAL</span></div>
              <button
                className="bg-green-600 text-white px-6 py-3 rounded font-bold text-base flex-1 hover:bg-green-700"
                onClick={handlePlaceOrder}
                disabled={cart.length === 0}
              >
                Login to Proceed &rarr;
              </button>
            </div>
          </div>
        </div>
      )}
      {showConfirmation && (
        <OrderConfirmationCard
          orderId={orderInfo.orderId}
          status={orderInfo.status}
          onClose={() => {
            setShowConfirmation(false);
            onClose();
          }}
        />
      )}
    </>
  );
} 