#!/usr/bin/env python3
"""
Script de verificación rápida para la base de datos WebApp
Ejecuta este script para verificar que todo esté configurado correctamente.
"""

import asyncio
import sys
import os
from pathlib import Path

# Configurar path para importar desde backend
# Este script está en scripts/, por lo que backend está en el directorio padre
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from dotenv import load_dotenv
except ImportError:
    print("❌ Error: Faltan dependencias")
    print("Instálalas con: pip install motor python-dotenv")
    sys.exit(1)

# Cargar variables de entorno
load_dotenv(backend_dir / '.env.local')
load_dotenv(backend_dir / '.env')

async def main():
    print("\n" + "="*80)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN - BASE DE DATOS WebApp")
    print("="*80 + "\n")
    
    # Verificar variables de entorno
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'WebApp')
    
    print("📋 Variables de entorno:")
    print(f"   ✅ MONGO_URL: {'Configurada' if mongo_url else '❌ NO CONFIGURADA'}")
    print(f"   ✅ DB_NAME: {db_name}")
    print()
    
    if not mongo_url:
        print("❌ ERROR: MONGO_URL no está configurada")
        print("\nPara configurar:")
        print("1. Abre: backend/.env")
        print("2. Asegúrate que tenga:")
        print('   MONGO_URL="mongodb+srv://usuario:password@cluster.mongodb.net/WebApp"')
        print('   DB_NAME="WebApp"')
        sys.exit(1)
    
    # Redactar URL para mostrar
    def redact_url(url: str) -> str:
        if '@' in url:
            protocol = url.split('://')[0]
            rest = url.split('://')[1]
            if '@' in rest:
                credentials, host = rest.split('@', 1)
                if ':' in credentials:
                    user = credentials.split(':')[0]
                    return f"{protocol}://{user}:***@{host}"
        return url
    
    print(f"🌐 Conectando a: {redact_url(mongo_url)}")
    print()
    
    try:
        # Crear cliente con timeout corto
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=10000)
        db = client[db_name]
        
        # Probar conexión
        print("⏳ Probando conexión...")
        await db.command('ping')
        print("✅ ¡CONEXIÓN EXITOSA!")
        print()
        
        # Verificar base de datos
        print(f"📊 Base de Datos: {db_name}")
        collections = await db.list_collection_names()
        print(f"   Colecciones encontradas: {len(collections)}")
        print()
        
        if not collections:
            print("📝 La base de datos está vacía (esto es normal si es la primera vez)")
            print()
            print("🚀 Qué hacer ahora:")
            print("   1. Inicia la aplicación con: docker compose -f docker-compose.dev.yml up --build")
            print("   2. O inicia el backend con: cd backend && uvicorn server:app --reload")
            print("   3. La aplicación creará automáticamente:")
            print("      - 7 usuarios (admin, profesores, estudiantes)")
            print("      - 3 programas académicos con materias")
            print("      - 1 curso de ejemplo")
            print("      - Collection 'App' (vacía)")
            print()
        else:
            print("📚 Colecciones existentes:")
            for coll_name in sorted(collections):
                count = await db[coll_name].count_documents({})
                emoji = "✅" if count > 0 else "📝"
                print(f"   {emoji} {coll_name}: {count} documentos")
            print()
            
            # Verificar usuarios
            if 'users' in collections:
                users_count = await db.users.count_documents({})
                if users_count >= 7:
                    print("✅ Usuarios configurados correctamente")
                    
                    # Contar por rol
                    admin_count = await db.users.count_documents({"role": "admin"})
                    teacher_count = await db.users.count_documents({"role": "profesor"})
                    student_count = await db.users.count_documents({"role": "estudiante"})
                    editor_count = await db.users.count_documents({"role": "editor"})
                    
                    print(f"   - {editor_count} Editor(es)")
                    print(f"   - {admin_count} Administrador(es)")
                    print(f"   - {teacher_count} Profesor(es)")
                    print(f"   - {student_count} Estudiante(s)")
                    print()
                    
            # Verificar programas
            if 'programs' in collections:
                programs_count = await db.programs.count_documents({})
                print(f"✅ Programas académicos: {programs_count}")
                print()
            
            # Verificar collection App
            if 'App' in collections:
                app_count = await db.App.count_documents({})
                print(f"✅ Collection 'App': {app_count} documentos")
                print()
        
        print("="*80)
        print("🎉 CONFIGURACIÓN CORRECTA - Todo listo para usar!")
        print("="*80)
        print()
        print("📖 Siguiente paso: Inicia la aplicación")
        print()
        print("   Opción 1 - Docker:")
        print("   docker compose -f docker-compose.dev.yml up --build")
        print()
        print("   Opción 2 - Sin Docker:")
        print("   cd backend && uvicorn server:app --reload --port 8001")
        print()
        print("📝 Usuarios de prueba: Ver USUARIOS_Y_CONTRASEÑAS.txt")
        print("📚 Guía completa: Ver CONFIGURACION_MONGODB.md")
        print()
        
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
        print()
        print("🔧 SOLUCIONES:")
        print()
        print("1. 🌐 Configurar Network Access en MongoDB Atlas:")
        print("   - Ve a: https://cloud.mongodb.com/")
        print("   - Network Access → ADD IP ADDRESS")
        print("   - Selecciona: 'ALLOW ACCESS FROM ANYWHERE' (0.0.0.0/0)")
        print("   - Espera 1-2 minutos")
        print()
        print("2. 🔑 Verificar credenciales:")
        print("   - MongoDB Atlas → Database Access")
        print("   - Usuario debe existir con permisos 'Read and write to any database'")
        print()
        print("3. ✅ Verificar que el cluster esté activo:")
        print("   - MongoDB Atlas → Database")
        print("   - El cluster debe estar en estado verde (Running)")
        print()
        print("📖 Guía completa: Ver CONFIGURACION_MONGODB.md")
        print()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
