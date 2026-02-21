import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel, AlertDialogAction } from '@/components/ui/alert-dialog';
import { toast } from 'sonner';
import { Plus, UserCog, Loader2, LogOut, Pencil, Trash2 } from 'lucide-react';
import api from '@/lib/api';

export default function EditorPage() {
  const { user, logout } = useAuth();
  const [admins, setAdmins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [editForm, setEditForm] = useState({ id: '', name: '', email: '', password: '' });
  const [adminToDelete, setAdminToDelete] = useState(null);
  const [saving, setSaving] = useState(false);

  const fetchAdmins = async () => {
    try {
      const res = await api.get('/editor/admins');
      setAdmins(res.data);
    } catch (err) {
      toast.error('Error cargando administradores');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAdmins(); }, []);

  const handleCreate = async () => {
    if (!form.name.trim() || !form.email.trim() || !form.password.trim()) {
      toast.error('Todos los campos son requeridos');
      return;
    }
    
    // Password length validation
    if (form.password.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }
    
    setSaving(true);
    try {
      await api.post('/editor/create-admin', form);
      toast.success('Administrador creado exitosamente');
      setDialogOpen(false);
      setForm({ name: '', email: '', password: '' });
      fetchAdmins();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error creando administrador');
    } finally {
      setSaving(false);
    }
  };

  const handleEditClick = (admin) => {
    setEditForm({
      id: admin.id,
      name: admin.name,
      email: admin.email,
      password: ''
    });
    setEditDialogOpen(true);
  };

  const handleEdit = async () => {
    if (!editForm.name.trim() || !editForm.email.trim()) {
      toast.error('Nombre y correo son requeridos');
      return;
    }
    
    // Password validation only if password is provided
    if (editForm.password && editForm.password.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }
    
    setSaving(true);
    try {
      const updateData = {
        name: editForm.name,
        email: editForm.email,
      };
      
      // Only include password if it's not empty
      if (editForm.password.trim()) {
        updateData.password = editForm.password;
      }
      
      await api.put(`/editor/admins/${editForm.id}`, updateData);
      toast.success('Administrador actualizado exitosamente');
      setEditDialogOpen(false);
      setEditForm({ id: '', name: '', email: '', password: '' });
      fetchAdmins();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error actualizando administrador');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteClick = (admin) => {
    setAdminToDelete(admin);
    setDeleteDialogOpen(true);
  };

  const handleDelete = async () => {
    if (!adminToDelete) return;
    
    setSaving(true);
    try {
      await api.delete(`/editor/admins/${adminToDelete.id}`);
      toast.success('Administrador eliminado exitosamente');
      setDeleteDialogOpen(false);
      setAdminToDelete(null);
      fetchAdmins();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error eliminando administrador');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <UserCog className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-2xl font-bold font-heading">Panel Editor</h1>
              <p className="text-sm text-muted-foreground">{user?.name}</p>
            </div>
          </div>
          <Button variant="outline" onClick={logout}>
            <LogOut className="h-4 w-4 mr-2" />
            Cerrar Sesión
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-6">
          {/* Welcome Card */}
          <Card>
            <CardHeader>
              <CardTitle>Crear Administradores</CardTitle>
              <CardDescription>
                Como editor, puedes crear usuarios administradores que tendrán acceso completo al sistema.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => setDialogOpen(true)} size="lg">
                <Plus className="h-5 w-5 mr-2" />
                Crear Nuevo Administrador
              </Button>
            </CardContent>
          </Card>

          {/* Admins List */}
          <Card>
            <CardHeader>
              <CardTitle>Administradores Creados ({admins.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : admins.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">
                  No hay administradores creados
                </p>
              ) : (
                <div className="space-y-3">
                  {admins.map((admin) => (
                    <div
                      key={admin.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div>
                        <p className="font-semibold">{admin.name}</p>
                        <p className="text-sm text-muted-foreground">{admin.email}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-muted-foreground mr-2">
                          {admin.active ? 'Activo' : 'Inactivo'}
                        </span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditClick(admin)}
                        >
                          <Pencil className="h-4 w-4 mr-1" />
                          Editar
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteClick(admin)}
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Eliminar
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Create Admin Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Crear Nuevo Administrador</DialogTitle>
            <DialogDescription>
              Ingresa el correo electrónico y contraseña para el nuevo administrador
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Nombre Completo</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Nombre del administrador"
              />
            </div>
            <div className="space-y-2">
              <Label>Correo Electrónico</Label>
              <Input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="admin@educando.com"
              />
            </div>
            <div className="space-y-2">
              <Label>Contraseña</Label>
              <Input
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                placeholder="Contraseña segura"
              />
              <p className="text-xs text-muted-foreground">Mínimo 6 caracteres</p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreate} disabled={saving}>
              {saving && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Crear Administrador
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Admin Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Administrador</DialogTitle>
            <DialogDescription>
              Actualiza la información del administrador. Deja la contraseña vacía si no deseas cambiarla.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Nombre Completo</Label>
              <Input
                value={editForm.name}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                placeholder="Nombre del administrador"
              />
            </div>
            <div className="space-y-2">
              <Label>Correo Electrónico</Label>
              <Input
                type="email"
                value={editForm.email}
                onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                placeholder="admin@educando.com"
              />
            </div>
            <div className="space-y-2">
              <Label>Nueva Contraseña (opcional)</Label>
              <Input
                type="password"
                value={editForm.password}
                onChange={(e) => setEditForm({ ...editForm, password: e.target.value })}
                placeholder="Dejar vacío para no cambiar"
              />
              <p className="text-xs text-muted-foreground">Mínimo 6 caracteres si se proporciona</p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleEdit} disabled={saving}>
              {saving && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Guardar Cambios
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Admin Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente al administrador{' '}
              <strong>{adminToDelete?.name}</strong> ({adminToDelete?.email}).
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={saving}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {saving && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
