import React, { useState, useEffect, useRef } from 'react';
import { FaBox, FaLock, FaUnlock, FaClock, FaCheckCircle } from 'react-icons/fa';

export default function BinInventoryTable() {
  const [bins, setBins] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showRefillModal, setShowRefillModal] = useState(false);
  const [selectedBinId, setSelectedBinId] = useState(null);
  const [refillLoading, setRefillLoading] = useState(false);
  const [refillQuantities, setRefillQuantities] = useState({});
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [detailsBinId, setDetailsBinId] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    // Fetch bins and products data
    const fetchData = () => {
      Promise.all([
        fetch('http://127.0.0.1:8000/bins/').then(res => res.json()),
        fetch('http://127.0.0.1:8000/products/').then(res => res.json())
      ])
      .then(([binsData, productsData]) => {
        setBins(binsData); // Always fully replace bins state
        console.log('[DEBUG] Polled bins:', binsData); // Debug log after polling
        setProducts(productsData);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
        setLoading(false);
      });
    };
    fetchData();
    const interval = setInterval(fetchData, 3000); // Poll every 3 seconds

    wsRef.current = new WebSocket('ws://127.0.0.1:8000/ws/bots');
    wsRef.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.event === 'status_update' && msg.bin_id && msg.bin_status) {
        setBins(prev => prev.map(bin =>
          bin.id === msg.bin_id ? { ...bin, status: msg.bin_status } : bin
        ));
      }
    };
    
    // Add WebSocket for orders to refresh product data when orders are completed
    const ordersWsRef = new WebSocket('ws://127.0.0.1:8000/ws/orders');
    ordersWsRef.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.event === 'status_update' && msg.order_id && msg.order_status === 'packed') {
          // Refresh product data when an order is completed
          fetch('http://127.0.0.1:8000/products/').then(res => res.json()).then(setProducts);
          console.log('[WS] Order completed, refreshing product data');
        }
      } catch (e) {
        console.error('[WS] Failed to parse orders message:', event.data, e);
      }
    };
    
    return () => {
      wsRef.current && wsRef.current.close();
      ordersWsRef && ordersWsRef.close();
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    console.log('Bin data:', bins);
  }, [bins]);

  // Helper function to get products for a bin
  const getProductsForBin = (binId) => {
    return products.filter(product => product.bin_id === binId);
  };

  // Helper function to format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Handler for refill button
  const handleRefillBin = (binId) => {
    setSelectedBinId(binId);
    // Set default quantity 1 for each product in the bin
    const binProducts = getProductsForBin(binId);
    const initialQuantities = {};
    binProducts.forEach(p => { initialQuantities[p.id] = 1; });
    setRefillQuantities(initialQuantities);
    setShowRefillModal(true);
  };

  // Handler for quantity change
  const handleQuantityChange = (productId, delta) => {
    setRefillQuantities(q => {
      const newQ = { ...q };
      newQ[productId] = Math.max(1, (newQ[productId] || 1) + delta);
      return newQ;
    });
  };

  // Handler for refill submission
  const handleRefillSubmit = async () => {
    if (!selectedBinId) return;
    setRefillLoading(true);
    try {
      // Prepare payload: send quantity for each product in the bin
      const binProducts = getProductsForBin(selectedBinId);
      const refillPayload = binProducts.map(product => ({
        bin_id: selectedBinId,
        product_id: product.id,
        quantity: refillQuantities[product.id] || 1
      }));
      const response = await fetch('http://127.0.0.1:8000/products/refill-multiple', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(refillPayload)
      });
      if (response.ok) {
        const result = await response.json();
        alert(`Successfully refilled Bin ${selectedBinId}`);
        // Refresh the data
        Promise.all([
          fetch('http://127.0.0.1:8000/bins/').then(res => res.json()),
          fetch('http://127.0.0.1:8000/products/').then(res => res.json())
        ]).then(([binsData, productsData]) => {
          setBins(binsData);
          setProducts(productsData);
          setShowRefillModal(false);
          setSelectedBinId(null);
        });
      } else {
        const error = await response.json();
        alert(`Failed to refill bin: ${error.detail}`);
      }
    } catch (error) {
      alert('Error refilling bin: ' + error.message);
    } finally {
      setRefillLoading(false);
    }
  };

  // Handler for show details
  const handleShowDetails = (binId) => {
    fetch('http://127.0.0.1:8000/products/')
      .then(res => res.json())
      .then(productsData => {
        setProducts(productsData);
        setDetailsBinId(binId);
        setShowDetailsModal(true);
      });
  };

  // Handler for resetting all bins
  const handleResetBins = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/admin/reset_bins/', { method: 'POST' });
      const result = await response.json();
      alert(result.message || 'Bins reset!');
      // Refresh the data immediately
      Promise.all([
        fetch('http://127.0.0.1:8000/bins/').then(res => res.json()),
        fetch('http://127.0.0.1:8000/products/').then(res => res.json())
      ]).then(([binsData, productsData]) => {
        setBins(binsData);
        setProducts(productsData);
      });
    } catch (error) {
      alert('Failed to reset bins: ' + error.message);
    }
  };

  // Helper function to get status color and icon
  const getStatusInfo = (status) => {
    switch (status?.toLowerCase()) {
      case 'locked':
        return {
          color: 'bg-red-100 text-red-700 border-red-200',
          icon: <FaLock className="text-red-600" />,
          description: 'Reserved for bot pickup'
        };
      case 'in-use':
        return {
          color: 'bg-yellow-100 text-yellow-700 border-yellow-200',
          icon: <FaClock className="text-yellow-600" />,
          description: 'Currently being accessed'
        };
      case 'available':
        return {
          color: 'bg-green-100 text-green-700 border-green-200',
          icon: <FaCheckCircle className="text-green-600" />,
          description: 'Ready for assignment'
        };
      default:
        return {
          color: 'bg-gray-100 text-gray-700 border-gray-200',
          icon: <FaBox className="text-gray-600" />,
          description: 'Unknown status'
        };
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow p-6 mb-8">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-700"></div>
          <span className="ml-3 text-gray-600">Loading bin inventory...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-blue-700">Bin Inventory</h2>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm font-semibold"
          onClick={handleResetBins}
        >
          Reset All Bins
        </button>
      </div>
      
      {/* Statistics Summary */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <div className="text-sm text-gray-600">Total Bins</div>
          <div className="text-2xl font-bold text-blue-600">{bins.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <div className="text-sm text-gray-600">Available</div>
          <div className="text-2xl font-bold text-green-600">{bins.filter(bin => bin.status === 'available').length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
          <div className="text-sm text-gray-600">Locked</div>
          <div className="text-2xl font-bold text-red-600">{bins.filter(bin => bin.status === 'locked').length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
          <div className="text-sm text-gray-600">In Use</div>
          <div className="text-2xl font-bold text-yellow-600">{bins.filter(bin => bin.status === 'in-use').length}</div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-blue-100 text-blue-700">
              <th className="py-3 px-4 text-left">Bin ID</th>
              <th className="py-3 px-4 text-left">Location</th>
              <th className="py-3 px-4 text-left">Products</th>
              <th className="py-3 px-4 text-left">Last Refilled</th>
              <th className="py-3 px-4 text-left">Status</th>
              <th className="py-3 px-4 text-left">Actions</th>
            </tr>
          </thead>
                      <tbody>
              {bins
                .sort((a, b) => a.id - b.id) // Sort bins by ID in ascending order
                .map(bin => {
                const binProducts = getProductsForBin(bin.id);
                const statusInfo = getStatusInfo(bin.status);
                
                return (
                  <tr key={bin.id} className="border-b hover:bg-blue-50 transition-colors">
                  <td className="py-3 px-4 font-mono font-semibold">
                    Bin_{bin.id}
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-mono text-gray-700">
                      (x={bin.x}, y={bin.y}, z={bin.z_location})
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {binProducts.length > 0 ? (
                      <div className="space-y-1">
                        {binProducts.slice(0, 2).map((product, idx) => (
                          <div key={idx} className="text-xs text-gray-700 truncate max-w-xs" title={product.name}>
                            • {product.name}
                          </div>
                        ))}
                        {binProducts.length > 2 && (
                          <div className="text-xs text-gray-500">
                            +{binProducts.length - 2} more products
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-gray-400 text-xs">No products</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-xs text-gray-600">
                    {binProducts.length > 0 ? (
                      formatDate(
                        binProducts.reduce(
                          (latest, p) => {
                            if (!p.last_refilled) return latest;
                            if (!latest) return p.last_refilled;
                            return new Date(p.last_refilled) > new Date(latest) ? p.last_refilled : latest;
                          },
                          null
                        )
                      )
                    ) : (
                      'N/A'
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      {statusInfo.icon}
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold border ${statusInfo.color}`}>
                        {bin.status === 'available' && 'Available'}
                        {bin.status === 'locked' && 'Locked'}
                        {bin.status === 'in-use' && 'In Use'}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {statusInfo.description}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex gap-2">
                      <button 
                        className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                        title="View Details"
                        onClick={() => handleShowDetails(bin.id)}
                      >
                        Details
                      </button>
                      <button 
                        className="px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded hover:bg-orange-200 transition-colors"
                        title="Refill Bin"
                        onClick={() => handleRefillBin(bin.id)}
                      >
                        Refill
                      </button>
                      {bin.status === 'available' && (
                        <button 
                          className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
                          title="Assign to Order"
                        >
                          Assign
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Refill Modal */}
      {showRefillModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold mb-4">Refill Bin {selectedBinId}</h3>
            
            {(() => {
              const binProducts = getProductsForBin(selectedBinId);
              return (
                <>
                  {binProducts.length > 0 ? (
                    <>
                      <p className="text-gray-600 mb-4">This bin contains the following products. Click "Refill" to update the last refill date:</p>
                      
                      <div className="max-h-60 overflow-y-auto mb-4 bg-gray-50 p-3 rounded">
                        {binProducts.map(product => (
                          <div key={product.id} className="flex items-center justify-between p-2 border-b border-gray-200 last:border-b-0">
                            <div className="flex-1">
                              <div className="font-semibold text-sm">{product.name}</div>
                              <div className="text-xs text-gray-500">₹{product.price}</div>
                              <div className="text-xs text-gray-400">
                                Last refilled: {formatDate(product.last_refilled)}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <button className="px-2 py-1 bg-gray-200 rounded text-lg font-bold" onClick={() => handleQuantityChange(product.id, -1)} disabled={refillLoading || (refillQuantities[product.id] || 1) <= 1}>-</button>
                              <span className="font-mono w-6 text-center">{refillQuantities[product.id] || 1}</span>
                              <button className="px-2 py-1 bg-gray-200 rounded text-lg font-bold" onClick={() => handleQuantityChange(product.id, 1)} disabled={refillLoading}>+</button>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="flex gap-2">
                        <button 
                          className="flex-1 px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 disabled:opacity-50"
                          onClick={handleRefillSubmit}
                          disabled={refillLoading}
                        >
                          {refillLoading ? 'Refilling...' : 'Refill Product'}
                        </button>
                        <button 
                          className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                          onClick={() => {
                            setShowRefillModal(false);
                            setSelectedBinId(null);
                          }}
                          disabled={refillLoading}
                        >
                          Cancel
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <p className="text-gray-600 mb-4">This bin has no products assigned to it.</p>
                      <div className="flex gap-2">
                        <button 
                          className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                          onClick={() => {
                            setShowRefillModal(false);
                            setSelectedBinId(null);
                          }}
                        >
                          Close
                        </button>
                      </div>
                    </>
                  )}
                </>
              );
            })()}
          </div>
        </div>
      )}

      {/* Details Modal */}
      {showDetailsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-bold mb-4">Bin Details - Bin {detailsBinId}</h3>
            {(() => {
              const bin = bins.find(b => b.id === detailsBinId);
              const binProducts = getProductsForBin(detailsBinId);
              // Debug log
              console.log('Products in bin', detailsBinId, binProducts);
              if (!bin) return <div className="text-red-500">Bin not found.</div>;
              
              const totalQuantity = binProducts.reduce((sum, p) => sum + (p.quantity ?? 0), 0);
              const totalSold = binProducts.reduce((sum, p) => sum + (p.sale_count ?? 0), 0);
              
              return (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="mb-2 text-gray-700"><b>Location:</b> (x={bin.x}, y={bin.y}, z={bin.z_location})</div>
                      <div className="mb-2 text-gray-700"><b>Status:</b> 
                        <span className={`ml-2 px-2 py-1 rounded-full text-xs font-semibold ${
                          bin.status === 'available' ? 'bg-green-100 text-green-800' :
                          bin.status === 'locked' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {bin.status === 'available' && 'Available'}
                          {bin.status === 'locked' && 'Locked'}
                          {bin.status === 'in-use' && 'In Use'}
                        </span>
                      </div>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="mb-2 text-gray-700"><b>Total Products:</b> {binProducts.length}</div>
                      <div className="mb-2 text-gray-700"><b>Current Inventory:</b> {totalQuantity}</div>
                      <div className="mb-2 text-gray-700"><b>Total Sold:</b> {totalSold}</div>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-800 mb-3">Products in Bin:</h4>
                    {binProducts.length > 0 ? (
                      <div className="space-y-3">
                        {binProducts.map(product => (
                          <div key={product.id} className="bg-gray-50 p-4 rounded-lg border">
                            <div className="flex justify-between items-start mb-2">
                              <div className="flex-1">
                                <div className="font-semibold text-gray-800">{product.name}</div>
                                <div className="text-sm text-gray-600">₹{product.price}</div>
                              </div>
                              <div className="text-right">
                                <div className="text-xs text-gray-500">Product ID: {product.id}</div>
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-4 mt-3">
                              <div className="bg-white p-3 rounded border">
                                <div className="text-xs text-gray-500 mb-1">Current Quantity</div>
                                <div className="text-lg font-bold text-blue-600">{product.quantity || 0}</div>
                              </div>
                              <div className="bg-white p-3 rounded border">
                                <div className="text-xs text-gray-500 mb-1">Quantities Sold</div>
                                <div className="text-lg font-bold text-green-600">{product.sale_count || 0}</div>
                              </div>
                            </div>
                            
                            {product.last_refilled && (
                              <div className="mt-3 text-xs text-gray-500">
                                Last refilled: {formatDate(product.last_refilled)}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-gray-400 text-sm mb-4 bg-gray-50 p-4 rounded-lg">
                        No products in this bin.
                      </div>
                    )}
                  </div>
                  
                  <div className="flex gap-2 mt-6">
                    <button 
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                      onClick={() => handleRefillBin(detailsBinId)}
                    >
                      Refill Bin
                    </button>
                    <button 
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
                      onClick={() => {
                        setShowDetailsModal(false);
                        setDetailsBinId(null);
                      }}
                    >
                      Close
                    </button>
                  </div>
                </>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
} 