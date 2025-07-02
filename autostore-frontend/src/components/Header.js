import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';
import { useSearch } from '../contexts/SearchContext';
import AuthModal from './AuthModal';
import { FaShoppingCart, FaCog } from 'react-icons/fa';

export default function Header({ onCartClick }) {
  const { user } = useAuth();
  const { signOut } = useAuth();
  const { cartCount, cartTotal } = useCart();
  const { search, setSearch } = useSearch();
  const [authOpen, setAuthOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <header className="bg-white shadow sticky top-0 z-40">
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-2">
          <FaShoppingCart className="text-pink-500 text-2xl" />
          <span className="text-2xl font-bold text-pink-600">AutoStore</span>
        </div>
        <input
          type="text"
          placeholder="Search products..."
          className="border rounded px-4 py-2 w-80 focus:outline-none focus:ring"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <div className="flex items-center gap-4 relative">
          {user ? (
            <div className="flex items-center gap-2">
              <span className="bg-pink-100 text-pink-600 rounded-full px-3 py-1 font-semibold">M</span>
              <span className="font-semibold">{user.name}</span>
            </div>
          ) : (
            <button
              className="bg-pink-500 text-white px-4 py-2 rounded font-semibold hover:bg-pink-600"
              onClick={() => setAuthOpen(true)}
            >
              Sign In / Sign Up
            </button>
          )}
          <div
            className="flex items-center gap-2 bg-pink-500 text-white px-3 py-2 rounded cursor-pointer"
            onClick={onCartClick}
          >
            <FaShoppingCart />
            <span className="font-bold">{cartCount} items ₹{cartTotal}</span>
          </div>
          <div className="relative">
            <FaCog
              className="text-2xl text-gray-400 hover:text-gray-600 cursor-pointer"
              onClick={() => setSettingsOpen((open) => !open)}
            />
            {settingsOpen && user && (
              <div className="absolute right-0 mt-2 w-32 bg-white border rounded shadow-lg z-50">
                <button
                  className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100"
                  onClick={() => { setSettingsOpen(false); signOut(); }}
                >
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} />
    </header>
  );
} 