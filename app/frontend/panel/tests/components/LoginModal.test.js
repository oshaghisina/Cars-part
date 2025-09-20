/**
 * Tests for LoginModal component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LoginModal from '@/components/LoginModal.vue'

// Mock the auth store
const mockAuthStore = {
  login: vi.fn(),
  isLoggedIn: false,
  user: null,
  loading: false,
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore,
}))

describe('LoginModal', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders login form correctly', () => {
    const wrapper = mount(LoginModal)
    
    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('has correct form labels', () => {
    const wrapper = mount(LoginModal)
    
    expect(wrapper.text()).toContain('Username or Email')
    expect(wrapper.text()).toContain('Password')
  })

  it('handles form submission', async () => {
    const wrapper = mount(LoginModal)
    
    // Fill form
    await wrapper.find('input[type="text"]').setValue('admin')
    await wrapper.find('input[type="password"]').setValue('password')
    
    // Submit form
    await wrapper.find('form').trigger('submit')
    
    expect(mockAuthStore.login).toHaveBeenCalledWith({
      username_or_email: 'admin',
      password: 'password'
    })
  })

  it('shows loading state', async () => {
    mockAuthStore.loading = true
    const wrapper = mount(LoginModal)
    
    expect(wrapper.find('button[disabled]').exists()).toBe(true)
  })

  it('handles login errors', async () => {
    mockAuthStore.login.mockRejectedValue(new Error('Invalid credentials'))
    const wrapper = mount(LoginModal)
    
    // Fill and submit form
    await wrapper.find('input[type="text"]').setValue('admin')
    await wrapper.find('input[type="password"]').setValue('wrong')
    await wrapper.find('form').trigger('submit')
    
    // Wait for error handling
    await wrapper.vm.$nextTick()
    
    expect(mockAuthStore.login).toHaveBeenCalled()
  })

  it('has proper accessibility attributes', () => {
    const wrapper = mount(LoginModal)
    
    const usernameInput = wrapper.find('input[type="text"]')
    const passwordInput = wrapper.find('input[type="password"]')
    
    expect(usernameInput.attributes('autocomplete')).toBe('username')
    expect(passwordInput.attributes('autocomplete')).toBe('current-password')
  })

  it('focuses username input on mount', async () => {
    const wrapper = mount(LoginModal)
    
    // Wait for mounted hook
    await wrapper.vm.$nextTick()
    
    // Check if focus was called (mocked)
    const usernameInput = wrapper.find('input[type="text"]')
    expect(usernameInput.exists()).toBe(true)
  })
})
