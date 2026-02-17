# Manual Testing Guide for EDITOR Role Implementation

## Prerequisites
- Backend server running on http://localhost:8001
- Frontend server running on http://localhost:3000
- MongoDB running and initialized with seed data

## Test 1: Editor Login and Basic Navigation

### Steps:
1. Open http://localhost:3000 in browser
2. You should see 4 tabs: Estudiante, Profesor, Admin, Editor
3. Click on "Editor" tab
4. Enter credentials:
   - Email: `editor@educando.com`
   - Password: `editor123`
5. Click "Ingresar"

### Expected Results:
- Login successful with welcome message
- Redirected to `/editor` page
- Page shows:
  - Header with "Panel Editor" title
  - User name "Editor Principal" 
  - Logout button
  - "Crear Administradores" card with description
  - "Crear Nuevo Administrador" button
  - "Administradores Creados" list showing existing admins

### Screenshots to Take:
- [ ] Login page with Editor tab
- [ ] Editor dashboard main view

---

## Test 2: Create New Admin via Editor

### Steps:
1. On Editor page, click "Crear Nuevo Administrador" button
2. Dialog should open with form
3. Fill in form:
   - Nombre Completo: `Test Administrator`
   - Correo Electrónico: `testadmin@educando.com`
   - Contraseña: `TestAdmin123`
4. Click "Crear Administrador"

### Expected Results:
- Success toast message: "Administrador creado exitosamente"
- Dialog closes
- New admin appears in the "Administradores Creados" list
- List shows: Name, Email, Status (Activo)

### Edge Cases to Test:
- Try creating admin with duplicate email → Should show error
- Try creating admin with empty fields → Should show validation error
- Try creating admin with invalid email format → Should show error

### Screenshots to Take:
- [ ] Create admin dialog
- [ ] Admin list showing new admin

---

## Test 3: Login as Newly Created Admin

### Steps:
1. Click "Cerrar Sesión" on Editor page
2. Return to login page
3. Click "Admin" tab
4. Enter new admin credentials:
   - Email: `testadmin@educando.com`
   - Password: `TestAdmin123`
5. Click "Ingresar"

### Expected Results:
- Login successful
- Redirected to `/admin` dashboard
- Full admin interface visible with:
  - Dashboard statistics
  - Navigation sidebar
  - Access to all admin features (Programas, Materias, Profesores, Estudiantes, Grupos)

### Screenshots to Take:
- [ ] Admin dashboard for newly created admin
- [ ] Admin sidebar navigation

---

## Test 4: UI Fix - Subjects Page Program Names

### Steps:
1. Login as admin (use any admin account)
2. Click on "Materias" in sidebar or navigate to `/admin/subjects`
3. View the subject cards displayed
4. Look at the Badge showing program name at bottom of each card

### Expected Results:
- Full program names should be visible without truncation
- Examples of what should be fully visible:
  - "Técnico en Asistencia Administrativa"
  - "Técnico Laboral en Atención a la Primera Infancia"
  - "Técnico en Seguridad y Salud en el Trabajo"
- Text may wrap to multiple lines if needed
- No "..." truncation visible

### Before vs After:
- **Before**: Badge showed "Técnico en Asist..." (truncated at ~40 characters)
- **After**: Badge shows full text "Técnico en Asistencia Administrativa"

### Screenshots to Take:
- [ ] Subjects page showing full program names (zoomed in on badges)

---

## Test 5: Authorization and Access Control

### Test 5A: Editor Cannot Access Admin Routes
1. Login as editor
2. Try to manually navigate to:
   - http://localhost:3000/admin
   - http://localhost:3000/admin/programs
   - http://localhost:3000/admin/subjects

**Expected**: Immediately redirected back to `/editor`

### Test 5B: Admin Cannot Access Editor Route
1. Login as admin
2. Try to manually navigate to:
   - http://localhost:3000/editor

**Expected**: Immediately redirected back to `/admin`

### Test 5C: Editor API Endpoint Protection
1. Login as admin
2. Open browser DevTools > Console
3. Try to call editor endpoint:
```javascript
fetch('http://localhost:8001/api/editor/admins', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
}).then(r => r.json()).then(console.log)
```

**Expected**: 403 Forbidden error with message "Solo editor puede ver administradores"

### Test 5D: Admin Creation Endpoint Protection
1. Login as profesor or estudiante
2. Try similar API call to create admin

**Expected**: 403 Forbidden error

---

## Test 6: Responsive Design - Mobile View

### Steps:
1. Open browser DevTools
2. Toggle device toolbar (responsive mode)
3. Set to mobile device (e.g., iPhone 12, 390x844)
4. Navigate to login page
5. View the role tabs

### Expected Results:
- On mobile (<640px): Tabs should display in 2 columns (2 rows)
- On desktop (>640px): Tabs should display in 4 columns (1 row)
- All tabs remain accessible and clickable
- No horizontal scrolling required

### Screenshots to Take:
- [ ] Mobile view of login page (2x2 grid)
- [ ] Desktop view of login page (1x4 grid)

---

## Test 7: Editor Page Performance

### Steps:
1. Login as editor
2. Open DevTools > Network tab
3. Clear network log
4. Reload `/editor` page
5. Note the API calls made

### Expected Results:
- Only 1-2 API calls on page load:
  - GET /api/auth/me (verify current user)
  - GET /api/editor/admins (fetch admin list)
- No unnecessary polling or repeated calls
- Page should load quickly (< 1 second on local)
- No heavy resources loaded (no charts, no large images)

### Performance Metrics:
- [ ] Initial page load time
- [ ] Number of API calls
- [ ] Total data transferred

---

## Regression Testing

### Test existing functionality remains working:

1. **Admin Functions**:
   - [ ] Can create/edit programs
   - [ ] Can create/edit subjects  
   - [ ] Can create/edit teachers
   - [ ] Can create/edit students
   - [ ] Can create/edit courses/groups

2. **Professor Functions**:
   - [ ] Can view assigned courses
   - [ ] Can create activities
   - [ ] Can grade students

3. **Student Functions**:
   - [ ] Can view enrolled courses
   - [ ] Can submit activities
   - [ ] Can view grades

---

## Security Testing

### Test authentication and authorization:

1. **Password Security**:
   - [ ] Passwords are not visible in network requests
   - [ ] Passwords are not visible in browser storage
   - [ ] Password hashing is used

2. **Token Security**:
   - [ ] JWT token is used for authentication
   - [ ] Token includes role information
   - [ ] Token expires after configured time

3. **Role-based Access**:
   - [ ] Each role can only access their designated routes
   - [ ] API endpoints validate user role
   - [ ] Unauthorized requests return 403

---

## Browser Compatibility

Test in multiple browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if available)
- [ ] Edge

---

## Summary Checklist

Core functionality:
- [ ] Editor can login
- [ ] Editor can create admins
- [ ] Created admins can login
- [ ] Program names display fully (not truncated)
- [ ] Mobile responsive layout works
- [ ] No security vulnerabilities
- [ ] No regression in existing features

---

## Known Issues / Limitations

- Phone field is optional for editor-created admins (can be None)
- Editor cannot edit or delete existing admins (by design)
- Editor cannot access any other system features (by design)

---

## Credentials Reference

```
Editor:
  Email: editor@educando.com
  Password: editor123

Existing Admin:
  Email: admin@educando.com
  Password: admin123

Profesor:
  Email: profesor@educando.com
  Password: profesor123

Estudiante:
  Cédula: 1234567890
  Password: estudiante123
```
