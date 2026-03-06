/**
 * Safely extracts a human-readable error message from an axios error.
 * Handles Pydantic validation errors (array of objects with {type, loc, msg, input})
 * and regular FastAPI error strings.
 *
 * @param {object} err - The axios error object
 * @param {string} fallback - Fallback message if no detail is found
 * @returns {string} A human-readable error message
 */
export function getErrorMessage(err, fallback = 'Ha ocurrido un error') {
  const detail = err?.response?.data?.detail;

  if (!detail) return fallback;

  // Pydantic validation error: array of objects
  if (Array.isArray(detail)) {
    return (
      detail
        .map((d) => {
          if (typeof d === 'string') return d;
          if (d && typeof d === 'object') {
            const loc = Array.isArray(d.loc)
              ? d.loc.filter((l) => l !== 'body').join(' → ') // 'body' is a FastAPI wrapper, not a useful field name
              : '';
            const msg = d.msg || d.message || JSON.stringify(d);
            return loc ? `${loc}: ${msg}` : msg;
          }
          return String(d);
        })
        .join('; ') || fallback
    );
  }

  // Regular string error
  if (typeof detail === 'string') return detail;

  // Object error (fallback)
  if (typeof detail === 'object') {
    return detail.msg || detail.message || fallback;
  }

  return fallback;
}
