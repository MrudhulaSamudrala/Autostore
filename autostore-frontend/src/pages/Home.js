import React, { useState } from 'react';
import { useSearch } from '../contexts/SearchContext';
import ProductSlider from '../components/ProductSlider';
import CategoryFilter from '../components/CategoryFilter';
import ProductCard from '../components/ProductCard';

const allProducts = [
  { product_id: 1, product_name: 'Widget A', price: 10, category: 'Electronics', sale: true, img: 'https://i.imgur.com/6IUbEME.png' },
  { product_id: 2, product_name: 'Chips', price: 5, category: 'Snacks', sale: false, img: 'https://i.imgur.com/1bX5QH6.png' },
  { product_id: 3, product_name: 'Soda', price: 8, category: 'Drinks', sale: true, img: 'https://i.imgur.com/8Km9tLL.png' },
  { product_id: 4, product_name: 'Shampoo', price: 12, category: 'Personal Care', sale: false, img: 'https://i.imgur.com/8Km9tLL.png' },
  { product_id: 5, product_name: 'Couch', price: 100, category: 'Household', sale: true, img: 'https://i.imgur.com/6IUbEME.png' },
  { product_id: 6, product_name: 'Cereal', price: 7, category: 'Grocery', sale: false, img: 'https://i.imgur.com/1bX5QH6.png' },
];

export default function Home() {
  const [category, setCategory] = useState('All');
  const { search } = useSearch();

  const filtered = allProducts.filter(p =>
    (category === 'All' || p.category === category) &&
    (p.product_name.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div>
      <CategoryFilter selected={category} onSelect={setCategory} />
      <ProductSlider />
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {filtered.map((p) => (
          <ProductCard key={p.product_id} product={p} />
        ))}
      </div>
    </div>
  );
} 