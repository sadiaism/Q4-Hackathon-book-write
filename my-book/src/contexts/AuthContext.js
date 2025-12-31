import React, { createContext, useContext, useEffect, useState } from 'react';
import { getAuthToken, getCurrentUser } from '../utils/auth';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check auth status on initial load
    const token = getAuthToken();
    if (token) {
      const currentUser = getCurrentUser();
      setUser(currentUser);
    }
    setLoading(false);

    // Listen for storage events to handle auth changes across tabs
    const handleStorageChange = (e) => {
      if (e.key === 'authToken') {
        const token = localStorage.getItem('authToken');
        if (token) {
          const currentUser = getCurrentUser();
          setUser(currentUser);
        } else {
          setUser(null);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login: (userData, token) => {
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
    },
    logout: () => {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      setUser(null);
    },
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};