import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Plus, Pencil, Trash2, Loader2, Building2 } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import api from '@/lib/api';

export default function ProgramsPage() {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', description: '', duration: '12 meses', moduleCount: 2 });
  const [saving, setSaving] = useState(false);

  const fetchPrograms = useCallback(async () => {
    try {
      const res = await api.get('/programs');
      setPrograms(res.data);
    } catch (err) {
      toast.error('Error cargando programas');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchPrograms(); }, [fetchPrograms]);

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', description: '', duration: '12 meses', moduleCount: 2 });
    setDialogOpen(true);
  };

  const openEdit = (prog) => {
    setEditing(prog);
    setForm({ 
      name: prog.name, 
      description: prog.description || '', 
      duration: prog.duration || '12 meses',
      moduleCount: prog.modules?.length || 2
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (!form.name.trim()) { toast.error('Nombre requerido'); return; }
    setSaving(true);
    try {
      // Generate modules structure based on moduleCount
      const modules = [];
      for (let i = 1; i <= form.moduleCount; i++) {
        modules.push({
          number: i,
          name: `MÓDULO ${i}`,
          subjects: editing?.modules?.[i - 1]?.subjects || []
        });
      }
      
      const saveData = {
        name: form.name,
        description: form.description,
        duration: form.duration,
        modules: modules
      };
      if (editing) {
        await api.put(`/programs/${editing.id}`, saveData);
        toast.success('Programa actualizado');
      } else {
        await api.post('/programs', saveData);
        toast.success('Programa creado');
      }
      setDialogOpen(false);
      fetchPrograms();
    } catch (err) {
      toast.error('Error guardando programa');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este programa?')) return;
    try {
      await api.delete(`/programs/${id}`);
      toast.success('Programa eliminado');
      fetchPrograms();
    } catch (err) {
      toast.error('Error eliminando programa');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold font-heading">Programas Técnicos</h1>
            <p className="text-muted-foreground mt-1 text-lg">Gestiona los técnicos virtuales</p>
          </div>
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" /> Nuevo Programa
          </Button>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : programs.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay programas registrados</p>
            <Button className="mt-4" onClick={openCreate}><Plus className="h-4 w-4" /> Crear Programa</Button>
          </CardContent></Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {programs.map((prog) => (
              <Card key={prog.id} className="shadow-card hover:shadow-card-hover transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-base font-heading">{prog.name}</CardTitle>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" onClick={() => openEdit(prog)}><Pencil className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(prog.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{prog.description}</p>
                  <div className="flex gap-2 flex-wrap">
                    <Badge variant="secondary">{prog.duration}</Badge>
                    {prog.modules && prog.modules.length > 0 && (
                      <Badge variant="outline">{prog.modules.length} MÓDULOS</Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? 'Editar Programa' : 'Nuevo Programa'}</DialogTitle>
            <DialogDescription>Completa los datos del programa técnico</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Nombre del Programa</Label>
              <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Técnico en..." />
            </div>
            <div className="space-y-2">
              <Label>Descripción</Label>
              <Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Describe el programa..." />
            </div>
            <div className="space-y-2">
              <Label>Duración</Label>
              <Input value={form.duration} onChange={(e) => setForm({ ...form, duration: e.target.value })} placeholder="12 meses" />
            </div>
            <div className="space-y-2">
              <Label>Número de Módulos</Label>
              <Select value={form.moduleCount.toString()} onValueChange={(val) => setForm({ ...form, moduleCount: parseInt(val) })}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona cantidad" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 Módulo</SelectItem>
                  <SelectItem value="2">2 Módulos</SelectItem>
                  <SelectItem value="3">3 Módulos</SelectItem>
                  <SelectItem value="4">4 Módulos</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                Define cuántos módulos tiene este programa técnico
              </p>
            </div>
            <div className="rounded-lg bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">
                <strong>Nota:</strong> Las fechas de inicio y cierre de los módulos se configuran por grupo en la sección "Cursos", no a nivel de programa.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving && <Loader2 className="h-4 w-4 animate-spin" />}
              {editing ? 'Actualizar' : 'Crear'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
