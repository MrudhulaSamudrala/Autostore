import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import AuthModal from './components/AuthModal';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LiveOrderTable from './LiveOrderTable';
import BinInventoryTable from './BinInventoryTable';
import BotGridView from './BotGridView';
import ProductSalesChart from './ProductSalesChart';

function DashboardContent() {
  const [route, setRoute] = useState('/');
  const [authOpen, setAuthOpen] = useState(false);
  const { user } = useAuth();

  React.useEffect(() => {
    if (!user) setAuthOpen(true);
    else setAuthOpen(false);
  }, [user]);

  let content;
  if (route === '/orders' || route === '/') content = <LiveOrderTable />;
  else if (route === '/bins') content = <BinInventoryTable />;
  else if (route === '/bots') content = <BotGridView />;
  else if (route === '/sales') content = <ProductSalesChart />;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar active={route} onNavigate={setRoute} />
      <div className="flex-1 flex flex-col min-h-screen">
        <Topbar />
        <main className="flex-1 p-8 overflow-auto">{content}</main>
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