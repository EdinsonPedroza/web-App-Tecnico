# Mejoras de Seguridad Implementadas

## Resumen

Se han implementado múltiples capas de seguridad en el backend para proteger contra intentos de hackeo y ataques comunes.

## Medidas de Seguridad Implementadas

### 1. Rate Limiting en Login ⚡

**Protección contra:** Ataques de fuerza bruta

**Implementación:**
- Límite: 5 intentos de login por IP
- Ventana de tiempo: 5 minutos
- Después de 5 intentos fallidos, la IP es bloqueada temporalmente
- Los intentos exitosos limpian el contador

**Código:**
```python
# Rate limiting: track login attempts per IP
login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW = 300  # 5 minutes

async def check_rate_limit(ip_address: str) -> bool:
    current_time = datetime.now().timestamp()
    # Clean old attempts
    login_attempts[ip_address] = [
        attempt_time for attempt_time in login_attempts[ip_address]
        if current_time - attempt_time < LOGIN_ATTEMPT_WINDOW
    ]
    # Check if limit exceeded
    if len(login_attempts[ip_address]) >= MAX_LOGIN_ATTEMPTS:
        return False
    return True
```

### 2. Mejora en Hash de Contraseñas 🔐

**Protección contra:** Rainbow tables, ataques de diccionario

**ANTES:** SHA256 (vulnerable, sin salt)
```python
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
```

**DESPUÉS:** Bcrypt (seguro, con salt automático)
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Try bcrypt first (new format)
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback to SHA256 for legacy passwords
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
```

**Beneficios:**
- Salt automático único por contraseña
- Algoritmo lento por diseño (dificulta ataques de fuerza bruta)
- Compatible con contraseñas antiguas (migración suave)

### 3. Sanitización de Entradas 🧹

**Protección contra:** XSS (Cross-Site Scripting), inyección de código

**Implementación:**
```python
def sanitize_string(input_str: str, max_length: int = 500) -> str:
    """Sanitize string input to prevent injection attacks"""
    if not input_str:
        return input_str
    # Remove potential XSS/injection characters
    sanitized = re.sub(r'[<>{}]', '', input_str)
    # Limit length
    return sanitized[:max_length]
```

**Aplicado en:**
- Nombres de usuarios
- Correos electrónicos
- Números de teléfono
- Cédulas (solo alfanuméricos)

### 4. Validación Robusta con Pydantic 📋

**Protección contra:** Inyección SQL, datos malformados, buffer overflow

**Validadores implementados:**

```python
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    cedula: Optional[str] = Field(None, max_length=50)
    password: str = Field(..., min_length=6, max_length=200)
    role: str = Field(..., pattern="^(estudiante|profesor|admin)$")
    
    @validator('name', 'email', 'phone')
    def sanitize_text_fields(cls, v):
        if v:
            return sanitize_string(v, 200)
        return v
    
    @validator('cedula')
    def sanitize_cedula(cls, v):
        if v:
            return re.sub(r'[^a-zA-Z0-9]', '', v)[:50]
        return v
```

**Características:**
- Límites de longitud estrictos
- Patrones regex para roles
- Sanitización automática en validadores
- Solo caracteres alfanuméricos en cédulas

### 5. Logging de Seguridad 📝

**Protección contra:** Análisis forense, detección de patrones de ataque

**Eventos registrados:**

1. **Rate limit excedido:**
```python
log_security_event("RATE_LIMIT_EXCEEDED", {
    "ip": client_ip,
    "role": req.role,
    "identifier": req.email or req.cedula
})
```

2. **Intentos de login fallidos:**
```python
log_security_event("LOGIN_FAILED_USER_NOT_FOUND", {...})
log_security_event("LOGIN_FAILED_WRONG_PASSWORD", {...})
log_security_event("LOGIN_FAILED_INACTIVE_ACCOUNT", {...})
```

3. **Intentos no autorizados:**
```python
log_security_event("UNAUTHORIZED_USER_CREATE_ATTEMPT", {...})
log_security_event("UNAUTHORIZED_USER_UPDATE_ATTEMPT", {...})
```

4. **Intentos de duplicados:**
```python
log_security_event("DUPLICATE_EMAIL_ATTEMPT", {...})
log_security_event("DUPLICATE_CEDULA_ATTEMPT", {...})
```

**Formato de logs:**
```
2026-02-17 17:49:14 - __main__ - WARNING - SECURITY: LOGIN_FAILED_WRONG_PASSWORD - {"ip": "192.168.1.100", "role": "estudiante", "user_id": "abc123", "identifier": "1234567890"}
```

### 6. Validación de Roles Estricta ✅

**Protección contra:** Escalación de privilegios, acceso no autorizado

```python
# En login
if req.role not in ["estudiante", "profesor", "admin", "editor"]:
    log_security_event("INVALID_ROLE", {"role": req.role, "ip": client_ip})
    raise HTTPException(status_code=400, detail="Rol inválido")

# En endpoints sensibles
if user["role"] != "admin":
    log_security_event("UNAUTHORIZED_USER_CREATE_ATTEMPT", {
        "attempted_by": user["id"],
        "attempted_role": user["role"]
    })
    raise HTTPException(status_code=403, detail="Solo admin puede crear usuarios")
```

### 7. Protección contra MongoDB Injection 🛡️

**Mediante:**
- Motor (driver async de MongoDB) que escapa automáticamente
- Validación de tipos con Pydantic
- Sanitización de strings

## Mejoras Adicionales Futuras (Recomendadas)

1. **HTTPS obligatorio** en producción
2. **Tokens con refresh** para sesiones más seguras
3. **2FA (autenticación de dos factores)** para admins
4. **Captcha** después de múltiples intentos fallidos
5. **Rotación de JWT_SECRET** periódica
6. **Auditoría de seguridad** con herramientas como OWASP ZAP
7. **Content Security Policy (CSP)** headers
8. **Rate limiting global** para todas las rutas (no solo login)

## Cómo Verificar la Seguridad

### 1. Probar Rate Limiting
```bash
# Intenta login 6 veces con credenciales incorrectas
for i in {1..6}; do
  curl -X POST http://localhost:8001/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"cedula":"wrong","password":"wrong","role":"estudiante"}'
done
# El 6to intento debe retornar error 429
```

### 2. Verificar Logs
```bash
# Ver logs de seguridad en el backend
docker logs web-app-tecnico-backend-1 | grep "SECURITY"
```

### 3. Probar Sanitización
```bash
# Intenta crear usuario con caracteres peligrosos
curl -X POST http://localhost:8001/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"<script>alert(1)</script>","cedula":"123","password":"test123","role":"estudiante"}'
# Los caracteres <> deben ser removidos
```

## Conclusión

✅ El sistema ahora cuenta con múltiples capas de protección contra:
- Ataques de fuerza bruta (rate limiting)
- Robo de contraseñas (bcrypt)
- Inyección de código (sanitización + validación)
- Acceso no autorizado (validación de roles + logging)
- Escalación de privilegios (permisos estrictos)

⚠️ **Importante:** Estas medidas reducen significativamente el riesgo pero no lo eliminan por completo. Siempre mantén el sistema actualizado y realiza auditorías de seguridad periódicas.
