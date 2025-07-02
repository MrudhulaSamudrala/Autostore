import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function Topbar() {
  const { user, signOut } = useAuth();
  return (
    <header className="sticky top-0 z-40 bg-white shadow flex items-center justify-between px-8 py-3 border-b">
      <div className="flex items-center gap-3">
        <span className="font-bold text-blue-700 text-lg">👷 Worker</span>
        {user && <span className="text-gray-600">{user.name}</span>}
      </div>
      <div className="flex items-center gap-4">
        <span className="font-bold text-xl text-blue-700">AutoStore Dashboard</span>
        {user && <button onClick={signOut} className="ml-4 px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 font-semibold">Sign Out</button>}
      </div>
    </header>
  );
} 