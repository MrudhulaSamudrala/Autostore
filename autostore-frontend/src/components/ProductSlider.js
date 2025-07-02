import React, { useEffect, useState } from 'react';

const slides = [
  {
    title: 'Smart storage Smarter delivery Zero delays',
    subtitle: 'Get faves to your door.',
    cta: 'Shop Now',
    img: 'https://i.imgur.com/8Km9tLL.png',
    bg: 'bg-blue-400',
  },
  {
    title: 'Big Sale on Electronics!',
    subtitle: 'Save up to 50% on gadgets.',
    cta: 'Explore',
    img: 'https://i.imgur.com/6IUbEME.png',
    bg: 'bg-pink-400',
  },
  {
    title: 'Fresh Snacks Delivered Fast',
    subtitle: 'Tasty treats at your doorstep.',
    cta: 'Order Snacks',
    img: 'https://i.imgur.com/1bX5QH6.png',
    bg: 'bg-green-400',
  },
];

export default function ProductSlider() {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => setIndex(i => (i + 1) % slides.length), 4000);
    return () => clearInterval(timer);
  }, []);
  const slide = slides[index];
  return (
    <div className={`rounded-xl p-8 flex items-center justify-between mb-8 ${slide.bg} transition-all duration-500`}>
      <div>
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">{slide.title}</h2>
        <p className="text-white mb-4">{slide.subtitle}</p>
        <button className="bg-white text-blue-600 font-semibold px-6 py-2 rounded shadow hover:bg-blue-50">{slide.cta}</button>
      </div>
      <img src={slide.img} alt="banner" className="h-32 md:h-40 lg:h-48 hidden md:block" />
    </div>
  );
} 