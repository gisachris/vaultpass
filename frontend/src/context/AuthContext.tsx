import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../lib/api';
import { User, LoginCredentials, RegisterCredentials, AuthContextType } from '../types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Check token and verify user session on mount
  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem('vaultpass_token');
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const response = await api.get<User>('/auth/me');
        setUser(response.data);
      } catch (error) {
        console.error('Failed to load user session', error);
        localStorage.removeItem('vaultpass_token');
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    setLoading(true);
    try {
      const response = await api.post<{ access_token: string; user: User }>('/auth/login', credentials);
      const { access_token, user: loggedUser } = response.data;
      
      localStorage.setItem('vaultpass_token', access_token);
      setUser(loggedUser);
    } catch (error) {
      localStorage.removeItem('vaultpass_token');
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    setLoading(true);
    try {
      await api.post('/auth/register', credentials);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('vaultpass_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
