// Debug script for Admin Panel Login Issue
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';
const ADMIN_PANEL_URL = 'http://localhost:5173';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

async function testLoginFlow() {
  console.log('🔍 Debugging Admin Panel Login Issue');
  console.log('=====================================\n');
  
  // Test 1: Check if admin panel is accessible
  console.log('1. 🌐 Testing Admin Panel Accessibility...');
  try {
    const response = await fetch(ADMIN_PANEL_URL);
    if (response.ok) {
      console.log('✅ Admin panel is accessible');
      console.log(`   URL: ${ADMIN_PANEL_URL}`);
      console.log(`   Status: ${response.status} ${response.statusText}`);
    } else {
      console.log('❌ Admin panel is not accessible');
      console.log(`   Status: ${response.status} ${response.statusText}`);
    }
  } catch (error) {
    console.error('❌ Error accessing admin panel:', error.message);
  }
  
  // Test 2: Test login API
  console.log('\n2. 🔐 Testing Login API...');
  try {
    const response = await api.post('/users/login', {
      username_or_email: 'admin',
      password: 'adminpassword'
    });
    
    if (response.status === 200 && response.data.access_token) {
      console.log('✅ Login API working correctly');
      console.log(`   User: ${response.data.user.username} (${response.data.user.role})`);
      console.log(`   Token: ${response.data.access_token.substring(0, 20)}...`);
      console.log(`   Expires in: ${response.data.expires_in} seconds`);
      
      // Test 3: Test token validation
      console.log('\n3. 🔍 Testing Token Validation...');
      const token = response.data.access_token;
      const meResponse = await api.get('/users/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (meResponse.status === 200) {
        console.log('✅ Token validation working');
        console.log(`   User ID: ${meResponse.data.id}`);
        console.log(`   Username: ${meResponse.data.username}`);
        console.log(`   Role: ${meResponse.data.role}`);
      } else {
        console.log('❌ Token validation failed');
      }
      
    } else {
      console.log('❌ Login API failed');
      console.log(`   Status: ${response.status}`);
      console.log(`   Data: ${JSON.stringify(response.data)}`);
    }
  } catch (error) {
    console.error('❌ Login API error:', error.message);
    if (error.response) {
      console.error(`   Status: ${error.response.status}`);
      console.error(`   Data: ${JSON.stringify(error.response.data)}`);
    }
  }
  
  // Test 4: Check localStorage simulation
  console.log('\n4. 💾 Testing localStorage Simulation...');
  try {
    const response = await api.post('/users/login', {
      username_or_email: 'admin',
      password: 'adminpassword'
    });
    
    if (response.data.access_token) {
      const token = response.data.access_token;
      console.log('✅ Simulating localStorage.setItem("access_token", token)');
      console.log(`   Token length: ${token.length}`);
      console.log(`   Token starts with: ${token.substring(0, 20)}...`);
      
      // Test if token can be retrieved
      console.log('✅ Simulating localStorage.getItem("access_token")');
      console.log(`   Retrieved token: ${token.substring(0, 20)}...`);
    }
  } catch (error) {
    console.error('❌ localStorage simulation error:', error.message);
  }
  
  console.log('\n📋 Debug Summary:');
  console.log('==================');
  console.log('✅ Admin Panel URL: http://localhost:5173');
  console.log('✅ Login Credentials: admin / adminpassword');
  console.log('✅ Expected Behavior: After login, modal should close and show dashboard');
  console.log('✅ Current Issue: Page stays on login modal after successful authentication');
  
  console.log('\n🔧 Debugging Steps:');
  console.log('1. Open browser console (F12)');
  console.log('2. Go to http://localhost:5173');
  console.log('3. Try to login with admin/adminpassword');
  console.log('4. Check console logs for authentication state changes');
  console.log('5. Look for any JavaScript errors');
  
  console.log('\n🎯 Expected Console Logs:');
  console.log('- "App: Initializing auth state"');
  console.log('- "Auth store: Starting login process"');
  console.log('- "Auth store: API response received: {...}"');
  console.log('- "Auth store: Setting authentication state"');
  console.log('- "Auth store: Authentication state updated: {...}"');
  console.log('- "App: Authentication state changed: {...}"');
  console.log('- "Login successful, closing modal and redirecting..."');
}

testLoginFlow();
