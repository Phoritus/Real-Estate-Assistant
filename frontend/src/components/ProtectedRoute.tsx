import { Navigate } from 'react-router-dom';
import { useContext } from 'react';
import type { ReactElement } from 'react';
import { AuthContext } from '../context/AuthContext';
import type { AuthContextValue } from '../context/AuthContext';

interface Props { children: ReactElement }

const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('AuthContext not found');
  return ctx;
};

export const ProtectedRoute = ({ children }: Props) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
};
