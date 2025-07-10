import React, { useState, useEffect } from 'react';
import { useSearch } from '../contexts/SearchContext';
import ProductSlider from '../components/ProductSlider';
import CategoryFilter from '../components/CategoryFilter';
import ProductCard from '../components/ProductCard';

export default function Home() {
  const [category, setCategory] = useState('All');
  const { search } = useSearch();
  const [products, setProducts] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/products/')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch products');
        return res.json();
      })
      .then(data => setProducts(data))
      .catch(err => setError(err.message));
  }, []);

  const filtered = products.filter(p => {
    const productCategory = (p.category || '').trim().toLowerCase();
    const selectedCategory = category.trim().toLowerCase();
    return (
      (selectedCategory === 'all' || (productCategory && productCategory === selectedCategory)) &&
      (p.name && p.name.toLowerCase().includes(search.toLowerCase()))
    );
  });

  return (
    <div>
      <CategoryFilter selected={category} onSelect={setCategory} />
      <ProductSlider />
      {error && <div className="text-red-500">{error}</div>}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {filtered.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
} 