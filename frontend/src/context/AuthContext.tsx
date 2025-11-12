import { createContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';

export interface AuthContextValue {
  isAuthenticated: boolean;
  login: (username?: string, password?: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('reauth');
    if (stored === 'true') setIsAuthenticated(true);
  }, []);

  const login = async () => {
    // Simulate auth delay
    await new Promise((r) => setTimeout(r, 400));
    setIsAuthenticated(true);
    localStorage.setItem('reauth', 'true');
  };

  const logout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('reauth');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
