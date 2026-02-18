# 🚀 Inicio Rápido: Render.com (20 minutos)

## Railway no funcionó, así que ahora usamos Render ✅

Esta es la guía MÁS RÁPIDA para tener tu app en línea.

---

## 🎯 4 Pasos Simples

### PASO 1: Crear Cuenta (2 minutos)
1. Ve a https://render.com
2. Clic en "Get Started"
3. Selecciona "Sign up with GitHub"
4. Autoriza a Render
5. ¡Listo!

### PASO 2: Desplegar con Blueprint (5 minutos)
1. En el dashboard, clic en "New +" → "Blueprint"
2. Conecta tu repositorio: `EdinsonPedroza/web-App-Tecnico`
3. Render detecta automáticamente el archivo `render.yaml`
4. Clic en "Apply"
5. **Espera 5-10 minutos** mientras Render construye todo

### PASO 3: Configurar MongoDB (5 minutos)

#### Opción A: MongoDB Atlas (Gratis - Recomendado)
1. Ve a https://www.mongodb.com/cloud/atlas/register
2. Crea cuenta (puedes usar Google)
3. Selecciona el plan **M0 FREE**
4. Crea un cluster (región: Oregon)
5. Crea usuario: `educando_admin` con contraseña segura
6. Permitir acceso desde `0.0.0.0/0`
7. Obtén la connection string (clic en "Connect" → "Connect your application")
8. Copia la URL (reemplaza `<password>` con tu contraseña)
9. Ve a Render → servicio "educando-backend" → "Environment"
10. Pega la URL en `MONGO_URL`
11. Guarda los cambios

#### Opción B: Private Service en Render ($7/mes)
1. En Render: "New +" → "Private Service"
2. Conecta tu repositorio
3. Dockerfile Path: `mongodb.Dockerfile`
4. Agrega disco: `/data/db` con 10GB
5. Copia la "Internal Connection String"
6. Ve al backend → Environment → pega en `MONGO_URL`

### PASO 4: Acceder a tu App (1 minuto)
1. En el dashboard, clic en el servicio "educando-frontend"
2. Copia la URL (ej: `https://educando-frontend.onrender.com`)
3. Ábrela en tu navegador
4. Inicia sesión:
   - Email: `admin@educando.com`
   - Contraseña: `admin123`
5. **¡Cambia la contraseña inmediatamente!**

---

## 🎉 ¡Listo!

Tu aplicación está en línea en: `https://educando-frontend.onrender.com`

---

## 💰 ¿Cuánto cuesta?

### Opción 1: Gratis + MongoDB Atlas Gratis
- Backend + Frontend: $0/mes (plan gratuito de Render)
- MongoDB Atlas M0: $0/mes (512MB de almacenamiento)
- **Total: $0/mes**
- Se "duerme" después de 15 min sin uso
- Tarda 30 seg en "despertar"
- Perfecto para probar

### Opción 2: Starter + MongoDB Atlas (Recomendado)
- Backend + Frontend: ~$7/mes (plan Starter de Render)
- MongoDB Atlas M0: $0/mes (gratis, 512MB)
- **Total: ~$7/mes**
- Siempre activo
- SSL/HTTPS incluido
- Deploy automático
- Perfecto para producción con pocos usuarios

### Opción 3: Todo en Render
- Backend + Frontend: ~$7/mes (plan Starter)
- MongoDB Private Service: ~$7/mes (con disco)
- **Total: ~$14/mes**
- Todo en un solo lugar
- 10GB de almacenamiento para MongoDB

---

## 🆘 ¿Problemas?

### La aplicación no carga
- Espera 15-20 minutos (la primera vez es lenta)
- Ve a "Logs" en cada servicio para ver errores

### Frontend no se conecta al backend
1. Ve al servicio "educando-backend"
2. Copia su URL
3. Ve al servicio "educando-frontend"
4. Ve a "Environment" → Edita `REACT_APP_BACKEND_URL`
5. Pega la URL del backend
6. Guarda

### Error en MongoDB
1. Verifica que "educando-mongodb" esté "Live"
2. Ve a "Connect" y copia la "Internal Connection String"
3. Ve al backend → "Environment" → Edita `MONGO_URL`
4. Pega la conexión interna
5. Guarda

---

## 📚 Más Información

- **Guía Completa**: Lee `GUIA_RENDER.md` para todos los detalles
- **Documentación**: https://render.com/docs
- **Soporte**: https://community.render.com/

---

## 🔄 ¿Por qué Render en lugar de Railway?

- ✅ Más estable
- ✅ Mejor documentación
- ✅ Comunidad más grande
- ✅ Mismo precio (~$14/mes)
- ✅ Plan gratuito más generoso

---

## ✅ Checklist Rápido

- [ ] Cuenta creada en Render
- [ ] Blueprint desplegado
- [ ] MongoDB configurado (Atlas o Private Service)
- [ ] Variable `MONGO_URL` configurada en el backend
- [ ] 2 servicios "Live": Backend, Frontend
- [ ] Puedo acceder a la URL del frontend
- [ ] Puedo iniciar sesión
- [ ] Cambié la contraseña por defecto

---

¡Ya está! Tu app está en internet 🎉
