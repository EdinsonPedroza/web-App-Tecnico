#!/bin/bash
# Script para configurar las credenciales de MongoDB de forma segura
# Este script crea un archivo .env.local con las credenciales (no se sube a Git)

echo "======================================================================"
echo "    CONFIGURACIÓN SEGURA DE MONGODB PARA webApp"
echo "======================================================================"
echo ""
echo "Este script creará un archivo backend/.env.local con tus credenciales."
echo "Este archivo NO se subirá a Git (está en .gitignore)"
echo ""

echo "Ingresa las credenciales de tu base de datos MongoDB Atlas:"
echo ""

# Pedir MongoDB URL
echo "MongoDB Connection String:"
echo "Formato: mongodb+srv://usuario:password@cluster.mongodb.net/webApp?appName=Cluster0"
read -p "URL: " MONGO_URL

if [ -z "$MONGO_URL" ]; then
    echo "❌ Error: Debes proporcionar un MongoDB URL"
    exit 1
fi

# Pedir DB Name
read -p "Nombre de la base de datos [webApp]: " DB_NAME
DB_NAME=${DB_NAME:-webApp}

# Crear archivo .env.local en backend
ENV_LOCAL_FILE="backend/.env.local"

echo ""
echo "Creando $ENV_LOCAL_FILE..."

cat > "$ENV_LOCAL_FILE" << EOF
# Configuración local de MongoDB (no se sube a Git)
# Generado automáticamente por configurar_mongodb.sh

MONGO_URL="$MONGO_URL"
DB_NAME="$DB_NAME"
CORS_ORIGINS="*"
EOF

# Verificar que se creó el archivo
if [ -f "$ENV_LOCAL_FILE" ]; then
    echo "✅ Archivo creado exitosamente!"
    echo ""
    echo "======================================================================"
    echo "    CONFIGURACIÓN COMPLETADA"
    echo "======================================================================"
    echo ""
    echo "📁 Archivo creado: $ENV_LOCAL_FILE"
    echo "🔒 Este archivo NO se subirá a Git (está en .gitignore)"
    echo ""
    echo "Próximos pasos:"
    echo "1. Asegúrate de haber configurado Network Access en MongoDB Atlas"
    echo "   (Ver CONFIGURACION_MONGODB.md para instrucciones)"
    echo ""
    echo "2. Inicia la aplicación:"
    echo "   - Con Docker: docker compose -f docker-compose.dev.yml up --build"
    echo "   - Sin Docker: cd backend && uvicorn server:app --reload"
    echo ""
    echo "3. Verifica la conexión:"
    echo "   python scripts/verificar_webapp.py"
    echo ""
    echo "📖 Guía completa: CONFIGURACION_MONGODB.md"
    echo "🚀 Inicio rápido: INICIO_RAPIDO_WEBAPP.md"
    echo ""
else
    echo "❌ Error al crear el archivo"
    exit 1
fi
