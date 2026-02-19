import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Plus, Pencil, Trash2, Loader2, BookOpen, Filter, Search } from 'lucide-react';
import api from '@/lib/api';

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterProgram, setFilterProgram] = useState('all');
  const [filterModule, setFilterModule] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', program_id: '', module_number: 1, description: '' });
  const [saving, setSaving] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [subRes, progRes] = await Promise.all([api.get('/subjects'), api.get('/programs')]);
      setSubjects(subRes.data);
      setPrograms(progRes.data);
    } catch (err) {
      toast.error('Error cargando datos');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const filtered = subjects.filter(s => {
    if (filterProgram !== 'all' && String(s.program_id) !== String(filterProgram)) return false;
    if (filterModule !== 'all' && s.module_number !== parseInt(filterModule)) return false;
    if (searchQuery && !s.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });
  const getProgramName = (id) => programs.find(p => p.id === id)?.name || 'Sin programa';
  
  // Get unique module numbers from subjects
  const availableModules = [...new Set(subjects.map(s => s.module_number))].sort();

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', program_id: programs[0]?.id ? String(programs[0].id) : '', module_number: 1, description: '' });
    setDialogOpen(true);
  };

  const openEdit = (subj) => {
    setEditing(subj);
    setForm({ name: subj.name, program_id: String(subj.program_id), module_number: subj.module_number, description: subj.description || '' });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (!form.name.trim() || !form.program_id) { toast.error('Nombre y programa requeridos'); return; }
    setSaving(true);
    try {
      if (editing) {
        await api.put(`/subjects/${editing.id}`, { name: form.name, description: form.description, module_number: form.module_number, program_id: form.program_id });
        toast.success('Materia actualizada');
      } else {
        await api.post('/subjects', form);
        toast.success('Materia creada');
      }
      setDialogOpen(false);
      fetchData();
    } catch (err) {
      toast.error('Error guardando materia');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar esta materia?')) return;
    try {
      await api.delete(`/subjects/${id}`);
      toast.success('Materia eliminada');
      fetchData();
    } catch (err) {
      toast.error('Error eliminando materia');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold font-heading">Materias</h1>
            <p className="text-muted-foreground mt-2 text-base">Plan de estudios por programa y módulo</p>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Select value={filterProgram} onValueChange={setFilterProgram}>
              <SelectTrigger className="w-56">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filtrar por programa" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los programas</SelectItem>
                {programs.map(p => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={filterModule} onValueChange={setFilterModule}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Módulo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los módulos</SelectItem>
                {availableModules.map(num => (
                  <SelectItem key={num} value={String(num)}>Módulo {num}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={openCreate} size="lg"><Plus className="h-5 w-5" /> Nueva Materia</Button>
          </div>
        </div>

        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Buscar materias por nombre..." 
            className="pl-9" 
            value={searchQuery} 
            onChange={(e) => setSearchQuery(e.target.value)} 
          />
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : filtered.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay materias registradas</p>
          </CardContent></Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filtered.map((subj) => (
              <Card key={subj.id} className="shadow-card hover:shadow-card-hover transition-shadow flex flex-col">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-sm font-heading">{subj.name}</CardTitle>
                    <div className="flex gap-1 shrink-0">
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => openEdit(subj)}><Pencil className="h-3 w-3" /></Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleDelete(subj.id)}><Trash2 className="h-3 w-3 text-destructive" /></Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col">
                  <p className="text-xs text-muted-foreground mb-3 flex-1">{subj.description || 'Sin descripción'}</p>
                  <div className="flex gap-2 mt-auto">
                    <Badge variant="secondary" className="text-xs">Módulo {subj.module_number}</Badge>
                    <Badge variant="outline" className="text-xs">{getProgramName(subj.program_id)}</Badge>
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
            <DialogTitle>{editing ? 'Editar Materia' : 'Nueva Materia'}</DialogTitle>
            <DialogDescription>Completa los datos de la materia</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Nombre</Label>
              <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Nombre de la materia" />
            </div>
            <div className="space-y-2">
              <Label>Programa</Label>
              <Select value={form.program_id} onValueChange={(v) => setForm({ ...form, program_id: v })}>
                <SelectTrigger><SelectValue placeholder="Seleccionar programa" /></SelectTrigger>
                <SelectContent>
                  {programs.map(p => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Módulo</Label>
              <Select value={String(form.module_number)} onValueChange={(v) => setForm({ ...form, module_number: parseInt(v) })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Módulo 1</SelectItem>
                  <SelectItem value="2">Módulo 2</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Descripción (opcional)</Label>
              <Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Breve descripción" />
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
