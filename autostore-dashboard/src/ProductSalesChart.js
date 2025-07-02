import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const mockData = [
  { product: 'Widget A', sales: 120 },
  { product: 'Widget B', sales: 80 },
  { product: 'Widget C', sales: 45 },
];

export default function ProductSalesChart() {
  return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <h2 className="text-xl font-bold mb-4 text-blue-700">Product Sales Chart</h2>
      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={mockData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="product" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="sales" fill="#2563eb" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
} 