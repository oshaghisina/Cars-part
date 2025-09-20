<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            {{ isEditing ? 'Edit Lead' : 'Add New Lead' }}
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
        <form @submit.prevent="saveLead">
          <div class="space-y-4">
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
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Enter first name"
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
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Enter last name"
              />
            </div>

            <!-- Phone Number -->
            <div>
              <label for="phone_e164" class="block text-sm font-medium text-gray-700">
                Phone Number *
              </label>
              <input
                id="phone_e164"
                v-model="formData.phone_e164"
                type="tel"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="+989123456789"
              />
            </div>

            <!-- Telegram User ID -->
            <div>
              <label for="telegram_user_id" class="block text-sm font-medium text-gray-700">
                Telegram User ID
              </label>
              <input
                id="telegram_user_id"
                v-model="formData.telegram_user_id"
                type="text"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Enter Telegram user ID"
              />
            </div>

            <!-- City -->
            <div>
              <label for="city" class="block text-sm font-medium text-gray-700">
                City
              </label>
              <input
                id="city"
                v-model="formData.city"
                type="text"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Enter city"
              />
            </div>

            <!-- Notes -->
            <div>
              <label for="notes" class="block text-sm font-medium text-gray-700">
                Notes
              </label>
              <textarea
                id="notes"
                v-model="formData.notes"
                rows="3"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Add any notes about this lead..."
              ></textarea>
            </div>

            <!-- Consent -->
            <div class="flex items-center">
              <input
                id="consent"
                v-model="formData.consent"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="consent" class="ml-2 block text-sm text-gray-900">
                Customer has given consent for data processing
              </label>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="mt-4 rounded-md bg-red-50 p-3">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">Error</h3>
                <div class="mt-1 text-sm text-red-700">{{ error }}</div>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              @click="$emit('close')"
              class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? (isEditing ? 'Updating...' : 'Creating...') : (isEditing ? 'Update Lead' : 'Create Lead') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useLeadsStore } from '../../stores/leads'

export default {
  name: 'LeadFormModal',
  props: {
    lead: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const leadsStore = useLeadsStore()
    
    const loading = ref(false)
    const error = ref(null)
    
    const formData = ref({
      first_name: '',
      last_name: '',
      phone_e164: '',
      telegram_user_id: '',
      city: '',
      notes: '',
      consent: true
    })

    const isEditing = computed(() => !!props.lead)

    // Watch for lead changes to populate form
    watch(() => props.lead, (newLead) => {
      if (newLead) {
        formData.value = {
          first_name: newLead.first_name || '',
          last_name: newLead.last_name || '',
          phone_e164: newLead.phone_e164 || '',
          telegram_user_id: newLead.telegram_user_id || '',
          city: newLead.city || '',
          notes: newLead.notes || '',
          consent: newLead.consent !== undefined ? newLead.consent : true
        }
      } else {
        // Reset form for new lead
        formData.value = {
          first_name: '',
          last_name: '',
          phone_e164: '',
          telegram_user_id: '',
          city: '',
          notes: '',
          consent: true
        }
      }
    }, { immediate: true })

    const saveLead = async () => {
      loading.value = true
      error.value = null
      
      try {
        if (isEditing.value) {
          await leadsStore.updateLead(props.lead.id, formData.value)
        } else {
          await leadsStore.createLead(formData.value)
        }
        
        emit('saved')
      } catch (err) {
        error.value = err.message || (isEditing.value ? 'Failed to update lead' : 'Failed to create lead')
      } finally {
        loading.value = false
      }
    }

    return {
      leadsStore,
      loading,
      error,
      formData,
      isEditing,
      saveLead
    }
  }
}
</script>
