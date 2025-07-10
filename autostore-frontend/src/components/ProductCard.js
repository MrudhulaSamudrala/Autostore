import React from 'react';
import { useCart } from '../contexts/CartContext';

export default function ProductCard({ product }) {
  const { cart, addToCart, removeFromCart } = useCart();
  const cartItem = cart.find(item => item.id === product.id);

  const handleIncrement = () => addToCart(product);
  const handleDecrement = () => {
    if (cartItem && cartItem.quantity > 1) {
      removeFromCart(product.id);
    } else {
      removeFromCart(product.id);
    }
  };

  return (
    <div className="p-4 border rounded-xl shadow-sm flex flex-col items-center bg-white relative">
      {product.sale && (
        <span className="absolute top-2 right-2 bg-pink-500 text-white text-xs px-2 py-1 rounded-full font-bold">SALE</span>
      )}
      <img
        src={product.image_url || 'https://via.placeholder.com/120'}
        alt={product.name || 'Product'}
        className="h-28 w-28 object-cover rounded mb-2"
      />
      <div className="text-xs text-gray-600 mb-1 flex items-center gap-1">
        <span className="inline-block bg-gray-100 px-2 py-0.5 rounded font-semibold">9 MINS</span>
      </div>
      <div className="font-semibold text-lg mb-1 text-center">{product.name || 'No Name'}</div>
      <div className="mb-2 text-gray-700 font-bold">
        ₹{product.price !== undefined ? product.price : 'N/A'}
      </div>
      {cartItem && cartItem.quantity > 0 ? (
        <div className="flex items-center border border-green-600 bg-white rounded overflow-hidden w-full max-w-[120px] justify-between">
          <button className="text-green-600 px-3 py-1 text-lg font-bold hover:bg-green-50" onClick={() => removeFromCart(product.id)}>-</button>
          <span className="font-semibold text-lg select-none">{cartItem.quantity}</span>
          <button className="text-green-600 px-3 py-1 text-lg font-bold hover:bg-green-50" onClick={handleIncrement}>+</button>
        </div>
      ) : (
        <button className="border border-green-600 text-green-600 bg-white rounded px-6 py-1 font-semibold w-full max-w-[120px] hover:bg-green-50" onClick={() => addToCart(product)}>
          ADD
        </button>
      )}
    </div>
  );
} 