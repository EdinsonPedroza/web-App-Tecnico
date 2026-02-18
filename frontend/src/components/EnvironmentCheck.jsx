import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { validateEnvironment } from '@/utils/envValidation';

/**
 * EnvironmentCheck Component
 * 
 * Validates environment configuration and displays errors if misconfigured.
 * Prevents blank screens by catching configuration issues early.
 */
function EnvironmentCheck({ children }) {
  const validation = validateEnvironment();

  // If environment is valid, render children normally
  if (validation.isValid) {
    return children;
  }

  // If environment is invalid, show configuration error
  const errorMessages = Object.entries(validation.results)
    .filter(([_, result]) => !result.isValid)
    .map(([key, result]) => result.message);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="max-w-2xl w-full">
        <Alert className="border-2 border-destructive/50 bg-background shadow-lg">
          <AlertTriangle className="h-5 w-5 text-destructive" />
          <AlertTitle className="text-lg font-semibold mt-0">
            Error de Configuración
          </AlertTitle>
          <AlertDescription className="space-y-4 mt-3">
            <div className="text-sm text-muted-foreground">
              <p className="mb-2 font-medium text-foreground">
                La aplicación no está configurada correctamente:
              </p>
              <ul className="list-disc list-inside ml-2 space-y-2">
                {errorMessages.map((msg, idx) => (
                  <li key={idx} className="font-mono text-xs">{msg}</li>
                ))}
              </ul>
            </div>

            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-md">
              <div className="flex gap-2">
                <Info className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="text-xs text-blue-900 dark:text-blue-100 space-y-2">
                  <p className="font-medium">Para administradores:</p>
                  <ul className="list-disc list-inside ml-2 space-y-1">
                    <li>Verifica las variables de entorno en el servidor</li>
                    <li>Asegúrate de que REACT_APP_BACKEND_URL esté correctamente definida</li>
                    <li>Reconstruye la aplicación después de cambiar variables de entorno</li>
                    <li>Consulta la documentación de configuración del proyecto</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="text-xs text-muted-foreground mt-4">
              <p>Si eres un usuario, por favor contacta al administrador del sistema.</p>
            </div>
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
}

export default EnvironmentCheck;
