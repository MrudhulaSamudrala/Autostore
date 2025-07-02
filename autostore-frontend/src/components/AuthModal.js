import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { FaShoppingCart } from 'react-icons/fa';

export default function AuthModal({ open, onClose }) {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState('signin');
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');

  if (!open) return null;

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (mode === 'signin') {
      if (!form.name && !form.email) {
        setError('Email or Username is required');
        return;
      }
      if (!form.password) {
        setError('Password is required');
        return;
      }
      signIn(form.name || form.email); // For demo, just use name or email
      setForm({ name: '', email: '', password: '' });
      setError('');
      onClose();
    } else {
      if (!form.name) {
        setError('Full Name is required');
        return;
      }
      if (!form.email) {
        setError('Email is required');
        return;
      }
      if (!form.password) {
        setError('Password is required');
        return;
      }
      signUp(form.name); // For demo, just use name
      setForm({ name: '', email: '', password: '' });
      setError('');
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-xs relative flex flex-col items-center">
        <button className="absolute top-2 right-2 text-gray-400 hover:text-gray-600" onClick={onClose}>&times;</button>
        <div className="flex flex-col items-center mb-6">
          <FaShoppingCart className="text-pink-500 text-4xl mb-1" />
          <span className="text-2xl font-bold text-pink-600">AutoStore</span>
        </div>
        <div className="flex w-full mb-6">
          <button
            className={`flex-1 py-2 font-bold rounded-tl-xl rounded-bl-xl ${mode === 'signin' ? 'bg-pink-500 text-white' : 'bg-white text-pink-500'}`}
            onClick={() => setMode('signin')}
          >
            Sign In
          </button>
          <button
            className={`flex-1 py-2 font-bold rounded-tr-xl rounded-br-xl ${mode === 'signup' ? 'bg-pink-500 text-white' : 'bg-white text-pink-500'}`}
            onClick={() => setMode('signup')}
          >
            Sign Up
          </button>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full">
          {mode === 'signin' ? (
            <>
              <input
                type="text"
                name="name"
                placeholder="Email or Username"
                className="border rounded px-3 py-2 focus:outline-none focus:ring"
                value={form.name}
                onChange={handleChange}
              />
              <input
                type="password"
                name="password"
                placeholder="Password"
                className="border rounded px-3 py-2 focus:outline-none focus:ring"
                value={form.password}
                onChange={handleChange}
              />
              <button type="submit" className="bg-pink-500 text-white py-2 rounded font-bold hover:bg-pink-600">
                Sign In
              </button>
            </>
          ) : (
            <>
              <input
                type="text"
                name="name"
                placeholder="Full Name"
                className="border rounded px-3 py-2 focus:outline-none focus:ring"
                value={form.name}
                onChange={handleChange}
              />
              <input
                type="email"
                name="email"
                placeholder="Email"
                className="border rounded px-3 py-2 focus:outline-none focus:ring"
                value={form.email}
                onChange={handleChange}
              />
              <input
                type="password"
                name="password"
                placeholder="Password"
                className="border rounded px-3 py-2 focus:outline-none focus:ring"
                value={form.password}
                onChange={handleChange}
              />
              <button type="submit" className="bg-pink-500 text-white py-2 rounded font-bold hover:bg-pink-600">
                Sign Up
              </button>
            </>
          )}
          {error && <div className="text-red-600 text-sm text-center">{error}</div>}
        </form>
        <div className="mt-4 text-center text-sm">
          {mode === 'signin' ? (
            <span>Don't you have an account ? <button className="text-pink-500 font-bold" onClick={() => setMode('signup')}>Sign Up.</button></span>
          ) : (
            <span>Already have an account ? <button className="text-pink-500 font-bold" onClick={() => setMode('signin')}>Sign In.</button></span>
          )}
        </div>
      </div>
    </div>
  );
} 