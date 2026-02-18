/**
 * Ensures a URL has a protocol prefix
 * @param {string} url - The URL to process
 * @returns {string} - The URL with protocol (https:// if missing)
 */
export function ensureProtocol(url) {
  if (!url || url.toLowerCase().startsWith('http')) {
    return url;
  }
  return `https://${url}`;
}
