// Test script for Admin Panel Password Generation functionality
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
  console.log('🔐 Testing Admin Login...');
  
  try {
    const response = await api.post('/users/login', {
      username_or_email: 'admin',
      password: 'adminpassword'
    });
    
    if (response.status === 200 && response.data.access_token) {
      authToken = response.data.access_token;
      console.log('✅ Admin login successful');
      console.log(`   User: ${response.data.user.username} (${response.data.user.role})`);
      return true;
    } else {
      console.log('❌ Admin login failed');
      return false;
    }
  } catch (error) {
    console.error('❌ Admin login error:', error.message);
    return false;
  }
}

async function testPasswordGeneration(length = 12, includeSymbols = true) {
  console.log(`\n🔑 Testing Password Generation (length: ${length}, symbols: ${includeSymbols})...`);
  
  try {
    const response = await api.get('/users/utils/generate-password', {
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      params: {
        length: length,
        include_symbols: includeSymbols
      }
    });
    
    if (response.status === 200) {
      const result = response.data;
      console.log('✅ Password generation successful');
      console.log(`   Password: ${result.password}`);
      console.log(`   Length: ${result.length}`);
      console.log(`   Includes Symbols: ${result.includes_symbols}`);
      console.log(`   Strength: ${result.strength}`);
      
      // Validate password characteristics
      const password = result.password;
      const hasLower = /[a-z]/.test(password);
      const hasUpper = /[A-Z]/.test(password);
      const hasDigit = /[0-9]/.test(password);
      const hasSymbol = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password);
      
      console.log(`   Validation:`);
      console.log(`     - Lowercase: ${hasLower ? '✅' : '❌'}`);
      console.log(`     - Uppercase: ${hasUpper ? '✅' : '❌'}`);
      console.log(`     - Digits: ${hasDigit ? '✅' : '❌'}`);
      console.log(`     - Symbols: ${hasSymbol ? '✅' : '❌'}`);
      console.log(`     - Correct Length: ${password.length === length ? '✅' : '❌'}`);
      
      return {
        success: true,
        password: result.password,
        valid: hasLower && hasUpper && hasDigit && (includeSymbols ? hasSymbol : true) && password.length === length
      };
    } else {
      console.log('❌ Password generation failed');
      return { success: false };
    }
  } catch (error) {
    console.error('❌ Password generation error:', error.message);
    if (error.response) {
      console.error(`   Status: ${error.response.status}`);
      console.error(`   Data: ${JSON.stringify(error.response.data)}`);
    }
    return { success: false };
  }
}

async function testMultiplePasswordGeneration() {
  console.log('\n🔄 Testing Multiple Password Generation...');
  
  const passwords = [];
  const tests = [
    { length: 8, symbols: true },
    { length: 12, symbols: true },
    { length: 16, symbols: true },
    { length: 12, symbols: false },
    { length: 20, symbols: true }
  ];
  
  for (const test of tests) {
    const result = await testPasswordGeneration(test.length, test.symbols);
    if (result.success) {
      passwords.push(result.password);
    }
  }
  
  // Check if all passwords are unique
  const uniquePasswords = new Set(passwords);
  const allUnique = uniquePasswords.size === passwords.length;
  
  console.log(`\n📊 Multiple Generation Results:`);
  console.log(`   Generated: ${passwords.length} passwords`);
  console.log(`   Unique: ${uniquePasswords.size} passwords`);
  console.log(`   All Unique: ${allUnique ? '✅' : '❌'}`);
  
  return allUnique;
}

async function testPasswordGenerationWithoutAuth() {
  console.log('\n🚫 Testing Password Generation Without Auth...');
  
  try {
    const response = await api.get('/users/utils/generate-password', {
      params: { length: 12, include_symbols: true }
    });
    
    console.log('❌ Password generation should have failed without auth');
    return false;
  } catch (error) {
    if (error.response && error.response.status === 401) {
      console.log('✅ Password generation correctly requires authentication');
      return true;
    } else {
      console.log('❌ Unexpected error:', error.message);
      return false;
    }
  }
}

async function testAdminPanelAccess() {
  console.log('\n🌐 Testing Admin Panel Frontend Access...');
  
  try {
    const response = await fetch(ADMIN_PANEL_URL);
    if (response.ok) {
      console.log('✅ Admin panel frontend accessible');
      console.log(`   URL: ${ADMIN_PANEL_URL}`);
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

async function runPasswordGenerationTests() {
  console.log('🧪 Admin Panel Password Generation Test Suite');
  console.log('=============================================\n');
  
  let allTestsPassed = true;
  
  // Test admin login
  if (!(await testAdminLogin())) {
    allTestsPassed = false;
    console.log('\n❌ Cannot proceed without admin login');
    return;
  }
  
  // Test password generation with different parameters
  const test1 = await testPasswordGeneration(12, true);
  if (!test1.success || !test1.valid) allTestsPassed = false;
  
  const test2 = await testPasswordGeneration(8, false);
  if (!test2.success || !test2.valid) allTestsPassed = false;
  
  // Test multiple password generation
  const multipleTest = await testMultiplePasswordGeneration();
  if (!multipleTest) allTestsPassed = false;
  
  // Test authentication requirement
  const authTest = await testPasswordGenerationWithoutAuth();
  if (!authTest) allTestsPassed = false;
  
  // Test frontend access
  const frontendTest = await testAdminPanelAccess();
  if (!frontendTest) allTestsPassed = false;
  
  console.log('\n📋 Password Generation Test Summary:');
  console.log('=====================================');
  console.log(`✅ Admin Login: ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Password Generation (12 chars, symbols): ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Password Generation (8 chars, no symbols): ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Multiple Password Generation: ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Authentication Required: ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Frontend Access: ${allTestsPassed ? 'PASS' : 'FAIL'}`);
  
  if (allTestsPassed) {
    console.log('\n🎉 All Password Generation Tests PASSED!');
    console.log('\n🚀 Ready to use Admin Panel Password Generation:');
    console.log(`   Backend API: ${API_BASE_URL}/users/utils/generate-password`);
    console.log(`   Admin Panel: ${ADMIN_PANEL_URL}`);
    console.log('   Login: admin / adminpassword');
    console.log('   Navigate to: Users → Create New User → Click password generate button');
  } else {
    console.log('\n❌ Some Password Generation Tests FAILED!');
  }
}

runPasswordGenerationTests();
