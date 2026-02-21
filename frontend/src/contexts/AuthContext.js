import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { setAuthToken, getMe, login as apiLogin, refreshToken as apiRefresh } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth from localStorage
  useEffect(() => {
    const savedUser = localStorage.getItem('kozbeyli_user');
    const token = localStorage.getItem('kozbeyli_token');

    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
      // Verify token is still valid
      getMe()
        .then((r) => {
          const u = r.data;
          setUser(u);
          localStorage.setItem('kozbeyli_user', JSON.stringify(u));
        })
        .catch(() => {
          // Token invalid — try refresh
          const refreshTok = localStorage.getItem('kozbeyli_refresh_token');
          if (refreshTok) {
            apiRefresh({ refresh_token: refreshTok })
              .then((r) => {
                setAuthToken(r.data.token);
                return getMe();
              })
              .then((r) => {
                setUser(r.data);
                localStorage.setItem('kozbeyli_user', JSON.stringify(r.data));
              })
              .catch(() => {
                logout();
              });
          } else {
            logout();
          }
        });
    }
    setLoading(false);
  }, []);

  const loginUser = useCallback(async (username, password) => {
    const res = await apiLogin({ username, password });
    const { token, refresh_token, user: userData } = res.data;
    setAuthToken(token);
    if (refresh_token) {
      localStorage.setItem('kozbeyli_refresh_token', refresh_token);
    }
    localStorage.setItem('kozbeyli_user', JSON.stringify(userData));
    setUser(userData);
    return userData;
  }, []);

  const logout = useCallback(() => {
    setAuthToken(null);
    localStorage.removeItem('kozbeyli_refresh_token');
    setUser(null);
  }, []);

  const hasPermission = useCallback(
    (pageId) => {
      if (!user) return false;
      if (user.role === 'admin') return true;
      const perms = user.permissions || [];
      return perms.includes('*') || perms.includes(pageId);
    },
    [user]
  );

  return (
    <AuthContext.Provider value={{ user, loading, loginUser, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
