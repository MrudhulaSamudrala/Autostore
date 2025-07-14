import React, { useEffect, useState, useRef } from 'react';

export default function BotGridView() {
  const [bots, setBots] = useState([]);
  const [orders, setOrders] = useState([]);
  const [bins, setBins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);
  const assignedOrderCountRef = useRef(0);
  const prevAssignedOrderIdsRef = useRef(new Set());

  // Function to fetch latest bot data
  const fetchLatestData = async () => {
    try {
      const [botsRes, ordersRes, binsRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/bots/'),
        fetch('http://127.0.0.1:8000/orders/'),
        fetch('http://127.0.0.1:8000/bins/')
      ]);
      
      if (!botsRes.ok) throw new Error('Failed to fetch bots');
      if (!ordersRes.ok) throw new Error('Failed to fetch orders');
      if (!binsRes.ok) throw new Error('Failed to fetch bins');
      
      const [botsData, ordersData, binsData] = await Promise.all([
        botsRes.json(),
        ordersRes.json(),
        binsRes.json()
      ]);
      
      setBots(botsData);
      setOrders(ordersData);
      setBins(binsData);
      // Track cumulative assigned orders
      const currentAssignedOrderIds = new Set(
        botsData
          .map(bot => bot.assigned_order_id)
          .filter(id => id !== null && id !== undefined)
      );
      // For each new assigned order id not seen before, increment the ref
      currentAssignedOrderIds.forEach(id => {
        if (!prevAssignedOrderIdsRef.current.has(id)) {
          assignedOrderCountRef.current += 1;
          prevAssignedOrderIdsRef.current.add(id);
        }
      });
      // Do not decrement or remove from the set, so the count only ever increases
      console.log('[REFRESH] Updated bots data:', botsData, 'Cumulative assigned orders:', assignedOrderCountRef.current);
    } catch (err) {
      console.error('[REFRESH] Error:', err);
      setError(err.message);
    }
  };

  useEffect(() => {
    // Initial data fetch
    fetchLatestData().finally(() => setLoading(false));

    // Set up periodic refresh every 3 seconds
    intervalRef.current = setInterval(() => {
      console.log('[AUTO REFRESH] Fetching latest data...');
      fetchLatestData();
    }, 3000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Helper function to get destination bin location with details
  const getDestinationBinLocation = (bot) => {
    if (bot.destination_bin && Array.isArray(bot.destination_bin)) {
      // destination_bin format: [x, y, z, bin_id]
      const x = bot.destination_bin[0];
      const y = bot.destination_bin[1];
      const z = bot.destination_bin[2] || 0;
      const binId = bot.destination_bin[3];
      
      if (binId) {
        // Find the bin details
        const bin = bins.find(b => b.id === binId);
        if (bin) {
          return `Bin ${binId} at (${x}, ${y}, ${z})`;
        } else {
          return `Bin ${binId} (${x}, ${y}, ${z})`;
        }
      } else {
        return `(${x}, ${y}, ${z})`;
      }
    }
    return 'None';
  };

  // Helper function to get current location
  const getCurrentLocation = (bot) => {
    return `(${bot.x}, ${bot.y}, ${bot.current_location_z || bot.z || 0})`;
  };

  if (loading) return <div className="text-center py-8">Loading bot data...</div>;
  if (error) return (
    <div className="text-center py-8">
      <div className="text-red-500 mb-4">Error: {error}</div>
      <button
        onClick={fetchLatestData}
        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
      >
        Retry
      </button>
    </div>
  );

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-blue-700">Bot Status</h2>
      
      {/* Control Buttons */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={fetchLatestData}
          className="inline-block px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
        >
          Refresh Bot Data
        </button>
      </div>
      
      {/* Bot Statistics */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <div className="text-sm text-gray-600">Total Bots</div>
          <div className="text-2xl font-bold text-green-600">{bots.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <div className="text-sm text-gray-600">Idle Bots</div>
          <div className="text-2xl font-bold text-blue-600">{bots.filter(bot => bot.status === 'idle').length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
          <div className="text-sm text-gray-600">Active Bots</div>
          <div className="text-2xl font-bold text-yellow-600">{bots.filter(bot => bot.status !== 'idle').length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <div className="text-sm text-gray-600">Assigned Orders</div>
          <div className="text-2xl font-bold text-purple-600">{assignedOrderCountRef.current}</div>
        </div>
      </div>
      
      {/* Bot Details Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bot ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Location</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Destination Bin Location</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned Order</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {bots.map(bot => {
              const assignedOrder = orders.find(order => order.id === bot.assigned_order_id);
              return (
                <tr key={bot.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    Bot #{bot.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      bot.status === 'idle' ? 'bg-green-100 text-green-800' :
                      bot.status === 'moving' ? 'bg-blue-100 text-blue-800' :
                      bot.status === 'packing' ? 'bg-yellow-100 text-yellow-800' :
                      bot.status === 'delivering' ? 'bg-purple-100 text-purple-800' :
                      bot.status === 'carrying' ? 'bg-orange-100 text-orange-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {['idle','moving','packing','delivering','carrying','returning'].includes(bot.status) ? bot.status : 'Unknown'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                    {getCurrentLocation(bot)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                    {getDestinationBinLocation(bot)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {assignedOrder ? `Order #${assignedOrder.id}` : 'None'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
} 