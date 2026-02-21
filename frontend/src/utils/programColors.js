/**
 * Returns a soft pastel background color class based on an index derived from the program id.
 * Colors are nearly white but perceptibly different so users can distinguish programs at a glance.
 */
const PROGRAM_BG_COLORS = [
  'bg-blue-50/80 dark:bg-blue-950/30 border-blue-200/60 dark:border-blue-800/40',
  'bg-green-50/80 dark:bg-green-950/30 border-green-200/60 dark:border-green-800/40',
  'bg-purple-50/80 dark:bg-purple-950/30 border-purple-200/60 dark:border-purple-800/40',
  'bg-amber-50/80 dark:bg-amber-950/30 border-amber-200/60 dark:border-amber-800/40',
  'bg-rose-50/80 dark:bg-rose-950/30 border-rose-200/60 dark:border-rose-800/40',
  'bg-cyan-50/80 dark:bg-cyan-950/30 border-cyan-200/60 dark:border-cyan-800/40',
  'bg-indigo-50/80 dark:bg-indigo-950/30 border-indigo-200/60 dark:border-indigo-800/40',
  'bg-orange-50/80 dark:bg-orange-950/30 border-orange-200/60 dark:border-orange-800/40',
];

/**
 * Given a list of programs and a program_id, returns a consistent soft-color CSS class string.
 * @param {Array} programs - Array of program objects with {id} field
 * @param {string} programId - The program id to look up
 * @returns {string} Tailwind CSS class string for soft background + border
 */
export function getProgramColorClasses(programs, programId) {
  if (!programId || !programs || programs.length === 0) return '';
  const idx = programs.findIndex(p => String(p.id) === String(programId));
  const colorIdx = idx >= 0 ? idx % PROGRAM_BG_COLORS.length : 0;
  return PROGRAM_BG_COLORS[colorIdx];
}
