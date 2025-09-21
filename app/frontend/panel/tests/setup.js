/**
 * Frontend test setup configuration
 */

import { config } from '@vue/test-utils'
import { vi } from 'vitest'
import { createPinia } from 'pinia'

// Global test configuration
config.global.plugins = [createPinia()]

// Mock global objects
// Provide a Jest-compatible global using Vitest's vi
global.jest = vi

global.console = {
  ...console,
  // Suppress console.log in tests
  log: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
}

// Mock fetch for API calls
global.fetch = vi.fn()

// Mock window.location
delete window.location
window.location = {
  href: 'http://localhost:5173',
  origin: 'http://localhost:5173',
  pathname: '/',
  search: '',
  hash: '',
  assign: vi.fn(),
  replace: vi.fn(),
  reload: vi.fn(),
}

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

export default config
