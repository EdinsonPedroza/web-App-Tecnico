import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import api from '@/lib/api';
import { toast } from 'sonner';

const AuthContext = createContext(null);

// Auto-logout after 15 minutes of inactivity (configurable via env var)
const INACTIVITY_TIMEOUT_MS = parseInt(process.env.REACT_APP_INACTIVITY_TIMEOUT_MIN || '15', 10) * 60 * 1000;
const INACTIVITY_WARNING_MS = INACTIVITY_TIMEOUT_MS - 60 * 1000; // warn 1 minute before logout
const ACTIVITY_EVENTS = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart', 'click'];

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const inactivityTimer = useRef(null);
  const warningTimer = useRef(null);

  const logout = useCallback(() => {
    localStorage.removeItem('educando_token');
    localStorage.removeItem('educando_user');
    setUser(null);
  }, []);

  // Reset inactivity timer on user activity
  const resetInactivityTimer = useCallback(() => {
    if (warningTimer.current) clearTimeout(warningTimer.current);
    if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
    warningTimer.current = setTimeout(() => {
      toast.warning('Tu sesión se cerrará en 1 minuto por inactividad');
    }, INACTIVITY_WARNING_MS);
    inactivityTimer.current = setTimeout(() => {
      toast.info('Sesión cerrada por inactividad');
      logout();
    }, INACTIVITY_TIMEOUT_MS);
  }, [logout]);

  useEffect(() => {
    const token = localStorage.getItem('educando_token');
    const savedUser = localStorage.getItem('educando_user');
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('educando_token');
        localStorage.removeItem('educando_user');
      }
    }
    setLoading(false);
  }, []);

  // Attach/detach inactivity tracking when user logs in/out
  useEffect(() => {
    if (!user) {
      if (warningTimer.current) clearTimeout(warningTimer.current);
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
      ACTIVITY_EVENTS.forEach(evt => window.removeEventListener(evt, resetInactivityTimer));
      return;
    }
    // Start the timer and listen for activity
    resetInactivityTimer();
    ACTIVITY_EVENTS.forEach(evt => window.addEventListener(evt, resetInactivityTimer, { passive: true }));
    return () => {
      if (warningTimer.current) clearTimeout(warningTimer.current);
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
      ACTIVITY_EVENTS.forEach(evt => window.removeEventListener(evt, resetInactivityTimer));
    };
  }, [user, resetInactivityTimer]);

  const login = useCallback(async (credentials) => {
    const res = await api.post('/auth/login', credentials);
    const { token, user: userData } = res.data;
    localStorage.setItem('educando_token', token);
    localStorage.setItem('educando_user', JSON.stringify(userData));
    setUser(userData);
    return userData;
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
