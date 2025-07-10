import React from 'react';

const categories = [
  'All',
  'Personal Care',
  'Grocery',
  'Household Essentials',
  'Snacks & Beverages',
  'Pharma & Wellness',
  'Packaged Foods',
  'Baby Care',
  'Toys',
  'Pet Supplies'
];

export default function CategoryFilter({ selected, onSelect }) {
  return (
    <div className="flex gap-2 pb-2 overflow-x-auto">
      {categories.map(cat => (
        <button
          key={cat}
          className={`px-4 py-1 rounded-full border ${selected === cat ? 'bg-pink-100 text-pink-600 border-pink-300' : 'bg-white text-gray-600 border-gray-200'} font-semibold`}
          onClick={() => onSelect(cat)}
        >
          {cat}
        </button>
      ))}
    </div>
  );
} 

// 'Household essentials', 'Snacks & Beverages',  'Pet Supplies', 'Package Foods', 'Baby Care'