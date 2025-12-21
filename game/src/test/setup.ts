import { afterEach } from 'vitest';

// Cleanup after each test
afterEach(() => {
  // Cleanup DOM after each test
  document.body.innerHTML = '';
});
