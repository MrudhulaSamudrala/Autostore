import React from 'react';
import { FaTachometerAlt, FaBoxOpen, FaRobot, FaChartBar, FaListAlt } from 'react-icons/fa';

const links = [
  // { name: 'Dashboard', icon: <FaTachometerAlt />, path: '/' },
  { name: 'Orders', icon: <FaListAlt />, path: '/orders' },
  { name: 'Bins', icon: <FaBoxOpen />, path: '/bins' },
  { name: 'Bots', icon: <FaRobot />, path: '/bots' },
  { name: '3D Bots', icon: <FaRobot style={{ filter: 'drop-shadow(0 0 2px #6366f1)' }} />, path: '/3d-bots' },
  { name: 'Sales Chart', icon: <FaChartBar />, path: '/sales' },
];

export default function Sidebar({ active, onNavigate }) {
  return (
    <aside className="bg-blue-700 text-white w-56 min-h-screen flex flex-col py-6 px-2 shadow-lg">
      <div className="text-2xl font-bold mb-10 flex items-center justify-center gap-2">
        <FaRobot className="text-3xl" />
        AutoStore
      </div>
      <nav className="flex flex-col gap-2">
        {links.map(link => (
          <button
            key={link.name}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg text-lg font-medium transition-colors ${active === link.path ? 'bg-white text-blue-700 shadow' : 'hover:bg-blue-600'}`}
            onClick={() => onNavigate(link.path)}
          >
            {link.icon}
            {link.name}
          </button>
        ))}
      </nav>
    </aside>
  );
} 