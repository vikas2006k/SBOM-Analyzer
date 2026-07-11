import React, { createContext, useState, useEffect, useContext } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check saved session on mount
    const savedToken = localStorage.getItem('sentinel_token');
    const savedUser = localStorage.getItem('sentinel_user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);
      const data = response.data.data;
      
      localStorage.setItem('sentinel_token', data.token);
      localStorage.setItem('sentinel_user', JSON.stringify(data.user));
      
      setToken(data.token);
      setUser(data.user);
      return { success: true };
    } catch (error) {
      console.error("Login failed:", error);
      const msg = error.response?.data?.message || "Invalid credentials. Please try again.";
      return { success: false, error: msg };
    }
  };

  const logout = () => {
    authAPI.logout();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
