import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

/**
 * ErrorBoundary Component
 * 
 * Catches JavaScript errors anywhere in the React component tree and displays
 * a fallback UI instead of crashing the whole app with a blank screen.
 * 
 * Common errors this catches:
 * - Chunk loading failures (outdated cached bundles)
 * - Component rendering errors
 * - JavaScript runtime errors
 * - Missing or incompatible dependencies
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      isChunkError: false,
    };
  }

  static getDerivedStateFromError(error) {
    // Check if it's a chunk loading error (common with React lazy loading and outdated cache)
    const isChunkError = error?.message?.toLowerCase().includes('chunk') ||
                         error?.message?.toLowerCase().includes('loading') ||
                         error?.name === 'ChunkLoadError';

    return {
      hasError: true,
      isChunkError,
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // Log to backend if error logging endpoint exists (optional)
    this.logErrorToService(error, errorInfo);
  }

  logErrorToService = (error, errorInfo) => {
    try {
      // Optional: Send error to backend for monitoring
      // This helps track production errors
      const errorData = {
        message: error?.toString(),
        stack: error?.stack,
        componentStack: errorInfo?.componentStack,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString(),
      };

      // Only log in production or if explicitly enabled
      if (process.env.NODE_ENV === 'production') {
        console.log('Error logged:', errorData);
        // Future enhancement: Send to backend endpoint
        // fetch('/api/logs/frontend-error', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(errorData),
        // }).catch(() => {});
      }
    } catch (loggingError) {
      // Silently fail if logging fails
      console.error('Failed to log error:', loggingError);
    }
  };

  handleReload = () => {
    // Clear cache and reload
    if (this.state.isChunkError) {
      // For chunk errors, try to clear cache
      if ('caches' in window) {
        caches.keys().then(names => {
          names.forEach(name => caches.delete(name));
        });
      }
    }
    window.location.reload();
  };

  handleGoHome = () => {
    // Navigate to home and reload
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      const { isChunkError, error } = this.state;

      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4">
          <div className="max-w-2xl w-full">
            <Alert className="border-2 border-destructive/50 bg-background shadow-lg">
              <AlertTriangle className="h-5 w-5 text-destructive" />
              <AlertTitle className="text-lg font-semibold mt-0">
                {isChunkError 
                  ? '¡Actualización Disponible!' 
                  : '¡Algo salió mal!'}
              </AlertTitle>
              <AlertDescription className="space-y-4 mt-3">
                <div className="text-sm text-muted-foreground">
                  {isChunkError ? (
                    <>
                      <p className="mb-2">
                        La aplicación ha sido actualizada. Por favor, recarga la página para obtener la última versión.
                      </p>
                      <p className="font-medium text-foreground">
                        Para solucionar este problema:
                      </p>
                      <ul className="list-disc list-inside ml-2 mt-2 space-y-1">
                        <li>Haz clic en "Recargar Página" abajo</li>
                        <li>O presiona <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">Ctrl+Shift+R</kbd> (Windows/Linux) o <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">⌘+Shift+R</kbd> (Mac)</li>
                        <li>Esto borrará el caché y cargará la versión más reciente</li>
                      </ul>
                    </>
                  ) : (
                    <>
                      <p className="mb-2">
                        Ha ocurrido un error inesperado. Estamos trabajando para solucionarlo.
                      </p>
                      <p className="font-medium text-foreground">
                        Intenta lo siguiente:
                      </p>
                      <ul className="list-disc list-inside ml-2 mt-2 space-y-1">
                        <li>Recarga la página presionando <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">Ctrl+Shift+R</kbd> (Windows/Linux) o <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">⌘+Shift+R</kbd> (Mac)</li>
                        <li>Limpia el caché de tu navegador</li>
                        <li>Intenta en otro navegador o dispositivo</li>
                        <li>Si el problema persiste, contacta al soporte técnico</li>
                      </ul>
                    </>
                  )}
                </div>

                {process.env.NODE_ENV === 'development' && error && (
                  <div className="mt-4 p-3 bg-muted rounded-md">
                    <p className="text-xs font-mono text-muted-foreground break-all">
                      <strong>Error:</strong> {error.toString()}
                    </p>
                  </div>
                )}

                <div className="flex gap-3 mt-4 flex-wrap">
                  <Button 
                    onClick={this.handleReload}
                    variant="default"
                    className="flex items-center gap-2"
                  >
                    <RefreshCw className="h-4 w-4" />
                    Recargar Página
                  </Button>
                  <Button 
                    onClick={this.handleGoHome}
                    variant="outline"
                    className="flex items-center gap-2"
                  >
                    <Home className="h-4 w-4" />
                    Ir al Inicio
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
