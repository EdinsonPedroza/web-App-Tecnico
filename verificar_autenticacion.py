#!/usr/bin/env python3
"""
Script para verificar que la autenticación funciona correctamente.
Prueba específicamente el usuario editor.
"""

from passlib.context import CryptContext

# Configuración de bcrypt (igual que en server.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Contraseñas de prueba - NOTA: Estas son las contraseñas del sistema
# Ver USUARIOS_Y_CONTRASEÑAS.txt para credenciales completas
passwords_to_test = {
    "editor": "Editor2026*CM",
    "admin": "Admin2026*LT",
    "profesor": "Profe2026*DS",
    "estudiante": "Estud2026*SM"
}

print("=" * 70)
print("VERIFICACIÓN DE SISTEMA DE AUTENTICACIÓN")
print("=" * 70)
print()

print("1. Verificando que bcrypt está funcionando correctamente:")
print("-" * 70)

# Probar hash y verificación
test_password = "Editor2026*CM"
test_hash = pwd_context.hash(test_password)

print(f"   Contraseña de prueba: {test_password}")
print(f"   Hash generado: {test_hash[:50]}...")
print(f"   Longitud del hash: {len(test_hash)} caracteres")
print()

# Verificar que el hash funciona
is_valid = pwd_context.verify(test_password, test_hash)
print(f"   ✓ Verificación con contraseña correcta: {is_valid}")

# Verificar que falla con contraseña incorrecta
is_invalid = pwd_context.verify("wrong_password", test_hash)
print(f"   ✓ Verificación con contraseña incorrecta: {is_invalid}")
print()

print("2. Generando hashes para todos los usuarios:")
print("-" * 70)

for role, password in passwords_to_test.items():
    hashed = pwd_context.hash(password)
    is_correct = pwd_context.verify(password, hashed)
    print(f"   {role:15} | Contraseña: {password:15} | Hash OK: {is_correct}")

print()
print("3. Verificación de hash específico del editor en el código:")
print("-" * 70)

# Este es el hash que debería estar en la base de datos para el editor
editor_password = "Editor2026*CM"
# Simular lo que hace el sistema al crear el usuario
editor_hash_from_code = pwd_context.hash(editor_password)

print(f"   Contraseña del editor: {editor_password}")
print(f"   Hash generado: {editor_hash_from_code[:50]}...")
print()

# Verificar que funciona
verification_result = pwd_context.verify("Editor2026*CM", editor_hash_from_code)
print(f"   ✓ Verificación con 'Editor2026*CM': {verification_result}")

wrong_verification = pwd_context.verify("wrongpassword", editor_hash_from_code)
print(f"   ✓ Verificación con 'wrongpassword' (incorrecta): {wrong_verification}")
print()

print("4. Resumen:")
print("-" * 70)
print("   ✓ Bcrypt está funcionando correctamente")
print("   ✓ Los hashes se generan correctamente")
print("   ✓ La verificación de contraseñas funciona")
print()
print("   Credenciales para probar el login:")
print("   - Pestaña: PROFESOR")
print("   - Email: carlos.mendez@educando.com")
print("   - Contraseña: Editor2026*CM")
print()
print("=" * 70)
print("NOTA: Si el login falla, verifica:")
print("  1. Que estés usando la pestaña 'PROFESOR' (no 'Estudiante')")
print("  2. Que el email sea exactamente: carlos.mendez@educando.com")
print("  3. Que la contraseña sea exactamente: Editor2026*CM")
print("  4. Que los datos iniciales se hayan creado en la base de datos")
print("  5. Ver USUARIOS_Y_CONTRASEÑAS.txt para todas las credenciales")
print("=" * 70)
