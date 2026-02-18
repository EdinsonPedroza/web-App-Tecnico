# 🚀 Inicio Rápido: Render.com (15 minutos)

## Railway no funcionó, así que ahora usamos Render ✅

Esta es la guía MÁS RÁPIDA para tener tu app en línea.

---

## 🎯 3 Pasos Simples

### PASO 1: Crear Cuenta (2 minutos)
1. Ve a https://render.com
2. Clic en "Get Started"
3. Selecciona "Sign up with GitHub"
4. Autoriza a Render
5. ¡Listo!

### PASO 2: Desplegar con Blueprint (10 minutos)
1. En el dashboard, clic en "New +" → "Blueprint"
2. Conecta tu repositorio: `EdinsonPedroza/web-App-Tecnico`
3. Render detecta automáticamente el archivo `render.yaml`
4. Clic en "Apply"
5. **Espera 10-15 minutos** mientras Render construye todo

### PASO 3: Acceder a tu App (1 minuto)
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

### Opción 1: Gratis (Con limitaciones)
- $0/mes
- Se "duerme" después de 15 min sin uso
- Tarda 30 seg en "despertar"
- Perfecto para probar

### Opción 2: Starter (Recomendado para producción)
- ~$14/mes
- Siempre activo
- Incluye MongoDB
- SSL/HTTPS incluido
- Deploy automático

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
- [ ] 3 servicios "Live": MongoDB, Backend, Frontend
- [ ] Puedo acceder a la URL del frontend
- [ ] Puedo iniciar sesión
- [ ] Cambié la contraseña por defecto

---

¡Ya está! Tu app está en internet 🎉
