import React from 'react';

const mockBins = [
  { id: 'Bin-1', product: 'Widget A', quantity: 20, location: 'A1' },
  { id: 'Bin-2', product: 'Widget B', quantity: 5, location: 'B2' },
  { id: 'Bin-3', product: 'Widget C', quantity: 0, location: 'C3' },
];

export default function BinInventoryTable() {
  return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <h2 className="text-xl font-bold mb-4 text-blue-700">Bin Inventory</h2>
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-blue-100 text-blue-700">
            <th className="py-2 px-3 text-left">Bin ID</th>
            <th className="py-2 px-3 text-left">Product</th>
            <th className="py-2 px-3 text-left">Quantity</th>
            <th className="py-2 px-3 text-left">Location</th>
          </tr>
        </thead>
        <tbody>
          {mockBins.map(bin => (
            <tr key={bin.id} className="border-b hover:bg-blue-50">
              <td className="py-2 px-3">{bin.id}</td>
              <td className="py-2 px-3">{bin.product}</td>
              <td className="py-2 px-3">
                <span className={`px-2 py-1 rounded text-xs font-semibold ${bin.quantity === 0 ? 'bg-red-100 text-red-700' : bin.quantity < 10 ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}`}>{bin.quantity}</span>
              </td>
              <td className="py-2 px-3">{bin.location}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 