import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ArrowLeft, Info } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

// ── Legend values ─────────────────────────────────────────────
const SI      = 'SI';       // Yes / approved
const NO      = 'NO';       // No / rejected / not enabled
const NA      = '—';        // Not applicable
const EXP     = 'EXP';      // Expired (admin enabled but teacher never graded)
const GANA    = 'GANA';     // Student passes the module/program
const NO_GANA = 'NO GANA';  // Student fails

/** Passing threshold: average grade ≥ 3.0 → student passes a module */
const PASS_THRESHOLD = 3.0; // eslint-disable-line no-unused-vars

// ── Color helpers ─────────────────────────────────────────────
const cellClass = (val) => {
  if (val === SI)  return 'text-green-700 dark:text-green-400 font-semibold';
  if (val === NO)  return 'text-red-600 dark:text-red-400 font-semibold';
  if (val === EXP) return 'text-orange-600 dark:text-orange-400 font-semibold';
  return 'text-muted-foreground';
};

const estadoBadge = (val) => {
  if (val === GANA) return <Badge className="bg-green-600 hover:bg-green-600 text-white">✅ GANA</Badge>;
  return <Badge variant="destructive">❌ NO GANA</Badge>;
};

// ── All simulation scenarios ──────────────────────────────────
// Columns: #, aprueba1, aprueba2, rec1, rec2, hab1, hab2, ok1, ok2, estado, descripcion
const SCENARIOS = [
  // ── Both pass normally ────────────────────────────────────
  [1,  SI, SI, NA, NA, NA, NA, SI, SI, GANA,    'Aprueba ambas materias normalmente. No se necesita recuperación.'],

  // ── Fails only MAT1 ──────────────────────────────────────
  [2,  NO, SI, NO, NA, NA, NA, NO, SI, NO_GANA, 'Reprueba MAT1. Admin NO habilita la recuperación → reprobado definitivo.'],
  [3,  NO, SI, SI, NA, NO, NA, NO, SI, NO_GANA, 'Reprueba MAT1. Admin SÍ habilita rec. Profesor RECHAZA la recuperación → reprobado.'],
  [4,  NO, SI, SI, NA, EXP,NA, NO, SI, NO_GANA, 'Reprueba MAT1. Admin SÍ habilita rec. Profesor NO califica antes del cierre (plazo vencido) → reprobado.'],
  [5,  NO, SI, SI, NA, SI, NA, SI, SI, GANA,    'Reprueba MAT1. Admin SÍ habilita rec. Profesor APRUEBA la recuperación → gana.'],

  // ── Fails only MAT2 ──────────────────────────────────────
  [6,  SI, NO, NA, NO, NA, NA, SI, NO, NO_GANA, 'Reprueba MAT2. Admin NO habilita la recuperación → reprobado definitivo.'],
  [7,  SI, NO, NA, SI, NA, NO, SI, NO, NO_GANA, 'Reprueba MAT2. Admin SÍ habilita rec. Profesor RECHAZA la recuperación → reprobado.'],
  [8,  SI, NO, NA, SI, NA, EXP,SI, NO, NO_GANA, 'Reprueba MAT2. Admin SÍ habilita rec. Profesor NO califica antes del cierre (plazo vencido) → reprobado.'],
  [9,  SI, NO, NA, SI, NA, SI, SI, SI, GANA,    'Reprueba MAT2. Admin SÍ habilita rec. Profesor APRUEBA la recuperación → gana.'],

  // ── Fails BOTH – admin enables neither ───────────────────
  [10, NO, NO, NO, NO, NA, NA, NO, NO, NO_GANA, 'Reprueba ambas. Admin NO habilita ninguna recuperación → reprobado definitivo.'],

  // ── Fails BOTH – admin enables only MAT1 ─────────────────
  [11, NO, NO, SI, NO, NO, NA, NO, NO, NO_GANA, 'Reprueba ambas. Admin habilita solo REC1. Profesor rechaza REC1. MAT2 sin rec → reprobado.'],
  [12, NO, NO, SI, NO, EXP,NA, NO, NO, NO_GANA, 'Reprueba ambas. Admin habilita solo REC1. Plazo de REC1 vence sin calificar. MAT2 sin rec → reprobado.'],
  [13, NO, NO, SI, NO, SI, NA, SI, NO, NO_GANA, 'Reprueba ambas. Admin habilita solo REC1. Profesor aprueba REC1. MAT2 sin rec → no gana (falta MAT2).'],

  // ── Fails BOTH – admin enables only MAT2 ─────────────────
  [14, NO, NO, NO, SI, NA, NO, NO, NO, NO_GANA, 'Reprueba ambas. Admin habilita solo REC2. Profesor rechaza REC2. MAT1 sin rec → reprobado.'],
  [15, NO, NO, NO, SI, NA, EXP,NO, NO, NO_GANA, 'Reprueba ambas. Admin habilita solo REC2. Plazo de REC2 vence sin calificar. MAT1 sin rec → reprobado.'],
  [16, NO, NO, NO, SI, NA, SI, NO, SI, NO_GANA, 'Reprueba ambas. Admin habilita solo REC2. Profesor aprueba REC2. MAT1 sin rec → no gana (falta MAT1).'],

  // ── Fails BOTH – admin enables BOTH ──────────────────────
  [17, NO, NO, SI, SI, NO, NO, NO, NO, NO_GANA, 'Reprueba ambas. Admin habilita ambas. Profesor rechaza ambas recuperaciones → reprobado.'],
  [18, NO, NO, SI, SI, NO, SI, NO, SI, NO_GANA, 'Reprueba ambas. Admin habilita ambas. Prof rechaza REC1, aprueba REC2 → no gana (falta MAT1).'],
  [19, NO, NO, SI, SI, SI, NO, SI, NO, NO_GANA, 'Reprueba ambas. Admin habilita ambas. Prof aprueba REC1, rechaza REC2 → no gana (falta MAT2).'],
  [20, NO, NO, SI, SI, EXP,EXP,NO, NO, NO_GANA, 'Reprueba ambas. Admin habilita ambas. Plazo vence sin que el prof califique ninguna → reprobado.'],
  [21, NO, NO, SI, SI, SI, EXP,SI, NO, NO_GANA, 'Reprueba ambas. Admin habilita ambas. Prof aprueba REC1, plazo de REC2 vence → no gana.'],
  [22, NO, NO, SI, SI, EXP,SI, NO, SI, NO_GANA, 'Reprueba ambas. Admin habilita ambas. Plazo de REC1 vence, prof aprueba REC2 → no gana.'],
  [23, NO, NO, SI, SI, SI, SI, SI, SI, GANA,    'Reprueba ambas. Admin habilita ambas. Profesor aprueba ambas recuperaciones → GANA.'],
];

const HEADERS = [
  '#',
  'APRUEBA MAT1',
  'APRUEBA MAT2',
  'REC1\n(admin hab.)',
  'REC2\n(admin hab.)',
  'HAB M1\n(prof califica)',
  'HAB M2\n(prof califica)',
  'OK1\n(resultado M1)',
  'OK2\n(resultado M2)',
  'ESTADO',
  'Descripción del caso',
];

export default function RecoverySimulatorPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('all'); // 'all' | 'gana' | 'no'

  const filtered = SCENARIOS.filter(s => {
    if (filter === 'gana') return s[9] === GANA;
    if (filter === 'no')   return s[9] !== GANA;
    return true;
  });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <Button variant="ghost" size="sm" onClick={() => navigate('/admin/recoveries')}>
                <ArrowLeft className="h-4 w-4" />
                Volver a Recuperaciones
              </Button>
            </div>
            <h1 className="text-3xl font-bold font-heading">Tabla de Simulación de Recuperaciones</h1>
            <p className="text-muted-foreground mt-1 text-lg">
              Todos los casos posibles de aprobación, reprobación y recuperación para dos materias (MAT1 y MAT2).
            </p>
          </div>
        </div>

        {/* Legend */}
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            <div className="flex flex-wrap gap-4 mt-1 text-sm">
              <span><span className="text-green-700 dark:text-green-400 font-semibold">SI</span> = Sí / Aprobado / Habilitado</span>
              <span><span className="text-red-600 dark:text-red-400 font-semibold">NO</span> = No / Rechazado / No habilitado</span>
              <span><span className="text-orange-600 dark:text-orange-400 font-semibold">EXP</span> = Plazo vencido sin calificar</span>
              <span><span className="text-muted-foreground font-semibold">—</span> = No aplica</span>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">
              <strong>REC1/REC2</strong>: El admin habilita la recuperación para esa materia.&nbsp;
              <strong>HAB M1/HAB M2</strong>: El profesor califica (aprueba) la recuperación del módulo.&nbsp;
              <strong>OK1/OK2</strong>: Resultado final de cada módulo.
            </p>
          </AlertDescription>
        </Alert>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <Card className="shadow-card">
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold font-heading">{SCENARIOS.length}</p>
              <p className="text-sm text-muted-foreground mt-1">Casos totales</p>
            </CardContent>
          </Card>
          <Card className="shadow-card">
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold font-heading text-green-600">{SCENARIOS.filter(s => s[9] === GANA).length}</p>
              <p className="text-sm text-muted-foreground mt-1">Casos GANA</p>
            </CardContent>
          </Card>
          <Card className="shadow-card">
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold font-heading text-red-600">{SCENARIOS.filter(s => s[9] !== GANA).length}</p>
              <p className="text-sm text-muted-foreground mt-1">Casos NO GANA</p>
            </CardContent>
          </Card>
        </div>

        {/* Filter buttons */}
        <div className="flex gap-2">
          <Button variant={filter === 'all'  ? 'default' : 'outline'} size="sm" onClick={() => setFilter('all')}>
            Todos ({SCENARIOS.length})
          </Button>
          <Button variant={filter === 'gana' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('gana')}>
            Solo GANA ({SCENARIOS.filter(s => s[9] === GANA).length})
          </Button>
          <Button variant={filter === 'no'   ? 'default' : 'outline'} size="sm" onClick={() => setFilter('no')}>
            Solo NO GANA ({SCENARIOS.filter(s => s[9] !== GANA).length})
          </Button>
        </div>

        {/* Main table */}
        <Card className="shadow-card overflow-x-auto">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Casos de prueba ({filtered.length})</CardTitle>
            <CardDescription>
              Simula cada fila ingresando los datos equivalentes en el sistema real para verificar que el resultado coincida.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/50">
                  {HEADERS.map((h, i) => (
                    <TableHead
                      key={i}
                      className="text-center whitespace-pre-line text-xs font-semibold px-3 py-3"
                    >
                      {h}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map(([num, ap1, ap2, r1, r2, h1, h2, ok1, ok2, estado, desc]) => (
                  <TableRow
                    key={num}
                    className={
                      estado === GANA
                        ? 'bg-green-50 dark:bg-green-950/30 hover:bg-green-100 dark:hover:bg-green-950/50'
                        : 'bg-red-50 dark:bg-red-950/20 hover:bg-red-100 dark:hover:bg-red-950/40'
                    }
                  >
                    <TableCell className="text-center font-mono text-xs text-muted-foreground px-3">{num}</TableCell>

                    {/* APRUEBA MAT1 / MAT2 */}
                    <TableCell className={`text-center px-3 ${cellClass(ap1)}`}>{ap1}</TableCell>
                    <TableCell className={`text-center px-3 ${cellClass(ap2)}`}>{ap2}</TableCell>

                    {/* REC1 / REC2 */}
                    <TableCell className={`text-center px-3 ${cellClass(r1)}`}>{r1}</TableCell>
                    <TableCell className={`text-center px-3 ${cellClass(r2)}`}>{r2}</TableCell>

                    {/* HAB M1 / HAB M2 */}
                    <TableCell className={`text-center px-3 ${cellClass(h1)}`}>{h1}</TableCell>
                    <TableCell className={`text-center px-3 ${cellClass(h2)}`}>{h2}</TableCell>

                    {/* OK1 / OK2 */}
                    <TableCell className={`text-center px-3 ${cellClass(ok1)}`}>{ok1}</TableCell>
                    <TableCell className={`text-center px-3 ${cellClass(ok2)}`}>{ok2}</TableCell>

                    {/* ESTADO */}
                    <TableCell className="text-center px-3">{estadoBadge(estado)}</TableCell>

                    {/* Descripción */}
                    <TableCell className="text-xs text-muted-foreground px-3 min-w-[260px]">{desc}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* How-to guide */}
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-lg">¿Cómo usar esta tabla para pruebas?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <ol className="list-decimal list-inside space-y-2">
              <li>Elige un caso de la tabla (por ejemplo el caso <strong>#5</strong>: estudiante reprueba MAT1, admin habilita recuperación y el profesor la aprueba).</li>
              <li>En el sistema, configura las calificaciones del estudiante de modo que <strong>APRUEBA MAT1</strong> y <strong>APRUEBA MAT2</strong> coincidan con la columna (SI = promedio ≥ 3.0 / NO = promedio &lt; 3.0).</li>
              <li>Desde el panel de recuperaciones, el <strong>admin</strong> habilita o no la recuperación según la columna <strong>REC1 / REC2</strong>.</li>
              <li>El <strong>profesor</strong> califica la actividad de recuperación según la columna <strong>HAB M1 / HAB M2</strong> (SI = aprueba, NO = rechaza, EXP = no califica antes del cierre).</li>
              <li>Verifica que <strong>OK1 / OK2</strong> y el <strong>ESTADO</strong> final del estudiante coincidan con lo esperado en la tabla.</li>
            </ol>
            <p className="pt-2 text-xs border-t">
              <strong>Nota:</strong> &quot;GANA&quot; significa que el estudiante aprueba el programa/módulo y puede continuar.
              &quot;NO GANA&quot; significa que queda reprobado o en proceso incompleto de recuperación.
            </p>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
