import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import { logEnvironmentInfo } from "@/utils/envValidation";

// Log environment configuration for debugging
logEnvironmentInfo();

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

  // Check if it's a chunk loading error
  if (event.message?.toLowerCase().includes('chunk') || 
      event.message?.toLowerCase().includes('loading')) {
    console.warn('Chunk loading error detected. This usually means the app was updated. Please refresh the page.');
  }
});

// Global promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
