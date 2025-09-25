// Test script for Admin Panel functionality
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

let authToken = '';

async function testAdminLogin() {
  console.log('🔐 Testing Admin Panel Login...');
  
  try {
    const response = await api.post('/users/login', {
      username_or_email: 'admin',
      password: 'adminpassword'
    });
    
    if (response.status === 200 && response.data.access_token) {
      authToken = response.data.access_token;
      console.log('✅ Admin login successful');
      console.log(`   User: ${response.data.user.username} (${response.data.user.role})`);
      console.log(`   Token: ${authToken.substring(0, 20)}...`);
      console.log(`   Expires in: ${response.data.expires_in} seconds`);
      return true;
    } else {
      console.log('❌ Admin login failed');
      return false;
    }
  } catch (error) {
    console.error('❌ Admin login error:', error.message);
    if (error.response) {
      console.error(`   Status: ${error.response.status}`);
      console.error(`   Data: ${JSON.stringify(error.response.data)}`);
    }
    return false;
  }
}

async function testAuthConfig() {
  console.log('\n⚙️ Testing Auth Configuration Endpoint...');
  
  try {
    const response = await api.get('/auth/config', {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    if (response.status === 200) {
      console.log('✅ Auth config endpoint working');
      const config = response.data;
      console.log(`   JWT Library: ${config.jwt.library}`);
      console.log(`   JWT Algorithm: ${config.jwt.algorithm}`);
      console.log(`   Token Expiry: ${config.jwt.access_token_expire_minutes} minutes`);
      console.log(`   Telegram SSO: ${config.features.telegram_sso ? 'Enabled' : 'Disabled'}`);
      console.log(`   OTP Enabled: ${config.features.otp_enabled ? 'Enabled' : 'Disabled'}`);
      return true;
    } else {
      console.log('❌ Auth config endpoint failed');
      return false;
    }
  } catch (error) {
    console.error('❌ Auth config error:', error.message);
    return false;
  }
}

async function testAuthStats() {
  console.log('\n📊 Testing Auth Statistics Endpoint...');
  
  try {
    const response = await api.get('/auth/stats', {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    if (response.status === 200) {
      console.log('✅ Auth stats endpoint working');
      const stats = response.data;
      console.log(`   Successful Logins: ${stats.authentication.successful_logins}`);
      console.log(`   Failed Logins: ${stats.authentication.failed_logins}`);
      console.log(`   OTP Requests: ${stats.otp.total_requests}`);
      console.log(`   Telegram Links: ${stats.telegram.total_links}`);
      return true;
    } else {
      console.log('❌ Auth stats endpoint failed');
      return false;
    }
  } catch (error) {
    console.error('❌ Auth stats error:', error.message);
    return false;
  }
}

async function testAuthHealth() {
  console.log('\n🏥 Testing Auth Health Endpoint...');
  
  try {
    const response = await api.get('/auth/health');
    
    if (response.status === 200) {
      console.log('✅ Auth health endpoint working');
      const health = response.data;
      console.log(`   Status: ${health.status}`);
      console.log(`   JWT Service: ${health.jwt_service}`);
      console.log(`   Telegram SSO: ${health.features.telegram_sso ? 'Enabled' : 'Disabled'}`);
      console.log(`   OTP: ${health.features.otp ? 'Enabled' : 'Disabled'}`);
      return true;
    } else {
      console.log('❌ Auth health endpoint failed');
      return false;
    }
  } catch (error) {
    console.error('❌ Auth health error:', error.message);
    return false;
  }
}

async function testAuthLogs() {
  console.log('\n📝 Testing Auth Logs Endpoint...');
  
  try {
    const response = await api.get('/auth/logs', {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    if (response.status === 200) {
      console.log('✅ Auth logs endpoint working');
      const logs = response.data;
      console.log(`   Total Logs: ${logs.total}`);
      console.log(`   Sample Logs: ${logs.logs.length}`);
      return true;
    } else {
      console.log('❌ Auth logs endpoint failed');
      return false;
    }
  } catch (error) {
    console.error('❌ Auth logs error:', error.message);
    return false;
  }
}

async function testAdminPanelAccess() {
  console.log('\n🌐 Testing Admin Panel Frontend Access...');
  
  try {
    const response = await fetch(ADMIN_PANEL_URL);
    if (response.ok) {
      console.log('✅ Admin panel frontend accessible');
      console.log(`   URL: ${ADMIN_PANEL_URL}`);
      console.log(`   Status: ${response.status} ${response.statusText}`);
      return true;
    } else {
      console.log('❌ Admin panel frontend not accessible');
      return false;
    }
  } catch (error) {
    console.error('❌ Admin panel access error:', error.message);
    return false;
  }
}

async function runAdminPanelTests() {
  console.log('🧪 Admin Panel Functionality Test Suite');
  console.log('=====================================\n');
  
  let allTestsPassed = true;
  
  // Test admin login
  if (!(await testAdminLogin())) {
    allTestsPassed = false;
    console.log('\n❌ Cannot proceed without admin login');
    return;
  }
  
  // Test auth endpoints
  if (!(await testAuthConfig())) allTestsPassed = false;
  if (!(await testAuthStats())) allTestsPassed = false;
  if (!(await testAuthHealth())) allTestsPassed = false;
  if (!(await testAuthLogs())) allTestsPassed = false;
  
  // Test frontend access
  if (!(await testAdminPanelAccess())) allTestsPassed = false;
  
  console.log('\n📋 Admin Panel Test Summary:');
  console.log('============================');
  console.log(`✅ Admin Login: ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Auth Config: ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Auth Stats: ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Auth Health: ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Auth Logs: ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Frontend Access: ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  
  if (allTestsPassed) {
    console.log('\n🎉 All Admin Panel Tests PASSED!');
    console.log('\n🚀 Ready to use Admin Panel:');
    console.log(`   URL: ${ADMIN_PANEL_URL}`);
    console.log('   Login: admin / adminpassword');
    console.log('   Auth Dashboard: /auth-dashboard');
  } else {
    console.log('\n❌ Some Admin Panel Tests FAILED!');
  }
}

runAdminPanelTests();
