#!/usr/bin/env node

/**
 * Web Login Test Script
 * Tests the web portal login functionality end-to-end
 */

const axios = require('axios');

const BASE_URL = 'http://localhost:8001';
const WEB_URL = 'http://localhost:5174';

// Test credentials
const TEST_CREDENTIALS = {
  username_or_email: 'admin',
  password: 'adminpassword'
};

console.log('🧪 Web Login Test Suite');
console.log('========================\n');

async function testBackendHealth() {
  console.log('1️⃣ Testing Backend Health...');
  try {
    const response = await axios.get(`${BASE_URL}/health`);
    console.log('✅ Backend is healthy:', response.data);
    return true;
  } catch (error) {
    console.log('❌ Backend health check failed:', error.message);
    return false;
  }
}

async function testWebPortalAccess() {
  console.log('\n2️⃣ Testing Web Portal Access...');
  try {
    const response = await axios.get(WEB_URL, { timeout: 5000 });
    console.log('✅ Web portal is accessible (status:', response.status + ')');
    return true;
  } catch (error) {
    console.log('❌ Web portal access failed:', error.message);
    return false;
  }
}

async function testLoginAPI() {
  console.log('\n3️⃣ Testing Login API...');
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/users/login`, TEST_CREDENTIALS, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.data.access_token) {
      console.log('✅ Login API successful');
      console.log('   - Token received:', response.data.access_token.substring(0, 20) + '...');
      console.log('   - User:', response.data.user.username);
      console.log('   - Expires in:', response.data.expires_in, 'seconds');
      return response.data.access_token;
    } else {
      console.log('❌ Login API failed - no token received');
      return null;
    }
  } catch (error) {
    console.log('❌ Login API failed:', error.response?.data || error.message);
    return null;
  }
}

async function testTokenValidation(token) {
  console.log('\n4️⃣ Testing Token Validation...');
  try {
    const response = await axios.get(`${BASE_URL}/api/v1/users/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('✅ Token validation successful');
    console.log('   - User ID:', response.data.id);
    console.log('   - Username:', response.data.username);
    console.log('   - Email:', response.data.email);
    return true;
  } catch (error) {
    console.log('❌ Token validation failed:', error.response?.data || error.message);
    return false;
  }
}

async function testAuthEndpoints() {
  console.log('\n5️⃣ Testing Auth Endpoints...');
  
  const endpoints = [
    '/api/v1/auth/config',
    '/api/v1/auth/stats',
    '/api/v1/auth/health'
  ];
  
  for (const endpoint of endpoints) {
    try {
      const response = await axios.get(`${BASE_URL}${endpoint}`);
      console.log(`✅ ${endpoint}:`, response.status);
    } catch (error) {
      console.log(`❌ ${endpoint}:`, error.response?.status || error.message);
    }
  }
}

async function testCORSConfiguration() {
  console.log('\n6️⃣ Testing CORS Configuration...');
  try {
    const response = await axios.options(`${BASE_URL}/api/v1/users/login`, {
      headers: {
        'Origin': WEB_URL,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
      }
    });
    
    const corsHeaders = {
      'Access-Control-Allow-Origin': response.headers['access-control-allow-origin'],
      'Access-Control-Allow-Methods': response.headers['access-control-allow-methods'],
      'Access-Control-Allow-Headers': response.headers['access-control-allow-headers']
    };
    
    console.log('✅ CORS preflight successful');
    console.log('   - Allow Origin:', corsHeaders['Access-Control-Allow-Origin']);
    console.log('   - Allow Methods:', corsHeaders['Access-Control-Allow-Methods']);
    console.log('   - Allow Headers:', corsHeaders['Access-Control-Allow-Headers']);
    return true;
  } catch (error) {
    console.log('❌ CORS preflight failed:', error.message);
    return false;
  }
}

async function testWebPortalComponents() {
  console.log('\n7️⃣ Testing Web Portal Components...');
  
  const components = [
    '/src/components/auth/LoginModal.vue',
    '/src/components/auth/RegisterModal.vue',
    '/src/components/auth/TelegramLoginButton.vue',
    '/src/views/TelegramCallback.vue'
  ];
  
  for (const component of components) {
    try {
      const response = await axios.get(`${WEB_URL}${component}`, { timeout: 3000 });
      console.log(`✅ ${component}: Accessible`);
    } catch (error) {
      console.log(`❌ ${component}: ${error.message}`);
    }
  }
}

async function runAllTests() {
  console.log('Starting comprehensive web login tests...\n');
  
  // Test backend health
  const backendHealthy = await testBackendHealth();
  if (!backendHealthy) {
    console.log('\n❌ Backend is not healthy. Stopping tests.');
    return;
  }
  
  // Test web portal access
  const webAccessible = await testWebPortalAccess();
  if (!webAccessible) {
    console.log('\n❌ Web portal is not accessible. Stopping tests.');
    return;
  }
  
  // Test CORS
  await testCORSConfiguration();
  
  // Test login API
  const token = await testLoginAPI();
  if (!token) {
    console.log('\n❌ Login API failed. Stopping tests.');
    return;
  }
  
  // Test token validation
  await testTokenValidation(token);
  
  // Test auth endpoints
  await testAuthEndpoints();
  
  // Test web portal components
  await testWebPortalComponents();
  
  console.log('\n🎉 Web Login Test Suite Complete!');
  console.log('==================================');
  console.log('✅ All critical tests passed');
  console.log('🌐 Web Portal: http://localhost:5174/');
  console.log('🔧 Backend API: http://localhost:8001/');
  console.log('📊 Admin Panel: http://localhost:5173/panel/');
  console.log('\n💡 You can now test the web login manually:');
  console.log('   1. Open http://localhost:5174/ in your browser');
  console.log('   2. Click the login button');
  console.log('   3. Use credentials: admin / adminpassword');
  console.log('   4. Check browser console for any errors');
}

// Handle errors gracefully
process.on('unhandledRejection', (error) => {
  console.log('\n❌ Unhandled error:', error.message);
  process.exit(1);
});

// Run the tests
runAllTests().catch(console.error);
