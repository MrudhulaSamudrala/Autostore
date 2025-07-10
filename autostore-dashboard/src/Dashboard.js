import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import AuthModal from './components/AuthModal';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LiveOrderTable from './LiveOrderTable';
import BinInventoryTable from './BinInventoryTable';
import BotGridView from './BotGridView';
import ProductSalesChart from './ProductSalesChart';
import Bot3DGridView from './Bot3DGridView';
// import Bot3DClaude from './Bot3DClaude';

function DashboardContent() {
  const [route, setRoute] = useState('/');
  const [authOpen, setAuthOpen] = useState(false);
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  React.useEffect(() => {
    if (!user) setAuthOpen(true);
    else setAuthOpen(false);
  }, [user]);

  useEffect(() => {
    fetch('http://localhost:8000/orders/')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch orders');
        return res.json();
      })
      .then(data => {
        setOrders(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  let content;
  if (route === '/orders' || route === '/') content = <LiveOrderTable />;
  else if (route === '/bins') content = <BinInventoryTable />;
  else if (route === '/bots') content = <BotGridView />;
  else if (route === '/sales') content = <ProductSalesChart />;
  else if (route === '/3d-bots') content = <Bot3DGridView />;
  // else if (route === '/3d-visualization') content = <Bot3DClaude />;

  if (loading) return <div>Loading orders...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar active={route} onNavigate={setRoute} />
      <div className="flex-1 flex flex-col min-h-screen">
        <Topbar onMenuClick={() => {}} />
        <main className="flex-1 p-8 overflow-auto">
          {content}
        </main>
      </div>
      <AuthModal open={authOpen} onClose={() => {}} />
    </div>
  );
}

export default function Dashboard() {
  return (
    <AuthProvider>
      <DashboardContent />
    </AuthProvider>
  );
} 