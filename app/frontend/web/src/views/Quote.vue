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
          
          <!-- Success Message -->
          <div v-if="success" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            <div class="flex items-center">
              <span class="text-2xl mr-2">✅</span>
              <div>
                <strong>Success!</strong> Your quote request has been submitted successfully. 
                We will contact you within 24 hours.
              </div>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <div class="flex items-center">
              <span class="text-2xl mr-2">❌</span>
              <div>
                <strong>Error:</strong> {{ error }}
              </div>
            </div>
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
import apiService from '../services/api.js'

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
      loading: false,
      error: null,
      success: false
    }
  },
  methods: {
    async submitQuote() {
      this.loading = true
      this.error = null
      this.success = false
      
      try {
        // Validate required fields
        if (!this.form.name || !this.form.phone || !this.form.parts) {
          throw new Error('Please fill in all required fields (Name, Phone, Parts)')
        }
        
        // Prepare lead data
        const leadData = {
          name: this.form.name,
          phone: this.form.phone,
          lastName: this.form.company || '',
          city: '', // Could be added to form if needed
          description: this.buildDescription()
        }
        
        // Create lead via API
        const lead = await apiService.createLead(leadData)
        
        this.success = true
        
        // Reset form after successful submission
        setTimeout(() => {
          this.resetForm()
        }, 3000)
        
      } catch (error) {
        console.error('Quote submission error:', error)
        this.error = error.message || 'Failed to send quote request. Please try again.'
      } finally {
        this.loading = false
      }
    },
    
    buildDescription() {
      let description = `Quote Request:\n\n`
      description += `Parts Needed: ${this.form.parts}\n\n`
      
      if (this.form.make || this.form.model || this.form.year) {
        description += `Vehicle Details:\n`
        if (this.form.make) description += `Make: ${this.form.make}\n`
        if (this.form.model) description += `Model: ${this.form.model}\n`
        if (this.form.year) description += `Year: ${this.form.year}\n`
        description += `\n`
      }
      
      if (this.form.requirements) {
        description += `Additional Requirements: ${this.form.requirements}\n\n`
      }
      
      if (this.form.email) {
        description += `Contact Email: ${this.form.email}\n`
      }
      
      if (this.form.company) {
        description += `Company: ${this.form.company}\n`
      }
      
      return description
    },
    
    resetForm() {
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
      this.success = false
      this.error = null
    }
  }
}
</script>
