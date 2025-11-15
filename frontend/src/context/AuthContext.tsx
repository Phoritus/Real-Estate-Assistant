import { createContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
});

export interface User {
  id: number;
  email: string;
  username: string;
  lastname: string;
}

export interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (userData: User) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axiosInstance.get('/users/me');
        const raw = response.data as any;
        setIsAuthenticated(true);
        setUser({ id: raw.id, email: raw.email, username: raw.username, lastname: raw.lastname });
      } catch {
        setIsAuthenticated(false);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (_userData?: Partial<User>) => {
    // After backend sets cookie, fetch the actual user profile
    try {
      const response = await axiosInstance.get('/users/me');
      const raw = response.data as any;
      setIsAuthenticated(true);
      setUser({ id: raw.id, email: raw.email, username: raw.username, lastname: raw.lastname });
    } catch {
      // fallback: mark as authenticated; profile will load on refresh
      setIsAuthenticated(true);
    }
  }

  const logout = async () => {
    try {
      await axiosInstance.post('/auth/logout');
    } catch (error) {
      console.error('Logout failed', error);
    } finally {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  if (isLoading) {
    return null; // or a loading spinner
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};