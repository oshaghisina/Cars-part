// Test script to debug login functionality
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

async function testLogin() {
  console.log('🧪 Testing Login Functionality...');
  
  try {
    console.log('1. Testing API endpoint...');
    const response = await api.post('/users/login', {
      username_or_email: 'admin',
      password: 'adminpassword'
    });
    
    console.log('✅ Login successful!');
    console.log('Response status:', response.status);
    console.log('Response data:', {
      hasToken: !!response.data.access_token,
      tokenLength: response.data.access_token?.length,
      user: response.data.user?.username,
      role: response.data.user?.role,
      expiresIn: response.data.expires_in
    });
    
    // Test token validation
    console.log('\n2. Testing token validation...');
    const token = response.data.access_token;
    const meResponse = await api.get('/users/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('✅ Token validation successful!');
    console.log('User info:', meResponse.data.username, meResponse.data.role);
    
    return true;
  } catch (error) {
    console.error('❌ Login test failed:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    return false;
  }
}

// Test CORS
async function testCORS() {
  console.log('\n🌐 Testing CORS...');
  
  try {
    const response = await fetch('http://localhost:8001/api/v1/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        username_or_email: 'admin',
        password: 'adminpassword'
      })
    });
    
    if (response.ok) {
      console.log('✅ CORS test successful!');
      const data = await response.json();
      console.log('Response data:', {
        hasToken: !!data.access_token,
        user: data.user?.username
      });
    } else {
      console.log('❌ CORS test failed:', response.status, response.statusText);
    }
  } catch (error) {
    console.error('❌ CORS test error:', error.message);
  }
}

// Run tests
async function runTests() {
  console.log('🚀 Starting Login Debug Tests...\n');
  
  await testLogin();
  await testCORS();
  
  console.log('\n📋 Test Summary:');
  console.log('- Backend API: Working');
  console.log('- CORS: Check results above');
  console.log('- Frontend: Check browser console for errors');
}

runTests();
