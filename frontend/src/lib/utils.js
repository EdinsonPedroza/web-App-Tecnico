import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"
import { format, formatDistance, formatRelative } from 'date-fns';
import { es } from 'date-fns/locale';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Format a date to a beautiful Spanish format
 * @param {string|Date} date - The date to format
 * @param {string} formatStr - The format string (default: 'PPP')
 * @returns {string} - Formatted date
 */
export function formatDate(date, formatStr = 'PPP') {
  if (!date) return '-';
  try {
    return format(new Date(date), formatStr, { locale: es });
  } catch (error) {
    console.error('Error formatting date:', error);
    return '-';
  }
}

/**
 * Format a date with time in a beautiful Spanish format
 * @param {string|Date} date - The date to format
 * @returns {string} - Formatted date with time
 */
export function formatDateTime(date) {
  if (!date) return '-';
  try {
    return format(new Date(date), "PPP 'a las' p", { locale: es });
  } catch (error) {
    console.error('Error formatting date:', error);
    return '-';
  }
}

/**
 * Format a date relative to now (e.g., "hace 2 días")
 * @param {string|Date} date - The date to format
 * @returns {string} - Formatted relative date
 */
export function formatRelativeDate(date) {
  if (!date) return '-';
  try {
    return formatDistance(new Date(date), new Date(), { addSuffix: true, locale: es });
  } catch (error) {
    console.error('Error formatting date:', error);
    return '-';
  }
}

/**
 * Format a short date (e.g., "15 Feb 2026")
 * @param {string|Date} date - The date to format
 * @returns {string} - Formatted short date
 */
export function formatShortDate(date) {
  if (!date) return '-';
  try {
    return format(new Date(date), 'd MMM yyyy', { locale: es });
  } catch (error) {
    console.error('Error formatting date:', error);
    return '-';
  }
}

/**
 * Format date for input fields (YYYY-MM-DD)
 * @param {string|Date} date - The date to format
 * @returns {string} - Formatted date for inputs
 */
export function formatInputDate(date) {
  if (!date) return '';
  try {
    return format(new Date(date), 'yyyy-MM-dd');
  } catch (error) {
    console.error('Error formatting date:', error);
    return '';
  }
}
