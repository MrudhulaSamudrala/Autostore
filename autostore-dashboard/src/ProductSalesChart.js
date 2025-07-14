import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

const COLORS = ["#10b981", "#3b82f6", "#f59e42", "#e11d48", "#6366f1", "#fbbf24", "#14b8a6", "#f472b6", "#a21caf", "#f43f5e"];

export default function ProductSalesChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('sales'); // 'sales' or 'inventory'
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('value-desc'); // 'name', 'value-desc', 'value-asc'

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/products/');
        if (!response.ok) throw new Error('Failed to fetch products');
        const products = await response.json();
        // Group products by name and sum the relevant metric
        const productData = products.reduce((acc, product) => {
          const name = product.name || 'Unknown Product';
          if (!acc[name]) {
            acc[name] = {
              product: name,
              sales: 0,
              inventory: 0
            };
          }
          acc[name].sales += (product.sale_count || 0);
          acc[name].inventory += (product.quantity || 0);
          return acc;
        }, {});
        const chartData = Object.values(productData);
        setData(chartData);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <h2 className="text-xl font-bold mb-4 text-blue-700">Product Analytics</h2>
      <div className="text-center py-8">Loading product data...</div>
    </div>
  );

  if (error) return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <h2 className="text-xl font-bold mb-4 text-blue-700">Product Analytics</h2>
      <div className="text-red-500 text-center py-8">Error: {error}</div>
    </div>
  );

  // Filter and map data for chart
  let filteredData = data
    .filter(item => item.product.toLowerCase().includes(search.toLowerCase()))
    .map(item => ({
      product: item.product,
      value: viewMode === 'sales' ? item.sales : item.inventory
    }));

  if (sortBy === 'name') {
    filteredData.sort((a, b) => a.product.localeCompare(b.product));
  } else if (sortBy === 'value-desc') {
    filteredData.sort((a, b) => b.value - a.value);
  } else if (sortBy === 'value-asc') {
    filteredData.sort((a, b) => a.value - b.value);
  }

  // Map each unique value to a color
  const uniqueValues = Array.from(new Set(filteredData.map(item => item.value))).sort((a, b) => a - b);
  const valueColorMap = new Map();
  uniqueValues.forEach((val, idx) => {
    valueColorMap.set(val, COLORS[idx % COLORS.length]);
  });

  return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-4 gap-2">
        <h2 className="text-xl font-bold text-blue-700">Product Analytics</h2>
        <div className="flex gap-2 items-center">
          <input
            type="text"
            placeholder="Search product..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
            style={{ minWidth: 180 }}
          />
          <select
            value={sortBy}
            onChange={e => setSortBy(e.target.value)}
            className="px-2 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="value-desc">Sort: High to Low</option>
            <option value="value-asc">Sort: Low to High</option>
            <option value="name">Sort: Name (A-Z)</option>
          </select>
          <button
            onClick={() => setViewMode('sales')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              viewMode === 'sales' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Quantities Sold
          </button>
          <button
            onClick={() => setViewMode('inventory')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              viewMode === 'inventory' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Current Inventory
          </button>
        </div>
      </div>
      {filteredData.length > 0 ? (
        <div className="w-full h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={filteredData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="product" />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [
                  value, 
                  viewMode === 'sales' ? 'Quantities Sold' : 'Current Inventory'
                ]}
              />
              <Bar 
                dataKey="value" 
                radius={[6, 6, 0, 0]}
              >
                {filteredData.map((entry, idx) => (
                  <Cell key={`cell-${entry.product}`} fill={valueColorMap.get(entry.value)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">No product data available</div>
      )}
      <div className="mt-4 text-sm text-gray-600">
        {viewMode === 'sales' ? (
          <p>Showing total quantities sold for each product</p>
        ) : (
          <p>Showing current inventory levels for each product</p>
        )}
      </div>
    </div>
  );
} 