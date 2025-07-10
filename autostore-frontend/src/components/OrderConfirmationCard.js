import React from 'react';

export default function OrderConfirmationCard({ orderId, status, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-sm w-full text-center">
        <h2 className="text-2xl font-bold mb-4 text-green-600">Order Placed Successfully!</h2>
        <div className="mb-2">
          <span className="font-semibold">Order ID:</span> {orderId}
        </div>
        <div className="mb-4">
          <span className="font-semibold">Status:</span> {status}
        </div>
        <button
          className="mt-4 px-6 py-2 bg-green-600 text-white rounded font-semibold hover:bg-green-700"
          onClick={onClose}
        >
          Close
        </button>
      </div>
    </div>
  );
} 