import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileQuestion, Home, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

/**
 * NotFoundPage Component
 * 
 * Displays a user-friendly 404 page when users navigate to non-existent routes.
 * Prevents blank screens by providing clear feedback and navigation options.
 */
function NotFoundPage() {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate('/', { replace: true });
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <Card className="max-w-md w-full shadow-lg">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-muted flex items-center justify-center">
            <FileQuestion className="h-8 w-8 text-muted-foreground" />
          </div>
          <CardTitle className="text-2xl font-bold">Página No Encontrada</CardTitle>
          <CardDescription className="text-base">
            Error 404
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground text-center">
            Lo sentimos, la página que buscas no existe o ha sido movida.
          </p>
          
          <div className="border-t pt-4 space-y-3">
            <p className="text-xs text-muted-foreground text-center">
              ¿Qué puedes hacer?
            </p>
            <ul className="text-xs text-muted-foreground space-y-2 list-disc list-inside">
              <li>Verifica que la URL esté escrita correctamente</li>
              <li>Regresa a la página anterior</li>
              <li>Vuelve a la página de inicio</li>
            </ul>
          </div>

          <div className="flex gap-3 pt-4 flex-col sm:flex-row">
            <Button 
              onClick={handleGoBack}
              variant="outline"
              className="flex items-center justify-center gap-2 flex-1"
            >
              <ArrowLeft className="h-4 w-4" />
              Volver Atrás
            </Button>
            <Button 
              onClick={handleGoHome}
              variant="default"
              className="flex items-center justify-center gap-2 flex-1"
            >
              <Home className="h-4 w-4" />
              Ir al Inicio
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default NotFoundPage;
