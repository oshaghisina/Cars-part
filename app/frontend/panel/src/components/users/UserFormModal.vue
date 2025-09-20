<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    @click.self="$emit('close')"
  >
    <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex items-center justify-between pb-4 border-b">
          <h3 class="text-lg font-medium text-gray-900">
            {{ isEdit ? 'Edit User' : 'Create New User' }}
          </h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="mt-6 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- First Name -->
            <div>
              <label for="first_name" class="block text-sm font-medium text-gray-700">
                First Name *
              </label>
              <input
                id="first_name"
                v-model="formData.first_name"
                type="text"
                required
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <!-- Last Name -->
            <div>
              <label for="last_name" class="block text-sm font-medium text-gray-700">
                Last Name *
              </label>
              <input
                id="last_name"
                v-model="formData.last_name"
                type="text"
                required
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <!-- Username -->
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700">
                Username *
              </label>
              <input
                id="username"
                v-model="formData.username"
                type="text"
                required
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700">
                Email *
              </label>
              <input
                id="email"
                v-model="formData.email"
                type="email"
                required
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <!-- Phone -->
            <div>
              <label for="phone" class="block text-sm font-medium text-gray-700">
                Phone
              </label>
              <input
                id="phone"
                v-model="formData.phone"
                type="tel"
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <!-- Role -->
            <div>
              <label for="role" class="block text-sm font-medium text-gray-700">
                Role *
              </label>
              <select
                id="role"
                v-model="formData.role"
                required
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="user">User</option>
                <option value="manager">Manager</option>
                <option value="admin">Admin</option>
                <option value="super_admin">Super Admin</option>
              </select>
            </div>

            <!-- Password (only for new users) -->
            <div v-if="!isEdit">
              <label for="password" class="block text-sm font-medium text-gray-700">
                Password *
              </label>
              <input
                id="password"
                v-model="formData.password"
                type="password"
                required
                minlength="8"
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <!-- Timezone -->
            <div>
              <label for="timezone" class="block text-sm font-medium text-gray-700">
                Timezone
              </label>
              <select
                id="timezone"
                v-model="formData.timezone"
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="UTC">UTC</option>
                <option value="Asia/Tehran">Asia/Tehran</option>
                <option value="America/New_York">America/New_York</option>
                <option value="Europe/London">Europe/London</option>
                <option value="Asia/Tokyo">Asia/Tokyo</option>
              </select>
            </div>

            <!-- Language -->
            <div>
              <label for="language" class="block text-sm font-medium text-gray-700">
                Language
              </label>
              <select
                id="language"
                v-model="formData.language"
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="en">English</option>
                <option value="fa">Persian</option>
                <option value="ar">Arabic</option>
              </select>
            </div>
          </div>

          <!-- Status Checkboxes -->
          <div class="flex items-center space-x-6">
            <div class="flex items-center">
              <input
                id="is_active"
                v-model="formData.is_active"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="is_active" class="ml-2 block text-sm text-gray-900">
                Active
              </label>
            </div>
            <div class="flex items-center">
              <input
                id="is_verified"
                v-model="formData.is_verified"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="is_verified" class="ml-2 block text-sm text-gray-900">
                Verified
              </label>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
            <div class="flex">
              <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              <div class="ml-3">
                <p class="text-sm text-red-800">{{ error }}</p>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <span v-if="loading" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Saving...
              </span>
              <span v-else>
                {{ isEdit ? 'Update User' : 'Create User' }}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import { useUsersStore } from '@/stores/users'

export default {
  name: 'UserFormModal',
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    user: {
      type: Object,
      default: null,
    },
    isEdit: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['close', 'save'],
  setup(props, { emit }) {
    const usersStore = useUsersStore()
    
    const loading = ref(false)
    const error = ref('')
    
    const formData = ref({
      first_name: '',
      last_name: '',
      username: '',
      email: '',
      phone: '',
      role: 'user',
      password: '',
      timezone: 'UTC',
      language: 'en',
      is_active: true,
      is_verified: false,
    })

    const resetForm = () => {
      formData.value = {
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        phone: '',
        role: 'user',
        password: '',
        timezone: 'UTC',
        language: 'en',
        is_active: true,
        is_verified: false,
      }
      error.value = ''
    }

    const populateForm = () => {
      if (props.user) {
        formData.value = {
          first_name: props.user.first_name || '',
          last_name: props.user.last_name || '',
          username: props.user.username || '',
          email: props.user.email || '',
          phone: props.user.phone || '',
          role: props.user.role || 'user',
          password: '', // Don't populate password for security
          timezone: props.user.timezone || 'UTC',
          language: props.user.language || 'en',
          is_active: props.user.is_active !== undefined ? props.user.is_active : true,
          is_verified: props.user.is_verified !== undefined ? props.user.is_verified : false,
        }
      }
    }

    const handleSubmit = async () => {
      loading.value = true
      error.value = ''
      
      try {
        if (props.isEdit) {
          await usersStore.updateUser(props.user.id, formData.value)
        } else {
          await usersStore.createUser(formData.value)
        }
        
        emit('save')
      } catch (err) {
        error.value = err.response?.data?.detail || err.message || 'An error occurred'
      } finally {
        loading.value = false
      }
    }

    watch(() => props.show, (newValue) => {
      if (newValue) {
        if (props.user) {
          populateForm()
        } else {
          resetForm()
        }
      }
    })

    watch(() => props.user, () => {
      if (props.show && props.user) {
        populateForm()
      }
    })

    onMounted(() => {
      if (props.show) {
        if (props.user) {
          populateForm()
        } else {
          resetForm()
        }
      }
    })

    return {
      loading,
      error,
      formData,
      handleSubmit,
    }
  },
}
</script>
