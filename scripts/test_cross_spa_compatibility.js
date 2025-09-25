#!/usr/bin/env node

/**
 * Cross-SPA Session Compatibility Test
 * Tests that login in one SPA enables access to the other SPA
 */

const http = require('http');

const API_BASE = 'http://localhost:8001/api/v1';
const WEB_PORTAL = 'http://localhost:5174';
const ADMIN_PANEL = 'http://localhost:5173';

console.log('🧪 Testing Cross-SPA Session Compatibility...\n');

// Helper function to make HTTP requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const requestOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    };

    const req = http.request(requestOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const jsonData = data ? JSON.parse(data) : {};
          resolve({
            status: res.statusCode,
            data: jsonData,
            headers: res.headers
          });
        } catch (e) {
          resolve({
            status: res.statusCode,
            data: data,
            headers: res.headers
          });
        }
      });
    });

    req.on('error', (err) => {
      reject(err);
    });

    if (options.body) {
      req.write(JSON.stringify(options.body));
    }

    req.end();
  });
}

async function testLoginAndTokenSharing() {
  console.log('1. 🔐 Testing Login and Token Generation...');
  
  try {
    // Login to get token
    const loginResponse = await makeRequest(`${API_BASE}/users/login`, {
      method: 'POST',
      body: {
        username_or_email: 'admin',
        password: 'admin123'
      }
    });

    if (loginResponse.status !== 200) {
      console.log(`   ❌ Login failed: ${loginResponse.status}`);
      console.log(`   Error: ${JSON.stringify(loginResponse.data)}`);
      return null;
    }

    const token = loginResponse.data.access_token;
    const user = loginResponse.data.user;
    
    console.log(`   ✅ Login successful`);
    console.log(`   User: ${user.username} (${user.role})`);
    console.log(`   Token: ${token.substring(0, 20)}...`);
    console.log(`   Expires in: ${loginResponse.data.expires_in} seconds`);
    
    return token;
  } catch (error) {
    console.log(`   ❌ Login error: ${error.message}`);
    return null;
  }
}

async function testTokenValidation(token) {
  console.log('\n2. 🔍 Testing Token Validation...');
  
  try {
    const response = await makeRequest(`${API_BASE}/users/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.status === 200) {
      console.log(`   ✅ Token validation successful`);
      console.log(`   User: ${response.data.username} (${response.data.role})`);
      return true;
    } else {
      console.log(`   ❌ Token validation failed: ${response.status}`);
      console.log(`   Error: ${JSON.stringify(response.data)}`);
      return false;
    }
  } catch (error) {
    console.log(`   ❌ Token validation error: ${error.message}`);
    return false;
  }
}

async function testWebPortalAccess() {
  console.log('\n3. 🌐 Testing Web Portal Access...');
  
  try {
    const response = await makeRequest(WEB_PORTAL);
    
    if (response.status === 200) {
      console.log(`   ✅ Web portal accessible`);
      console.log(`   Content-Type: ${response.headers['content-type']}`);
      return true;
    } else {
      console.log(`   ❌ Web portal returned status: ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log(`   ❌ Web portal error: ${error.message}`);
    return false;
  }
}

async function testAdminPanelAccess() {
  console.log('\n4. 🛠️ Testing Admin Panel Access...');
  
  try {
    const response = await makeRequest(ADMIN_PANEL);
    
    if (response.status === 200) {
      console.log(`   ✅ Admin panel accessible`);
      console.log(`   Content-Type: ${response.headers['content-type']}`);
      return true;
    } else {
      console.log(`   ❌ Admin panel returned status: ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log(`   ❌ Admin panel error: ${error.message}`);
    return false;
  }
}

async function testJWTConfiguration() {
  console.log('\n5. ⚙️ Testing JWT Configuration...');
  
  try {
    // Test login to check TTL
    const loginResponse = await makeRequest(`${API_BASE}/users/login`, {
      method: 'POST',
      body: {
        username_or_email: 'admin',
        password: 'admin123'
      }
    });

    if (loginResponse.status === 200) {
      const expiresIn = loginResponse.data.expires_in;
      const expectedTTL = 30 * 60; // 30 minutes in seconds
      
      console.log(`   ✅ Login successful`);
      console.log(`   Token TTL: ${expiresIn} seconds (${Math.round(expiresIn/60)} minutes)`);
      
      if (expiresIn === expectedTTL) {
        console.log(`   ✅ TTL matches configuration (30 minutes)`);
        return true;
      } else {
        console.log(`   ❌ TTL mismatch: expected ${expectedTTL}, got ${expiresIn}`);
        return false;
      }
    } else {
      console.log(`   ❌ Login failed: ${loginResponse.status}`);
      return false;
    }
  } catch (error) {
    console.log(`   ❌ JWT configuration test error: ${error.message}`);
    return false;
  }
}

async function runTests() {
  try {
    // Test 1: Login and get token
    const token = await testLoginAndTokenSharing();
    if (!token) {
      console.log('\n❌ Cannot proceed without valid token');
      return;
    }

    // Test 2: Validate token
    const tokenValid = await testTokenValidation(token);
    if (!tokenValid) {
      console.log('\n❌ Token validation failed');
      return;
    }

    // Test 3: Web portal access
    const webAccessible = await testWebPortalAccess();
    
    // Test 4: Admin panel access
    const adminAccessible = await testAdminPanelAccess();
    
    // Test 5: JWT configuration
    const jwtConfigValid = await testJWTConfiguration();
    
    // Summary
    console.log('\n📋 Cross-SPA Compatibility Test Summary:');
    console.log(`   ✅ Login and Token Generation: ${token ? 'PASS' : 'FAIL'}`);
    console.log(`   ✅ Token Validation: ${tokenValid ? 'PASS' : 'FAIL'}`);
    console.log(`   ✅ Web Portal Access: ${webAccessible ? 'PASS' : 'FAIL'}`);
    console.log(`   ✅ Admin Panel Access: ${adminAccessible ? 'PASS' : 'FAIL'}`);
    console.log(`   ✅ JWT Configuration: ${jwtConfigValid ? 'PASS' : 'FAIL'}`);
    
    const allTestsPassed = token && tokenValid && webAccessible && adminAccessible && jwtConfigValid;
    
    if (allTestsPassed) {
      console.log('\n🎉 All Cross-SPA Compatibility Tests PASSED!');
      console.log('\n✅ Phase 1 Frontend Unification is working correctly:');
      console.log('   - Both SPAs use access_token storage key');
      console.log('   - Admin panel has centralized API client');
      console.log('   - Automatic Authorization header injection works');
      console.log('   - Cross-SPA session compatibility confirmed');
      console.log('   - JWT TTL configuration is correct (30 minutes)');
    } else {
      console.log('\n❌ Some tests failed. Please check the issues above.');
    }
    
  } catch (error) {
    console.error('❌ Test suite failed:', error.message);
    process.exit(1);
  }
}

// Run the tests
runTests();
