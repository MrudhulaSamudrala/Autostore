import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import AuthModal from './components/AuthModal';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LiveOrderTable from './LiveOrderTable';
import BinInventoryTable from './BinInventoryTable';
import BotGridView from './BotGridView';
import ProductSalesChart from './ProductSalesChart';
import Bot3DGridView from './Bot3DGridView';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Dashboard Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen bg-gray-50">
          <Sidebar active="/orders" onNavigate={() => {}} />
          <div className="flex-1 flex flex-col min-h-screen">
            <Topbar onMenuClick={() => {}} />
            <main className="flex-1 p-8 overflow-auto">
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h2 className="text-xl font-bold text-red-800 mb-4">Something went wrong</h2>
                <p className="text-red-700 mb-4">An error occurred while loading this page. Please try refreshing the page.</p>
                <button 
                  onClick={() => window.location.reload()} 
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Refresh Page
                </button>
              </div>
            </main>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

function MainLayoutContent() {
  const [route, setRoute] = useState('/orders'); // Default to orders page
  const [authOpen, setAuthOpen] = useState(false);
  const { user } = useAuth();

  React.useEffect(() => {
    if (!user) setAuthOpen(true);
    else setAuthOpen(false);
  }, [user]);

  let content;
  if (route === '/orders') content = <LiveOrderTable />;
  else if (route === '/bins') content = <BinInventoryTable />;
  else if (route === '/bots') content = <BotGridView />;
  else if (route === '/sales') content = <ProductSalesChart />;
  else if (route === '/3d-bots') content = <Bot3DGridView />;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar active={route} onNavigate={setRoute} />
      <div className="flex-1 flex flex-col min-h-screen">
        <Topbar onMenuClick={() => {}} />
        <main className="flex-1 p-8 overflow-auto">
          <ErrorBoundary>
            {content}
          </ErrorBoundary>
        </main>
      </div>
      <AuthModal open={authOpen} onClose={() => {}} />
    </div>
  );
}

export default function MainLayout() {
  return (
    <AuthProvider>
      <MainLayoutContent />
    </AuthProvider>
  );
} 