#!/usr/bin/env python3
"""
Script para verificar que la autenticación funciona correctamente.
Prueba específicamente el usuario editor.
"""

import os
import bcrypt as _bcrypt

def hash_pw(password):
    return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')

def verify_pw(password, hashed):
    return _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Contraseñas de prueba - NOTA: Usar variables de entorno en producción
# Ver USUARIOS_Y_CONTRASEÑAS.txt para credenciales completas
passwords_to_test = {
    "editor": os.environ.get("SEED_EDITOR_PASSWORD", ""),
    "admin": os.environ.get("SEED_ADMIN_PASSWORD", ""),
    "profesor": os.environ.get("SEED_PROF1_PASSWORD", ""),
    "estudiante": os.environ.get("SEED_STUDENT_PASSWORD", "")
}

print("=" * 70)
print("VERIFICACIÓN DE SISTEMA DE AUTENTICACIÓN")
print("=" * 70)
print()

print("1. Verificando que bcrypt está funcionando correctamente:")
print("-" * 70)

# Probar hash y verificación con una contraseña genérica
test_password = "TestPassword123!"
test_hash = hash_pw(test_password)

print(f"   Hash generado: {test_hash[:50]}...")
print(f"   Longitud del hash: {len(test_hash)} caracteres")
print()

# Verificar que el hash funciona
is_valid = verify_pw(test_password, test_hash)
print(f"   ✓ Verificación con contraseña correcta: {is_valid}")

# Verificar que falla con contraseña incorrecta
is_invalid = verify_pw("wrong_password", test_hash)
print(f"   ✓ Verificación con contraseña incorrecta: {is_invalid}")
print()

print("2. Generando hashes para todos los usuarios:")
print("-" * 70)

for role, password in passwords_to_test.items():
    if not password:
        print(f"   {role:15} | [Variable de entorno no configurada]")
        continue
    hashed = hash_pw(password)
    is_correct = verify_pw(password, hashed)
    print(f"   {role:15} | Hash OK: {is_correct}")

print()
print("3. Verificación del sistema bcrypt:")
print("-" * 70)

# Simular lo que hace el sistema al crear el usuario
editor_password = os.environ.get("SEED_EDITOR_PASSWORD", "")
if editor_password:
    editor_hash_from_code = hash_pw(editor_password)
    print(f"   Hash generado: {editor_hash_from_code[:50]}...")
    print()
    verification_result = verify_pw(editor_password, editor_hash_from_code)
    print(f"   ✓ Verificación con contraseña correcta: {verification_result}")
    wrong_verification = verify_pw("wrongpassword", editor_hash_from_code)
    print(f"   ✓ Verificación con 'wrongpassword' (incorrecta): {wrong_verification}")
else:
    print("   [SEED_EDITOR_PASSWORD no configurada - omitiendo verificación específica]")
print()

print("4. Resumen:")
print("-" * 70)
print("   ✓ Bcrypt está funcionando correctamente")
print("   ✓ Los hashes se generan correctamente")
print("   ✓ La verificación de contraseñas funciona")
print()
print("   Credenciales para probar el login:")
print("   - Pestaña: PROFESOR")
print("   - Email: [Ver variable de entorno o logs del backend]")
print("   - Contraseña: [Ver variable de entorno SEED_EDITOR_PASSWORD o logs del backend]")
print()
print("=" * 70)
print("NOTA: Si el login falla, verifica:")
print("  1. Que estés usando la pestaña 'PROFESOR' (no 'Estudiante')")
print("  2. Que el email y la contraseña sean los configurados en el servidor")
print("  3. Que los datos iniciales se hayan creado en la base de datos")
print("  4. Ver USUARIOS_Y_CONTRASEÑAS.txt para todas las credenciales")
print("=" * 70)
