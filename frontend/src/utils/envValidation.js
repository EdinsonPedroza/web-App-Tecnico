/**
 * Environment Validation Utility
 * 
 * Validates that critical environment variables are properly configured.
 * Helps detect configuration issues early before they cause blank screens.
 */

/**
 * Detects if an error is a chunk loading error
 * @param {Error} error - The error to check
 * @returns {boolean} True if it's a chunk loading error
 */
export function isChunkError(error) {
  if (!error) return false;

  // Check error name
  if (error.name === 'ChunkLoadError') {
    return true;
  }

  // Check error message for chunk-related keywords
  const message = error.message?.toLowerCase() || '';
  return message.includes('chunk') ||
         message.includes('loading css') ||
         message.includes('loading js') ||
         message.includes('failed to fetch dynamically imported module') ||
         message.includes('dynamically imported module') ||
         message.includes('importing a module script failed');
}

/**
 * Validates the backend URL configuration
 * @returns {Object} Validation result with isValid flag and optional error message
 */
export function validateBackendUrl() {
  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Backend URL is optional - if empty, the app uses relative URLs (nginx proxy)
  // So we only validate if it's provided
  if (!backendUrl || backendUrl.trim() === '') {
    return {
      isValid: true,
      message: 'Using relative URLs (nginx proxy mode)',
      url: null,
    };
  }

  // Check if URL seems valid
  const trimmedUrl = backendUrl.trim();
  
  // Validate URL format using URL constructor for robust validation
  // Note: If no protocol is specified, we assume https:// for validation
  // Runtime behavior will depend on how ensureProtocol() handles the URL
  try {
    // Try to construct URL - will throw if invalid
    // Add https if no protocol specified (matches ensureProtocol behavior)
    const urlToTest = trimmedUrl.startsWith('http') ? trimmedUrl : `https://${trimmedUrl}`;
    new URL(urlToTest);
  } catch (error) {
    return {
      isValid: false,
      message: `REACT_APP_BACKEND_URL has invalid format: "${trimmedUrl}"`,
      url: trimmedUrl,
    };
  }

  return {
    isValid: true,
    message: 'Backend URL configured',
    url: trimmedUrl,
  };
}

/**
 * Validates all critical environment variables
 * @returns {Object} Validation results
 */
export function validateEnvironment() {
  const results = {
    backendUrl: validateBackendUrl(),
  };

  const allValid = Object.values(results).every(r => r.isValid);

  return {
    isValid: allValid,
    results,
  };
}

/**
 * Logs environment configuration details (safe for production)
 */
export function logEnvironmentInfo() {
  if (process.env.NODE_ENV === 'development') {
    console.log('=== Environment Configuration ===');
    console.log('NODE_ENV:', process.env.NODE_ENV);
    console.log('REACT_APP_BACKEND_URL:', process.env.REACT_APP_BACKEND_URL || '(empty - using relative URLs)');
    console.log('================================');
  }
}
