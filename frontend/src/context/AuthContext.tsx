import { createContext, useState, useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';
import { BASE_URL } from '../config/env.tsx'


const axiosInstance = axios.create({
  baseURL: BASE_URL,
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
    const checkedOnce = useRef(false);

    const USER_KEY = 'auth_user';

  useEffect(() => {
    // First attempt: load from localStorage to avoid network call
    if (!checkedOnce.current) {
      const cached = localStorage.getItem(USER_KEY);
      if (cached) {
        try {
          const parsed = JSON.parse(cached) as User;
          setUser(parsed);
          setIsAuthenticated(true);
          setIsLoading(false);
          checkedOnce.current = true;
          return; // Skip initial /users/me call
        } catch {
          // fall through to server check
        }
      }
    }

    const checkAuth = async () => {
      if (checkedOnce.current) return; // Prevent duplicate checks
      try {
        const response = await axiosInstance.get('/users/me');
        const raw = response.data as any;
        const u: User = { id: raw.id, email: raw.email, username: raw.username, lastname: raw.lastname };
        setIsAuthenticated(true);
        setUser(u);
        localStorage.setItem(USER_KEY, JSON.stringify(u));
      } catch {
        setIsAuthenticated(false);
        setUser(null);
        localStorage.removeItem(USER_KEY);
      } finally {
        setIsLoading(false);
        checkedOnce.current = true;
      }
    };
    checkAuth();

    // Listen for cross-tab logout/login
    const onStorage = (e: StorageEvent) => {
      if (e.key === USER_KEY) {
        if (e.newValue) {
          try {
            const parsed = JSON.parse(e.newValue) as User;
            setUser(parsed);
            setIsAuthenticated(true);
          } catch {
            // ignore parse errors
          }
        } else {
          setUser(null);
          setIsAuthenticated(false);
        }
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const login = async (_userData?: Partial<User>) => {
    // Only fetch if user not already cached
    if (!user) {
      try {
        const response = await axiosInstance.get('/users/me');
        const raw = response.data as any;
        const u: User = { id: raw.id, email: raw.email, username: raw.username, lastname: raw.lastname };
        setIsAuthenticated(true);
        setUser(u);
        localStorage.setItem(USER_KEY, JSON.stringify(u));
      } catch {
        setIsAuthenticated(true); // cookie exists, will resolve later
      }
    } else {
      setIsAuthenticated(true);
    }
  };

  const logout = async () => {
    try {
      await axiosInstance.post('/auth/logout');
    } catch (error) {
      console.error('Logout failed', error);
    } finally {
      setIsAuthenticated(false);
      setUser(null);
      localStorage.removeItem(USER_KEY);
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