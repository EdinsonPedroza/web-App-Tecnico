import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import { logEnvironmentInfo, isChunkError } from "@/utils/envValidation";

// Log environment configuration for debugging
logEnvironmentInfo();


const maybeAutoReloadForChunk = (reason) => {
  if (!isChunkError(reason)) return false;
  try {
    const last = parseInt(sessionStorage.getItem('_chunk_auto_reload_at') || '0', 10);
    const now = Date.now();
    // Avoid reload loops: max one automatic reload every 15s
    if (now - last < 15000) return false;
    sessionStorage.setItem('_chunk_auto_reload_at', String(now));
    window.location.reload();
    return true;
  } catch (_) {
    window.location.reload();
    return true;
  }
};

// Global error handler for uncaught errors
window.addEventListener('error', (event) => {
  // Log error to console for debugging
  console.error('Global error caught:', {
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    error: event.error,
  });

  // Check if it's a chunk loading error using shared utility
  if (isChunkError(event.error) || event.filename?.includes('chunk')) {
    console.warn('Chunk loading error detected. Trying automatic reload once.');
    maybeAutoReloadForChunk(event.error || new Error(event.message || 'chunk error'));
  }
});

// Global promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  maybeAutoReloadForChunk(event.reason);
});

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
