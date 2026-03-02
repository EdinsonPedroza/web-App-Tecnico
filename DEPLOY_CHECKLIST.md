# Lista de verificación de despliegue en producción

Plataforma objetivo: **Render** · Base de datos: **MongoDB Atlas Flex** · Almacenamiento: **AWS S3**

---

## 1. Configurar MongoDB Atlas Flex

- [ ] Crea una cuenta en <https://www.mongodb.com/cloud/atlas/register> (si no tienes una).
- [ ] En el panel de Atlas, selecciona **Create a cluster** → elige **Atlas Flex** (o M0 Free Tier para pruebas).
- [ ] **Network Access** → Add IP Address:  
  > ⚠️ **Advertencia de seguridad**: Usa `0.0.0.0/0` solo como medida temporal para el primer deploy.  
  > En producción, restringe el acceso a los IPs de salida de Render (consulta [Render outbound IPs](https://render.com/docs/static-outbound-ip-addresses)) para reducir la superficie de ataque.
- [ ] **Database Access** → Add New Database User:
  - Authentication Method: Password
  - Nombre de usuario: `educando_user` (o el que prefieras)
  - Contraseña: genera una segura (mínimo 24 caracteres, alfanumérica con caracteres especiales; usa un gestor de contraseñas)
  - Roles: `readWrite` sobre la base de datos `WebApp`
- [ ] **Connect** → Drivers → copia la **Connection String** y reemplaza `<password>` con la contraseña creada.  
  Ejemplo: `mongodb+srv://educando_user:TU_PASSWORD@cluster0.abcde.mongodb.net/WebApp?retryWrites=true&w=majority`
- [ ] Guarda la connection string de forma segura; la necesitarás en el paso 3.

---

## 2. Configurar AWS S3

- [ ] Inicia sesión en <https://console.aws.amazon.com>.
- [ ] Ve a **S3** → **Create bucket**:
  - Nombre: p.ej. `educando-uploads` (debe ser único globalmente)
  - Región: la más cercana a tus usuarios (p.ej. `us-east-1`)
  - **Block all public access**: ACTIVADO (los objetos se servirán mediante URLs firmadas)
- [ ] En la configuración del bucket → **Permissions** → **Bucket Policy**, agrega:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "AllowBackendAccess",
        "Effect": "Allow",
        "Principal": {
          "AWS": "arn:aws:iam::TU_ACCOUNT_ID:user/educando-s3-user"
        },
        "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
        "Resource": "arn:aws:s3:::educando-uploads/*"
      }
    ]
  }
  ```
- [ ] Ve a **IAM** → **Users** → **Create user**:
  - Nombre: `educando-s3-user`
  - Tipo de acceso: **Programmatic access**
  - **No adjuntes `AmazonS3FullAccess`** — en su lugar, crea una política personalizada de mínimo privilegio limitada solo a ese bucket (ver la política de ejemplo en el paso anterior)
- [ ] Guarda el **Access Key ID** y el **Secret Access Key** generados; los necesitarás en el paso 3.
- [ ] Anota el nombre del bucket y la región; los necesitarás como variables de entorno.

---

## 3. Configurar Render Dashboard

### Backend (`educando-backend`)

En **Render Dashboard** → selecciona el servicio `educando-backend` → **Environment**:

| Variable | Valor |
|---|---|
| `MONGO_URL` | Connection string de MongoDB Atlas (paso 1) |
| `JWT_SECRET` | Cadena aleatoria segura — genera con `openssl rand -hex 32` |
| `CORS_ORIGINS` | `https://educando-frontend.onrender.com,https://corporacioneducando.com,https://www.corporacioneducando.com` |
| `AWS_ACCESS_KEY_ID` | Access Key ID del usuario IAM (paso 2) |
| `AWS_SECRET_ACCESS_KEY` | Secret Access Key del usuario IAM (paso 2) |
| `AWS_S3_BUCKET` | Nombre del bucket S3 (p.ej. `educando-uploads`) |
| `AWS_S3_REGION` | Región del bucket (p.ej. `us-east-1`) |
| `CREATE_SEED_USERS` | `true` solo en el primer deploy; cambiar a `false` después (ver paso 5) |
| `DB_NAME` | `WebApp` |

### Frontend (`educando-frontend`)

En **Render Dashboard** → selecciona el servicio `educando-frontend` → **Environment**:

| Variable | Valor |
|---|---|
| `BACKEND_URL` | URL pública HTTPS del backend, p.ej. `https://educando-backend.onrender.com` |
| `REACT_APP_BACKEND_URL` | La misma URL del backend |

---

## 4. Primer deploy y verificación

- [ ] En Render Dashboard haz clic en **Manual Deploy** → **Deploy latest commit** para ambos servicios.
- [ ] Espera a que el backend complete el build y esté en estado **Live**.
- [ ] Ve a **Logs** del backend y verifica:
  - `MongoDB connection successful`
  - `Datos iniciales verificados/creados exitosamente`
  - `7 usuarios semilla disponibles` (si `CREATE_SEED_USERS=true`)
- [ ] Ve a **Logs** del frontend y verifica que el build terminó sin errores.
- [ ] Abre la URL del frontend en el navegador y verifica que:
  - La página de login carga correctamente.
  - Puedes autenticarte con las credenciales semilla.
  - La carga/descarga de archivos funciona (si S3 está configurado).
- [ ] Prueba el endpoint de salud del backend: `https://educando-backend.onrender.com/api/health` → debe responder `{"status": "ok"}`.

---

## 5. Post-deploy

- [ ] En Render Dashboard → `educando-backend` → **Environment**, cambia:  
  `CREATE_SEED_USERS` → `false`  
  Esto evita que los usuarios semilla se recreen en cada reinicio.
- [ ] Verifica que los dominios custom (`corporacioneducando.com`) apunten correctamente a los servicios de Render mediante registros CNAME.
- [ ] Activa las **notificaciones de deploy** en Render para recibir alertas ante fallos.
- [ ] Configura **health check alerts** en Render para el backend (`/api/health`).
- [ ] Revisa y rota el `JWT_SECRET` periódicamente (cada 90 días como mínimo).
- [ ] Habilita **MFA** en tu cuenta de MongoDB Atlas y AWS.
