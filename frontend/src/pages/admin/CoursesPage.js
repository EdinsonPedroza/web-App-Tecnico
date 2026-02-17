import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import { Plus, Pencil, Trash2, Loader2, ClipboardList, Users, BookOpen, Search } from 'lucide-react';
import api from '@/lib/api';

export default function CoursesPage() {
  const [courses, setCourses] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ 
    name: '', 
    program_id: '', 
    subject_id: '',  // Keep for backward compatibility
    subject_ids: [],  // Multiple subjects
    year: new Date().getFullYear(), 
    month: 'Enero',
    student_ids: [],
    start_date: '',
    end_date: '',
    module_dates: {}  // e.g., {"1": {"start": "2026-01-01", "end": "2026-06-30"}}
  });
  const [saving, setSaving] = useState(false);
  const [subjectSearch, setSubjectSearch] = useState('');
  const [studentSearch, setStudentSearch] = useState('');

  const fetchData = useCallback(async () => {
    try {
      const [cRes, pRes, sRes, tRes, stRes] = await Promise.all([
        api.get('/courses'), api.get('/programs'), api.get('/subjects'),
        api.get('/users?role=profesor'), api.get('/users?role=estudiante')
      ]);
      setCourses(cRes.data); setPrograms(pRes.data); setSubjects(sRes.data);
      setTeachers(tRes.data); setStudents(stRes.data);
    } catch (err) {
      toast.error('Error cargando datos');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const getName = (arr, id) => arr.find(i => i.id === id)?.name || '-';
  const filteredSubjects = form.program_id ? subjects.filter(s => String(s.program_id) === String(form.program_id)) : subjects;
  
  // Get the selected program to determine module count
  const selectedProgram = programs.find(p => p.id === form.program_id);
  const moduleCount = selectedProgram?.modules?.length || 0;
  
  const formatGrupoSuggestion = (month, year, programId) => {
    if (!month || !year || !programId) return '';
    const programName = getName(programs, programId);
    if (!programName || programName === '-') return '';
    const lastTwoWords = programName.split(' ').slice(-2).join(' ').toUpperCase();
    return `${month.toUpperCase()}-${year} - ${lastTwoWords}`;
  };

  const openCreate = () => {
    setEditing(null);
    setForm({ 
      name: '', 
      program_id: '', 
      subject_id: '',  // Keep for backward compatibility
      subject_ids: [],  // Multiple subjects
      year: new Date().getFullYear(), 
      month: 'Enero',
      student_ids: [],
      start_date: '',
      end_date: '',
      module_dates: {}
    });
    setSubjectSearch('');
    setStudentSearch('');
    setDialogOpen(true);
  };

  const openEdit = (course) => {
    setEditing(course);
    // Extract month and year from course name if possible
    const monthMatch = course.name.match(/(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)/i);
    const yearMatch = course.name.match(/\d{4}/);
    setForm({ 
      name: course.name, 
      program_id: course.program_id, 
      subject_id: course.subject_id || '',  // Backward compatibility
      subject_ids: course.subject_ids || (course.subject_id ? [course.subject_id] : []),  // Convert single to array
      year: yearMatch ? parseInt(yearMatch[0]) : new Date().getFullYear(),
      month: monthMatch ? monthMatch[0] : 'Enero',
      student_ids: course.student_ids || [],
      start_date: course.start_date || '',
      end_date: course.end_date || '',
      module_dates: course.module_dates || {}
    });
    setSubjectSearch('');
    setStudentSearch('');
    setDialogOpen(true);
  };

  const toggleStudent = (studentId) => {
    setForm(prev => ({
      ...prev,
      student_ids: prev.student_ids.includes(studentId)
        ? prev.student_ids.filter(id => id !== studentId)
        : [...prev.student_ids, studentId]
    }));
  };

  const handleSave = async () => {
    if (!form.name.trim()) { toast.error('Nombre del curso requerido'); return; }
    if (form.subject_ids.length === 0) { toast.error('Debes seleccionar al menos una materia'); return; }
    setSaving(true);
    try {
      const saveData = {
        name: form.name,
        subject_ids: form.subject_ids,
        student_ids: form.student_ids,
        start_date: form.start_date || null,
        end_date: form.end_date || null,
        module_dates: form.module_dates || {}
      };
      
      if (editing) {
        await api.put(`/courses/${editing.id}`, saveData);
        toast.success('Curso actualizado');
      } else {
        await api.post('/courses', {
          ...saveData,
          program_id: form.program_id,
          subject_id: form.subject_ids[0] || null,  // For backward compatibility, use first subject
          year: form.year
        });
        toast.success('Curso creado');
      }
      setDialogOpen(false);
      fetchData();
    } catch (err) {
      toast.error('Error guardando curso: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este curso?')) return;
    try { await api.delete(`/courses/${id}`); toast.success('Curso eliminado'); fetchData(); }
    catch (err) { toast.error('Error eliminando curso'); }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold font-heading">Grupos</h1>
            <p className="text-muted-foreground mt-1 text-xl">Gestiona grupos por programa, materia y cohorte</p>
          </div>
          <Button onClick={openCreate} size="lg"><Plus className="h-5 w-5" /> Nuevo Grupo</Button>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : courses.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <ClipboardList className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay grupos creados</p>
          </CardContent></Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {courses.map((c) => (
              <Card key={c.id} className="shadow-card hover:shadow-card-hover transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-sm font-heading">{c.name}</CardTitle>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => openEdit(c)}><Pencil className="h-3 w-3" /></Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleDelete(c.id)}><Trash2 className="h-3 w-3 text-destructive" /></Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <BookOpen className="h-4 w-4" />
                      <span className="truncate">{getName(programs, c.program_id)}</span>
                    </div>
                    {c.subject_ids && c.subject_ids.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {c.subject_ids.map(subjectId => (
                          <Badge key={subjectId} variant="secondary" className="text-xs">
                            {getName(subjects, subjectId)}
                          </Badge>
                        ))}
                      </div>
                    )}
                    <div className="flex gap-2 flex-wrap pt-1">
                      <Badge variant="secondary">{c.year}</Badge>
                      <Badge variant="outline">{c.student_ids?.length || 0} estudiantes</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl">{editing ? 'Editar Grupo' : 'Nuevo Grupo'}</DialogTitle>
            <DialogDescription className="text-base">Configura el grupo y asigna estudiantes y materias</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {!editing && (
              <>
                <div className="space-y-2">
                  <Label className="text-base">Programa</Label>
                  <Select value={form.program_id} onValueChange={(v) => {
                    if (form.subject_ids.length > 0) {
                      if (window.confirm('¿Cambiar el programa borrará las materias seleccionadas. Continuar?')) {
                        setForm({ ...form, program_id: v, subject_ids: [] });
                      }
                    } else {
                      setForm({ ...form, program_id: v, subject_ids: [] });
                    }
                  }}>
                    <SelectTrigger><SelectValue placeholder="Seleccionar programa" /></SelectTrigger>
                    <SelectContent>{programs.map(p => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
              </>
            )}
            {/* Subject Selection - Show for both create and edit */}
            {form.program_id && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label className="text-base">Materias del Grupo ({form.subject_ids.length} seleccionadas)</Label>
                  {filteredSubjects.length > 0 && (
                    <Button 
                      type="button" 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => {
                        if (form.subject_ids.length === filteredSubjects.length) {
                          setForm({ ...form, subject_ids: [] });
                        } else {
                          setForm({ ...form, subject_ids: filteredSubjects.map(s => s.id) });
                        }
                      }}
                    >
                      {form.subject_ids.length === filteredSubjects.length ? 'Deseleccionar todas' : 'Seleccionar todas'}
                    </Button>
                  )}
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input 
                    placeholder="Buscar materias..." 
                    value={subjectSearch}
                    onChange={(e) => setSubjectSearch(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <div className="max-h-48 overflow-y-auto rounded-lg border p-3 space-y-2">
                  {filteredSubjects.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No hay materias para este programa</p>
                  ) : (
                    filteredSubjects
                      .filter(s => (s.name || '').toLowerCase().includes(subjectSearch.toLowerCase()))
                      .map((s) => (
                        <div key={s.id} className="flex items-center gap-2">
                          <Checkbox 
                            checked={form.subject_ids.includes(s.id)} 
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setForm({ ...form, subject_ids: [...form.subject_ids, s.id] });
                              } else {
                                setForm({ ...form, subject_ids: form.subject_ids.filter(id => id !== s.id) });
                              }
                            }}
                          />
                          <span className="text-sm">{s.name || 'Sin nombre'} <span className="text-muted-foreground">(Módulo {s.module_number})</span></span>
                        </div>
                      ))
                  )}
                </div>
              </div>
            )}
            {!editing && (
              <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-base">Mes</Label>
                    <Select value={form.month} onValueChange={(v) => {
                      if (v && form.year) {
                        const newName = `${v.toUpperCase()}-${form.year}`;
                        setForm({ ...form, month: v, name: newName });
                      } else {
                        setForm({ ...form, month: v });
                      }
                    }}>
                      <SelectTrigger><SelectValue placeholder="Seleccionar mes" /></SelectTrigger>
                      <SelectContent>
                        {['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'].map(m => (
                          <SelectItem key={m} value={m}>{m}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-base">Año</Label>
                    <Input 
                      type="number" 
                      value={form.year} 
                      onChange={(e) => {
                        const newYear = parseInt(e.target.value) || new Date().getFullYear();
                        if (form.month && newYear) {
                          const newName = `${form.month.toUpperCase()}-${newYear}`;
                          setForm({ ...form, year: newYear, name: newName });
                        } else {
                          setForm({ ...form, year: newYear });
                        }
                      }} 
                      placeholder="2026"
                      min="2024"
                      max="2030"
                    />
                  </div>
                </div>
            )}
            <div className="space-y-2">
              <Label className="text-base">Nombre del Grupo (Auto-generado)</Label>
              <Input 
                value={form.name} 
                onChange={(e) => setForm({ ...form, name: e.target.value })} 
                placeholder="Ej: ENERO-2026"
                readOnly={!editing}
                className={!editing ? 'bg-muted/30' : ''}
              />
              <p className="text-xs text-muted-foreground">
                {!editing ? 'Se genera automáticamente al seleccionar mes y año' : 'Puedes editar el nombre del grupo'}
              </p>
            </div>
            {/* Module Dates - Show only if a program is selected and it has modules */}
            {form.program_id && moduleCount > 0 && (
              <div className="space-y-3">
                <Label className="text-base">Fechas de Inicio y Cierre por Módulo</Label>
                <div className="rounded-lg border p-4 space-y-4 bg-muted/20">
                  {Array(moduleCount).fill().map((_, i) => {
                    const moduleNum = i + 1;
                    return (
                      <div key={moduleNum} className="space-y-2">
                        <p className="text-sm font-semibold text-foreground">Módulo {moduleNum}</p>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="space-y-1">
                            <Label className="text-xs">Fecha Inicio</Label>
                            <Input 
                              type="date" 
                              value={form.module_dates[moduleNum]?.start || ''} 
                              onChange={(e) => {
                                const newModuleDates = { ...form.module_dates };
                                if (!newModuleDates[moduleNum]) newModuleDates[moduleNum] = {};
                                newModuleDates[moduleNum].start = e.target.value;
                                setForm({ ...form, module_dates: newModuleDates });
                              }} 
                              placeholder="Fecha de inicio" 
                            />
                          </div>
                          <div className="space-y-1">
                            <Label className="text-xs">Fecha Cierre</Label>
                            <Input 
                              type="date" 
                              value={form.module_dates[moduleNum]?.end || ''} 
                              onChange={(e) => {
                                const newModuleDates = { ...form.module_dates };
                                if (!newModuleDates[moduleNum]) newModuleDates[moduleNum] = {};
                                newModuleDates[moduleNum].end = e.target.value;
                                setForm({ ...form, module_dates: newModuleDates });
                              }} 
                              placeholder="Fecha de cierre" 
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <p className="text-xs text-muted-foreground">
                  Define el período de cada módulo para este grupo
                </p>
              </div>
            )}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-base">Estudiantes Inscritos ({form.student_ids.length} seleccionados)</Label>
                {students.length > 0 && (
                  <Button 
                    type="button" 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => {
                      if (form.student_ids.length === students.length) {
                        setForm({ ...form, student_ids: [] });
                      } else {
                        setForm({ ...form, student_ids: students.map(s => s.id) });
                      }
                    }}
                  >
                    {form.student_ids.length === students.length ? 'Deseleccionar todos' : 'Seleccionar todos'}
                  </Button>
                )}
              </div>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input 
                  placeholder="Buscar estudiantes por nombre o cédula..." 
                  value={studentSearch}
                  onChange={(e) => setStudentSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
              <div className="max-h-48 overflow-y-auto rounded-lg border p-4 space-y-2.5">
                {students.length === 0 ? <p className="text-sm text-muted-foreground">No hay estudiantes</p> : students
                  .filter(s => 
                    (s.name || '').toLowerCase().includes(studentSearch.toLowerCase()) || 
                    (s.cedula && s.cedula.includes(studentSearch))
                  )
                  .map((s) => (
                  <div key={s.id} className="flex items-center gap-2.5">
                    <Checkbox checked={form.student_ids.includes(s.id)} onCheckedChange={() => toggleStudent(s.id)} />
                    <span className="text-sm">{s.name || 'Sin nombre'} <span className="text-muted-foreground">({s.cedula}) - Módulo {s.module}</span></span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
            <Button onClick={handleSave} disabled={saving}>{saving && <Loader2 className="h-4 w-4 animate-spin" />}{editing ? 'Actualizar' : 'Crear'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
