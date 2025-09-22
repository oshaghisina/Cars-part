<template>
  <div class="quote">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">Request a Quote</h1>
      
      <div class="bg-white rounded-lg shadow-md p-8">
        <form @submit.prevent="submitQuote" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Name *</label>
              <input
                v-model="form.name"
                type="text"
                required
                class="input-field"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Email *</label>
              <input
                v-model="form.email"
                type="email"
                required
                class="input-field"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Phone</label>
              <input
                v-model="form.phone"
                type="tel"
                class="input-field"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Company</label>
              <input
                v-model="form.company"
                type="text"
                class="input-field"
              />
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Vehicle Details *</label>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input
                v-model="form.make"
                type="text"
                placeholder="Make (e.g., BYD)"
                required
                class="input-field"
              />
              <input
                v-model="form.model"
                type="text"
                placeholder="Model (e.g., F3)"
                required
                class="input-field"
              />
              <input
                v-model="form.year"
                type="text"
                placeholder="Year (e.g., 2020)"
                required
                class="input-field"
              />
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Parts Needed *</label>
            <textarea
              v-model="form.parts"
              rows="4"
              required
              placeholder="Please describe the parts you need in detail..."
              class="input-field"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Additional Requirements</label>
            <textarea
              v-model="form.requirements"
              rows="3"
              placeholder="Any specific requirements, quantities, or special instructions..."
              class="input-field"
            ></textarea>
          </div>
          
          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="loading"
              class="btn-primary px-8 py-3 disabled:opacity-50"
            >
              {{ loading ? 'Sending Quote Request...' : 'Send Quote Request' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Quote',
  data() {
    return {
      form: {
        name: '',
        email: '',
        phone: '',
        company: '',
        make: '',
        model: '',
        year: '',
        parts: '',
        requirements: ''
      },
      loading: false
    }
  },
  methods: {
    async submitQuote() {
      this.loading = true
      
      try {
        // Simulate API call - replace with actual API integration
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Show success message
        alert('Quote request sent successfully! We will contact you within 24 hours.')
        
        // Reset form
        this.form = {
          name: '',
          email: '',
          phone: '',
          company: '',
          make: '',
          model: '',
          year: '',
          parts: '',
          requirements: ''
        }
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
