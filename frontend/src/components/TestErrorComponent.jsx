import React from 'react';

/**
 * Test component that intentionally throws an error
 * Use this to test the ErrorBoundary component
 * 
 * To test:
 * 1. Temporarily import and add this component to a route in App.js
 * 2. Navigate to that route
 * 3. The ErrorBoundary should catch the error and display fallback UI
 * 4. Remove this component after testing
 */
function TestErrorComponent({ errorType = 'render' }) {
  if (errorType === 'render') {
    // Simulate a rendering error
    throw new Error('Test Error: This is a simulated rendering error for testing ErrorBoundary');
  }

  if (errorType === 'chunk') {
    // Simulate a chunk loading error
    const error = new Error('Loading chunk 5 failed');
    error.name = 'ChunkLoadError';
    throw error;
  }

  return (
    <div>
      <h1>Test Component</h1>
      <button onClick={() => {
        throw new Error('Test Error: Button click error');
      }}>
        Throw Error on Click
      </button>
    </div>
  );
}

export default TestErrorComponent;
