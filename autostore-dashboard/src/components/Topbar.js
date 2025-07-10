import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { FaRobot, FaBars } from 'react-icons/fa';
import AuthModal from './AuthModal';

export default function Topbar({ onMenuClick }) {
  const { user, signOut } = useAuth();
  const [authOpen, setAuthOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full bg-gradient-to-r from-blue-50 via-white to-blue-100 shadow-lg border-b border-blue-200 rounded-b-2xl">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-3 md:py-4">
        {/* Left: Project Icon + Name */}
        <div className="flex items-center gap-3 md:gap-4">
          <span className="flex items-center gap-2">
            <FaRobot className="text-blue-500 text-3xl drop-shadow" />
            <span className="text-2xl md:text-3xl font-extrabold text-blue-700 tracking-tight select-none">AutoStore</span>
          </span>
        </div>
        {/* Right: Auth or User Info + Menu */}
        <div className="flex items-center gap-4 relative">
          {user ? (
            <>
              <div className="flex items-center gap-2 md:gap-3 bg-blue-100/60 px-3 py-1 rounded-full shadow-sm">
                <span className="bg-blue-500 text-white rounded-full px-3 py-1 font-bold text-lg shadow-md border-2 border-white">
                  {user.name?.[0]?.toUpperCase() || 'W'}
                </span>
                <span className="font-semibold text-blue-700 text-base md:text-lg">{user.name}</span>
              </div>
              <div className="relative">
                <button
                  className="p-2 rounded-full hover:bg-blue-200 transition-colors"
                  onClick={() => setMenuOpen((open) => !open)}
                  aria-label="Menu"
                >
                  <FaBars className="text-2xl text-blue-500" />
                </button>
                {menuOpen && (
                  <div className="absolute right-0 mt-2 w-40 bg-white border border-blue-100 rounded-xl shadow-xl z-50 animate-fade-in">
                    <button
                      className="block w-full text-left px-4 py-3 text-blue-700 font-semibold hover:bg-blue-50 rounded-xl transition-colors"
                      onClick={() => { setMenuOpen(false); signOut(); }}
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <button
              className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-6 py-2 rounded-full font-bold shadow-md hover:from-blue-600 hover:to-blue-700 transition-all text-base md:text-lg"
              onClick={() => setAuthOpen(true)}
            >
              Sign In / Sign Up
            </button>
          )}
        </div>
      </div>
      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} />
    </header>
  );
} 