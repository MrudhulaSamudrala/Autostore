import React from 'react';
import { useCart } from '../contexts/CartContext';

export default function ProductCard({ product }) {
  const { cart, addToCart, removeFromCart } = useCart();
  const cartItem = cart.find(item => item.product_id === product.product_id);

  const handleIncrement = () => {
    addToCart(product);
  };

  const handleDecrement = () => {
    if (cartItem && cartItem.quantity > 1) {
      // Decrement quantity by removing and re-adding with quantity - 1
      removeFromCart(product.product_id);
      for (let i = 0; i < cartItem.quantity - 1; i++) {
        addToCart(product);
      }
    } else {
      removeFromCart(product.product_id);
    }
  };

  return (
    <div className="p-4 border rounded-xl shadow-sm flex flex-col items-center bg-white relative">
      {product.sale && (
        <span className="absolute top-2 right-2 bg-pink-500 text-white text-xs px-2 py-1 rounded-full font-bold">SALE</span>
      )}
      <img
        src={product.img || 'https://via.placeholder.com/120'}
        alt={product.product_name}
        className="h-28 w-28 object-cover rounded mb-2"
      />
      <div className="text-xs text-gray-600 mb-1 flex items-center gap-1">
        <span className="inline-block bg-gray-100 px-2 py-0.5 rounded font-semibold">9 MINS</span>
      </div>
      <div className="font-semibold text-lg mb-1 text-center">{product.product_name}</div>
      <div className="text-gray-500 text-sm mb-1">200 g</div>
      <div className="mb-2 text-gray-700 font-bold">₹{product.price}</div>
      {cartItem ? (
        <div className="flex items-center border border-green-600 bg-white rounded overflow-hidden w-full max-w-[120px] justify-between">
          <button
            className="text-green-600 px-3 py-1 text-lg font-bold hover:bg-green-50"
            onClick={handleDecrement}
          >
            -
          </button>
          <span className="font-semibold text-lg select-none">{cartItem.quantity}</span>
          <button
            className="text-green-600 px-3 py-1 text-lg font-bold hover:bg-green-50"
            onClick={handleIncrement}
          >
            +
          </button>
        </div>
      ) : (
        <button
          className="border border-green-600 text-green-600 bg-white rounded px-6 py-1 font-semibold w-full max-w-[120px] hover:bg-green-50"
          onClick={() => addToCart(product)}
        >
          ADD
        </button>
      )}
    </div>
  );
} 