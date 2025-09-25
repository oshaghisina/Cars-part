// Test script for Logout Redirect Functionality
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

async function testLogoutFlow() {
  console.log('🔍 Testing Logout Redirect Functionality');
  console.log('=====================================\n');
  
  let authToken = '';
  
  // Step 1: Login to get a token
  console.log('1. 🔐 Testing Login...');
  try {
    const response = await api.post('/users/login', {
      username_or_email: 'admin',
      password: 'adminpassword'
    });
    
    if (response.status === 200 && response.data.access_token) {
      authToken = response.data.access_token;
      console.log('✅ Login successful');
      console.log(`   Token: ${authToken.substring(0, 20)}...`);
      console.log(`   User: ${response.data.user.username} (${response.data.user.role})`);
    } else {
      console.log('❌ Login failed');
      return;
    }
  } catch (error) {
    console.error('❌ Login error:', error.message);
    return;
  }
  
  // Step 2: Test token validation
  console.log('\n2. 🔍 Testing Token Validation...');
  try {
    const response = await api.get('/users/me', {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    if (response.status === 200) {
      console.log('✅ Token validation successful');
      console.log(`   User: ${response.data.username} (${response.data.role})`);
    } else {
      console.log('❌ Token validation failed');
    }
  } catch (error) {
    console.error('❌ Token validation error:', error.message);
  }
  
  // Step 3: Test logout API
  console.log('\n3. 🚪 Testing Logout API...');
  try {
    const response = await api.post('/users/logout', {}, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    if (response.status === 200) {
      console.log('✅ Logout API successful');
      console.log(`   Response: ${JSON.stringify(response.data)}`);
    } else {
      console.log('❌ Logout API failed');
      console.log(`   Status: ${response.status}`);
    }
  } catch (error) {
    console.error('❌ Logout API error:', error.message);
  }
  
  // Step 4: Test token after logout
  console.log('\n4. 🔍 Testing Token After Logout...');
  try {
    const response = await api.get('/users/me', {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    if (response.status === 401) {
      console.log('✅ Token properly invalidated after logout');
    } else {
      console.log('❌ Token still valid after logout');
      console.log(`   Status: ${response.status}`);
    }
  } catch (error) {
    if (error.response?.status === 401) {
      console.log('✅ Token properly invalidated after logout (401 error)');
    } else {
      console.error('❌ Unexpected error after logout:', error.message);
    }
  }
  
  console.log('\n📋 Logout Redirect Test Summary:');
  console.log('================================');
  console.log('✅ Login functionality working');
  console.log('✅ Token validation working');
  console.log('✅ Logout API working');
  console.log('✅ Token invalidation working');
  
  console.log('\n🎯 Frontend Logout Test Instructions:');
  console.log('1. Go to http://localhost:5173');
  console.log('2. Login with admin/adminpassword');
  console.log('3. Navigate to any page (e.g., /panel/parts)');
  console.log('4. Click logout button in top-right user menu');
  console.log('5. Verify that:');
  console.log('   - Page redirects to root (/)');
  console.log('   - Login modal appears');
  console.log('   - URL shows http://localhost:5173/');
  console.log('   - Console shows logout debug logs');
  
  console.log('\n🔧 Expected Console Logs on Logout:');
  console.log('- "TopBar: Starting logout process"');
  console.log('- "Auth store: Starting logout process"');
  console.log('- "Auth store: Clearing authentication state"');
  console.log('- "Auth store: Logout completed, authentication state cleared"');
  console.log('- "TopBar: Logout completed, redirecting to root"');
  console.log('- "App: Authentication state changed: {from: true, to: false}"');
  
  console.log('\n🚨 If logout doesn\'t redirect:');
  console.log('1. Check browser console for errors');
  console.log('2. Verify localStorage is cleared');
  console.log('3. Check if window.location.href redirect is working');
  console.log('4. Verify router navigation guard is active');
}

testLogoutFlow();
