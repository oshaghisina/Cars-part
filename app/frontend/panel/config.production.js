// Production configuration for Admin Panel
// This file should be used when building for production deployment

export const productionConfig = {
  // API Base URL for production server
  API_BASE_URL: 'http://5.223.59.155/api/v1',
  
  // Other production settings
  APP_TITLE: 'China Car Parts - Admin Panel',
  DEBUG: false
}

// Instructions for deployment:
// 1. Set VITE_API_BASE_URL=http://5.223.59.155/api/v1 in your production environment
// 2. Or modify the client.js to use this configuration
// 3. Build with: npm run build:panel
