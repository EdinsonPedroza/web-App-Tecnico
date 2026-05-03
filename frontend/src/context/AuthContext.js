import React, { createContext, useContext, useState, useEffect, useCallback, useRef, useMemo } from 'react';
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
  const lastResetRef = useRef(0);

  const logout = useCallback(async (reason) => {
    try {
      const refreshToken = sessionStorage.getItem('educando_refresh_token');
      if (refreshToken) {
        await api.post('/auth/logout', { refresh_token: refreshToken }).catch(() => {});
      }
    } catch {}
    sessionStorage.removeItem('educando_token');
    sessionStorage.removeItem('educando_refresh_token');
    sessionStorage.removeItem('educando_user');
    setUser(null);
    if (reason === 'inactivity') {
      toast.info('Sesión cerrada por inactividad');
    }
  }, []);

  // Reset inactivity timer on user activity — throttled to once per second to avoid
  // clearTimeout/setTimeout thrash from high-frequency events like mousemove.
  const resetInactivityTimer = useCallback(() => {
    const now = Date.now();
    if (now - lastResetRef.current < 1000) return;
    lastResetRef.current = now;
    if (warningTimer.current) clearTimeout(warningTimer.current);
    if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
    warningTimer.current = setTimeout(() => {
      toast.warning('Tu sesión se cerrará en 1 minuto por inactividad');
    }, INACTIVITY_WARNING_MS);
    inactivityTimer.current = setTimeout(() => {
      logout('inactivity');
    }, INACTIVITY_TIMEOUT_MS);
  }, [logout]);

  useEffect(() => {
    const token = sessionStorage.getItem('educando_token');
    const savedUser = sessionStorage.getItem('educando_user');
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        sessionStorage.removeItem('educando_token');
        sessionStorage.removeItem('educando_user');
      }
      // Sincronizar datos con el backend en segundo plano
      api.get('/auth/me').then(res => {
        sessionStorage.setItem('educando_user', JSON.stringify(res.data));
        setUser(res.data);
      }).catch((err) => {
        // Only clear session for actual auth failures (401),
        // not for network errors or server errors
        if (err.response?.status === 401) {
          sessionStorage.removeItem('educando_token');
          sessionStorage.removeItem('educando_refresh_token');
          sessionStorage.removeItem('educando_user');
          setUser(null);
        }
        // For network errors, timeouts, 5xx, etc., keep the cached user data
        // The user will be re-validated on next successful API call
      });
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
    const { token, refresh_token, user: userData } = res.data;
    sessionStorage.setItem('educando_token', token);
    sessionStorage.setItem('educando_refresh_token', refresh_token);
    sessionStorage.setItem('educando_user', JSON.stringify(userData));
    setUser(userData);
    return userData;
  }, []);

  const value = useMemo(
    () => ({ user, login, logout, loading }),
    [user, login, logout, loading]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
