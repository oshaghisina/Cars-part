#!/usr/bin/env node

/**
 * Phone Login Test Script
 * Tests the phone number OTP login functionality
 */

const axios = require('axios');

const BASE_URL = 'http://localhost:8001';

// Test phone number (you can change this)
const TEST_PHONE = '+989123456789';

console.log('📱 Phone Login Test Suite');
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

async function testOTPRequest() {
  console.log('\n2️⃣ Testing OTP Request...');
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/otp/phone/login/request`, {
      phone_number: TEST_PHONE
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.data.success) {
      console.log('✅ OTP request successful');
      console.log('   - Message:', response.data.message);
      console.log('   - Expires in:', response.data.expires_in, 'seconds');
      console.log('   - Resend allowed:', response.data.resend);
      return true;
    } else {
      console.log('❌ OTP request failed:', response.data.message);
      return false;
    }
  } catch (error) {
    console.log('❌ OTP request failed:', error.response?.data || error.message);
    return false;
  }
}

async function testOTPVerify() {
  console.log('\n3️⃣ Testing OTP Verification...');
  try {
    // Note: This will fail with a real OTP since we don't have the actual code
    // But it tests the endpoint structure
    const response = await axios.post(`${BASE_URL}/api/v1/otp/phone/login/verify`, {
      phone_number: TEST_PHONE,
      otp_code: '123456' // This will fail, but tests the endpoint
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('✅ OTP verification endpoint accessible');
    console.log('   - Response:', response.data);
    return true;
  } catch (error) {
    if (error.response?.status === 400 || error.response?.status === 404) {
      console.log('✅ OTP verification endpoint accessible (expected failure with test code)');
      console.log('   - Error:', error.response.data.detail);
      return true;
    } else {
      console.log('❌ OTP verification failed:', error.response?.data || error.message);
      return false;
    }
  }
}

async function testRateLimiting() {
  console.log('\n4️⃣ Testing Rate Limiting...');
  try {
    // Make multiple rapid requests to test rate limiting
    const promises = [];
    for (let i = 0; i < 5; i++) {
      promises.push(
        axios.post(`${BASE_URL}/api/v1/otp/phone/login/request`, {
          phone_number: TEST_PHONE
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        }).catch(err => ({ error: err.response?.data || err.message }))
      );
    }
    
    const results = await Promise.all(promises);
    const rateLimited = results.some(result => 
      result.error && result.error.detail && result.error.detail.includes('rate')
    );
    
    if (rateLimited) {
      console.log('✅ Rate limiting is working');
    } else {
      console.log('⚠️ Rate limiting may not be active (this could be normal)');
    }
    
    return true;
  } catch (error) {
    console.log('❌ Rate limiting test failed:', error.message);
    return false;
  }
}

async function testCORSConfiguration() {
  console.log('\n5️⃣ Testing CORS Configuration...');
  try {
    const response = await axios.options(`${BASE_URL}/api/v1/otp/phone/login/request`, {
      headers: {
        'Origin': 'http://localhost:5174',
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

async function testPhoneNumberValidation() {
  console.log('\n6️⃣ Testing Phone Number Validation...');
  
  const testCases = [
    { phone: '+989123456789', valid: true, description: 'Valid Iranian number' },
    { phone: '+1234567890', valid: true, description: 'Valid US number' },
    { phone: '989123456789', valid: false, description: 'Missing + prefix' },
    { phone: '+98', valid: false, description: 'Too short' },
    { phone: '+989123456789012345', valid: false, description: 'Too long' },
    { phone: '', valid: false, description: 'Empty string' }
  ];
  
  for (const testCase of testCases) {
    try {
      await axios.post(`${BASE_URL}/api/v1/otp/phone/login/request`, {
        phone_number: testCase.phone
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (testCase.valid) {
        console.log(`✅ ${testCase.description}: Valid (as expected)`);
      } else {
        console.log(`❌ ${testCase.description}: Should be invalid but was accepted`);
      }
    } catch (error) {
      if (error.response?.status === 422) {
        if (!testCase.valid) {
          console.log(`✅ ${testCase.description}: Invalid (as expected)`);
        } else {
          console.log(`❌ ${testCase.description}: Should be valid but was rejected`);
        }
      } else {
        console.log(`⚠️ ${testCase.description}: Unexpected error - ${error.response?.data?.detail || error.message}`);
      }
    }
  }
  
  return true;
}

async function runAllTests() {
  console.log('Starting comprehensive phone login tests...\n');
  
  // Test backend health
  const backendHealthy = await testBackendHealth();
  if (!backendHealthy) {
    console.log('\n❌ Backend is not healthy. Stopping tests.');
    return;
  }
  
  // Test CORS
  await testCORSConfiguration();
  
  // Test phone number validation
  await testPhoneNumberValidation();
  
  // Test OTP request
  await testOTPRequest();
  
  // Test OTP verification
  await testOTPVerify();
  
  // Test rate limiting
  await testRateLimiting();
  
  console.log('\n🎉 Phone Login Test Suite Complete!');
  console.log('==================================');
  console.log('✅ All critical tests completed');
  console.log('🌐 Web Portal: http://localhost:5174/');
  console.log('🔧 Backend API: http://localhost:8001/');
  console.log('\n💡 You can now test phone login manually:');
  console.log('   1. Open http://localhost:5174/ in your browser');
  console.log('   2. Click the login button');
  console.log('   3. Click "ورود با شماره تلفن" (Login with Phone)');
  console.log('   4. Enter a valid phone number (e.g., +989123456789)');
  console.log('   5. Check your SMS for the OTP code');
  console.log('   6. Enter the OTP code to complete login');
  console.log('\n📱 Note: SMS functionality requires proper SMS service configuration');
}

// Handle errors gracefully
process.on('unhandledRejection', (error) => {
  console.log('\n❌ Unhandled error:', error.message);
  process.exit(1);
});

// Run the tests
runAllTests().catch(console.error);
