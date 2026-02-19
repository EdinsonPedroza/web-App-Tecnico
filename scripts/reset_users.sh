#!/bin/bash
# Script para reiniciar usuarios del sistema
# Elimina TODOS los usuarios existentes y crea nuevos usuarios por defecto

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🔄 RESET DE USUARIOS - Sistema Técnico Virtual             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Detectar URL del backend
if [ -z "$BACKEND_URL" ]; then
    BACKEND_URL="http://localhost:8000"
    echo "📍 Usando URL por defecto: $BACKEND_URL"
else
    echo "📍 Usando URL configurada: $BACKEND_URL"
fi

echo ""
echo "⚠️  ADVERTENCIA: Esto eliminará TODOS los usuarios existentes"
echo "    y creará nuevos usuarios por defecto."
echo ""
read -p "¿Continuar? (s/N): " confirm

if [[ ! "$confirm" =~ ^[sS]$ ]]; then
    echo "❌ Operación cancelada"
    exit 0
fi

echo ""
echo "🔄 Reiniciando usuarios..."
echo ""

# Llamar al endpoint de reset con token de confirmación
response=$(curl -s -X POST "$BACKEND_URL/api/admin/reset-users?confirm_token=RESET_ALL_USERS_CONFIRM")

# Verificar si la respuesta contiene "message"
if echo "$response" | grep -q "message"; then
    echo "✅ Usuarios reiniciados exitosamente"
    echo ""
    echo "📋 Nuevos usuarios creados:"
    echo ""
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📖 Consulta NUEVOS_USUARIOS.md para ver las credenciales"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "❌ Error al reiniciar usuarios"
    echo "$response"
    exit 1
fi
