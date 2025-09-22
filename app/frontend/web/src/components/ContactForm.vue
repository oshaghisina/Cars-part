<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900 font-persian font-persian-bold text-rtl">Get a Quote</h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 font-persian"
          >
            <span class="text-2xl font-persian">&times;</span>
          </button>
        </div>
        
        <form @submit.prevent="submitQuote" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1 font-persian">نام</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1 font-persian">ایمیل</label>
            <input
              v-model="form.email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1 font-persian">تلفن</label>
            <input
              v-model="form.phone"
              type="tel"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1 font-persian">Part Description</label>
            <textarea
              v-model="form.description"
              rows="3"
              required
              placeholder="Describe the parts you need..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1 font-persian">Vehicle Details</label>
            <input
              v-model="form.vehicle"
              type="text"
              placeholder="Make, مدل, Year"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 text-gray-600 hover:text-gray-800 font-persian"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="bg-blue-600 text-white px-6 py-2 rounded-md font-semibold hover:bg-blue-700 disabled:opacity-50 font-persian"
            >
              {{ loading ? 'Sending...' : 'Send Quote Request' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContactForm',
  data() {
    return {
      form: {
        name: '',
        email: '',
        phone: '',
        description: '',
        vehicle: ''
      },
      loading: false
    }
  },
  methods: {
    async submitQuote() {
      this.loading = true
      
      try {
        // Simulate API call - replace with actual API integration
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        // Show success message
        alert('Quote request sent successfully! We will contact you soon.')
        
        // Reset form and close modal
        this.form = {
          name: '',
          email: '',
          phone: '',
          description: '',
          vehicle: ''
        }
        this.$emit('close')
      } catch (error) {
        console.error('Quote submission error:', error)
        alert('Failed to send quote request. Please try again.')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
