import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Load user from localStorage
    const stored = localStorage.getItem('autostore_user');
    if (stored) setUser(JSON.parse(stored));
  }, []);

  const signIn = (name) => {
    setUser({ name });
    localStorage.setItem('autostore_user', JSON.stringify({ name }));
  };

  const signUp = (name) => {
    setUser({ name });
    localStorage.setItem('autostore_user', JSON.stringify({ name }));
  };

  const signOut = () => {
    setUser(null);
    localStorage.removeItem('autostore_user');
  };

  return (
    <AuthContext.Provider value={{ user, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
} 