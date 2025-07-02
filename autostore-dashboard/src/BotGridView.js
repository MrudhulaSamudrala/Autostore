import React from 'react';
import { FaRobot } from 'react-icons/fa';

const gridSize = 10;
const mockBots = [
  { id: 'Bot-1', x: 2, y: 3, status: 'idle' },
  { id: 'Bot-2', x: 5, y: 7, status: 'busy' },
  { id: 'Bot-3', x: 8, y: 1, status: 'charging' },
];

const statusColor = {
  idle: 'text-green-500',
  busy: 'text-yellow-500',
  charging: 'text-blue-500',
};

export default function BotGridView() {
  const grid = Array.from({ length: gridSize }, (_, y) =>
    Array.from({ length: gridSize }, (_, x) => {
      const bot = mockBots.find(b => b.x === x && b.y === y);
      return bot ? bot : null;
    })
  );

  return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <h2 className="text-xl font-bold mb-4 text-blue-700">Bot Grid View</h2>
      <div className="grid grid-cols-10 gap-1 mb-4">
        {grid.flat().map((cell, idx) => (
          <div
            key={idx}
            className="w-8 h-8 flex items-center justify-center bg-gray-100 rounded border"
          >
            {cell ? (
              <FaRobot className={`text-xl ${statusColor[cell.status]}`} title={cell.id} />
            ) : null}
          </div>
        ))}
      </div>
      <div className="flex gap-4 mt-2 text-sm">
        <span className="flex items-center gap-1"><FaRobot className="text-green-500" />Idle</span>
        <span className="flex items-center gap-1"><FaRobot className="text-yellow-500" />Busy</span>
        <span className="flex items-center gap-1"><FaRobot className="text-blue-500" />Charging</span>
      </div>
    </div>
  );
} 