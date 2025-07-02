import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import CartPage from './pages/CartPage';
import OrderStatusPage from './pages/OrderStatusPage';
import { AuthProvider } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';
import { SearchProvider } from './contexts/SearchContext';
import Header from './components/Header';
import CartDrawer from './components/CartDrawer';

function App() {
  const [cartOpen, setCartOpen] = useState(false);
  return (
    <AuthProvider>
      <CartProvider>
        <SearchProvider>
          <Router>
            <Header onCartClick={() => setCartOpen(true)} />
            <CartDrawer open={cartOpen} onClose={() => setCartOpen(false)} />
            <div className="p-4 max-w-7xl mx-auto">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/cart" element={<CartPage />} />
                <Route path="/order-status/:orderId" element={<OrderStatusPage />} />
              </Routes>
            </div>
          </Router>
        </SearchProvider>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
