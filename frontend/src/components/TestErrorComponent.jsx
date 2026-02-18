import React from 'react';

/**
 * Test component that intentionally throws an error
 * Use this to test the ErrorBoundary component
 * 
 * IMPORTANT: ErrorBoundary only catches errors during:
 * - Rendering
 * - Lifecycle methods
 * - Constructors of child components
 * 
 * ErrorBoundary does NOT catch errors in:
 * - Event handlers (use try-catch for those)
 * - Asynchronous code (setTimeout, promises)
 * - Server-side rendering
 * - Errors thrown in the ErrorBoundary itself
 * 
 * To test:
 * 1. Temporarily import and add this component to a route in App.js
 * 2. Navigate to that route
 * 3. The ErrorBoundary should catch the error and display fallback UI
 * 4. Remove this component after testing
 */
function TestErrorComponent({ errorType = 'render' }) {
  if (errorType === 'render') {
    // Simulate a rendering error - THIS WILL BE CAUGHT by ErrorBoundary
    throw new Error('Test Error: This is a simulated rendering error for testing ErrorBoundary');
  }

  if (errorType === 'chunk') {
    // Simulate a chunk loading error - THIS WILL BE CAUGHT by ErrorBoundary
    const error = new Error('Loading chunk 5 failed');
    error.name = 'ChunkLoadError';
    throw error;
  }

  return (
    <div>
      <h1>Test Component</h1>
      <p>Note: The button below will NOT be caught by ErrorBoundary because errors in event handlers must be handled with try-catch.</p>
      <button onClick={() => {
        // This error will NOT be caught by ErrorBoundary
        // Event handler errors need to be caught with try-catch
        try {
          throw new Error('Test Error: Button click error');
        } catch (error) {
          console.error('Caught error in event handler:', error);
          alert('Error in event handler (not caught by ErrorBoundary): ' + error.message);
        }
      }}>
        Test Event Handler Error
      </button>
    </div>
  );
}

export default TestErrorComponent;
