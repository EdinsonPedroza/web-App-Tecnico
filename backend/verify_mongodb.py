#!/usr/bin/env python3
"""
Script de verificación de conexión a MongoDB
Este script te ayuda a verificar si tu connection string de MongoDB funciona correctamente.
"""

import asyncio
import sys
import os

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    print("❌ Error: motor no está instalado")
    print("Instálalo con: pip install motor")
    sys.exit(1)

async def verify_connection(mongo_url: str):
    """Verifica la conexión a MongoDB y lista información básica"""
    
    print("=" * 80)
    print("VERIFICACIÓN DE CONEXIÓN A MONGODB")
    print("=" * 80)
    print()
    
    # Redactar URL para logging (ocultar contraseña)
    def redact_url(url: str) -> str:
        if '@' in url:
            # Extraer la parte de credenciales
            protocol = url.split('://')[0]
            rest = url.split('://')[1]
            if '@' in rest:
                credentials, host = rest.split('@', 1)
                if ':' in credentials:
                    user = credentials.split(':')[0]
                    return f"{protocol}://{user}:***@{host}"
        return url
    
    print(f"📡 Intentando conectar a: {redact_url(mongo_url)}")
    print()
    
    try:
        # Crear cliente
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=10000)
        
        # Extraer nombre de la base de datos de la URL
        db_name = 'educando_db'  # default
        if '/' in mongo_url and '?' in mongo_url:
            parts = mongo_url.split('/')
            if len(parts) > 3:
                db_part = parts[3]
                if '?' in db_part:
                    db_name = db_part.split('?')[0]
        
        db = client[db_name]
        
        # Probar la conexión
        print("⏳ Probando conexión...")
        await db.command('ping')
        print("✅ ¡Conexión exitosa a MongoDB!")
        print()
        
        # Obtener información del servidor
        server_info = await db.command('serverStatus')
        print(f"📊 Información del servidor:")
        print(f"   - Versión MongoDB: {server_info.get('version', 'desconocida')}")
        print(f"   - Host: {server_info.get('host', 'desconocido')}")
        print()
        
        # Listar bases de datos
        print("📁 Bases de datos disponibles:")
        databases = await client.list_database_names()
        for db_name in databases:
            if db_name not in ['admin', 'local', 'config']:
                print(f"   - {db_name}")
        print()
        
        # Verificar colecciones en la base de datos
        print(f"📚 Colecciones en '{db.name}':")
        collections = await db.list_collection_names()
        if collections:
            for coll_name in collections:
                count = await db[coll_name].count_documents({})
                print(f"   - {coll_name}: {count} documentos")
        else:
            print("   (vacía - no hay colecciones)")
        print()
        
        # Verificar usuarios específicamente
        if 'users' in collections:
            user_count = await db.users.count_documents({})
            print(f"👥 Usuarios en la colección 'users': {user_count}")
            print()
            
            if user_count == 0:
                print("⚠️  No hay usuarios en la base de datos.")
                print("   Los usuarios se crearán automáticamente cuando el backend se inicie por primera vez.")
                print()
            elif user_count == 7:
                print("✅ ¡Perfecto! Los 7 usuarios iniciales están presentes.")
                print()
            
            # Listar usuarios (sin contraseñas)
            if user_count > 0:
                print("📋 Lista de usuarios:")
                async for user in db.users.find({}, {"_id": 0, "password_hash": 0}).limit(20):
                    role = user.get('role', 'sin rol')
                    name = user.get('name', 'Sin nombre')
                    identifier = user.get('email') or user.get('cedula', 'Sin identificador')
                    active = "✓" if user.get('active', True) else "✗"
                    print(f"   [{active}] {name:25} | {role:12} | {identifier}")
                print()
        
        # Resumen final
        print("=" * 80)
        print("RESUMEN")
        print("=" * 80)
        print("✅ La conexión a MongoDB funciona correctamente")
        print("✅ Puedes usar esta connection string en Render")
        print()
        print("Siguiente paso:")
        print("1. Ve a Render Dashboard → educando-backend → Environment")
        print("2. Agrega o actualiza la variable MONGO_URL con esta connection string")
        print("3. Re-despliega el backend (Manual Deploy → Deploy latest commit)")
        print("4. Verifica los logs del backend para confirmar la conexión")
        print()
        print("Credenciales de usuarios: Ver archivo USUARIOS_Y_CONTRASEÑAS.txt")
        print("=" * 80)
        
    except asyncio.TimeoutError:
        print("❌ Error: Tiempo de espera agotado")
        print()
        print("Posibles causas:")
        print("1. El cluster de MongoDB Atlas está en pausa o inactivo")
        print("2. No se permite el acceso desde tu IP en MongoDB Atlas")
        print("   → Ve a Network Access y permite acceso desde 0.0.0.0/0")
        print("3. La connection string es incorrecta")
        print("4. Problemas de conexión a internet")
        print()
        return False
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error de conexión: {error_msg}")
        print()
        
        # Diagnóstico específico
        if "Authentication failed" in error_msg or "auth" in error_msg.lower():
            print("🔍 Diagnóstico: Error de autenticación")
            print()
            print("Soluciones:")
            print("1. Verifica que reemplazaste <password> con tu contraseña real")
            print("2. Si tu contraseña tiene caracteres especiales, encódalos:")
            print("   @ → %40, : → %3A, / → %2F, ? → %3F")
            print("   Ejemplo: Pass@123 → Pass%40123")
            print("3. Crea un nuevo usuario en MongoDB Atlas con una contraseña sin caracteres especiales")
            
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            print("🔍 Diagnóstico: Error de conexión")
            print()
            print("Soluciones:")
            print("1. Verifica que el cluster de MongoDB Atlas esté activo")
            print("2. En MongoDB Atlas → Network Access:")
            print("   - Agrega una IP Address")
            print("   - Selecciona 'Allow Access from Anywhere' (0.0.0.0/0)")
            print("3. Verifica tu conexión a internet")
            
        elif "not found" in error_msg.lower():
            print("🔍 Diagnóstico: Base de datos o colección no encontrada")
            print()
            print("Esto es normal si es la primera vez. El backend creará las colecciones automáticamente.")
        
        print()
        return False
    
    return True


async def main():
    print()
    
    # Obtener MONGO_URL del argumento o variable de entorno
    mongo_url = None
    
    if len(sys.argv) > 1:
        mongo_url = sys.argv[1]
    else:
        # Intentar leer de variable de entorno
        from dotenv import load_dotenv
        from pathlib import Path
        
        # Cargar .env si existe
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            mongo_url = os.environ.get('MONGO_URL')
    
    if not mongo_url:
        print("=" * 80)
        print("USO DEL SCRIPT")
        print("=" * 80)
        print()
        print("Opción 1: Pasar la connection string como argumento:")
        print('  python verify_mongodb.py "mongodb+srv://user:pass@cluster.mongodb.net/educando_db"')
        print()
        print("Opción 2: Configurar MONGO_URL en el archivo .env")
        print("  1. Edita el archivo backend/.env")
        print("  2. Descomenta o agrega: MONGO_URL=tu_connection_string")
        print("  3. Ejecuta: python verify_mongodb.py")
        print()
        print("=" * 80)
        sys.exit(1)
    
    # Ejecutar verificación
    success = await verify_connection(mongo_url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación cancelada por el usuario")
        sys.exit(1)
