<template>
  <div class="contact">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">Contact Us</h1>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Contact Form -->
        <div class="bg-white rounded-lg shadow-md p-8">
          <h2 class="text-xl font-semibold text-gray-900 mb-6">Send us a Message</h2>
          
          <form @submit.prevent="submitContact" class="space-y-4">
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
              <label class="block text-sm font-medium text-gray-700 mb-2">Subject *</label>
              <select
                v-model="form.subject"
                required
                class="input-field"
              >
                <option value="">Select a subject</option>
                <option value="general">General Inquiry</option>
                <option value="quote">Quote Request</option>
                <option value="support">Technical Support</option>
                <option value="order">Order Support</option>
                <option value="other">Other</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Message *</label>
              <textarea
                v-model="form.message"
                rows="5"
                required
                placeholder="Please describe your inquiry..."
                class="input-field"
              ></textarea>
            </div>
            
            <button
              type="submit"
              :disabled="loading"
              class="btn-primary w-full disabled:opacity-50"
            >
              {{ loading ? 'Sending...' : 'Send Message' }}
            </button>
          </form>
        </div>
        
        <!-- Contact Information -->
        <div class="space-y-6">
          <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Get in Touch</h3>
            <div class="space-y-3">
              <div class="flex items-center">
                <span class="text-2xl mr-3">📧</span>
                <div>
                  <p class="font-semibold">Email</p>
                  <p class="text-gray-600">info@chinaautoparts.com</p>
                </div>
              </div>
              
              <div class="flex items-center">
                <span class="text-2xl mr-3">📞</span>
                <div>
                  <p class="font-semibold">Phone</p>
                  <p class="text-gray-600">+86 123 456 7890</p>
                </div>
              </div>
              
              <div class="flex items-center">
                <span class="text-2xl mr-3">📍</span>
                <div>
                  <p class="font-semibold">Address</p>
                  <p class="text-gray-600">Shanghai, China</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Business Hours</h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span>Monday - Friday</span>
                <span class="text-gray-600">9:00 AM - 6:00 PM (CST)</span>
              </div>
              <div class="flex justify-between">
                <span>Saturday</span>
                <span class="text-gray-600">9:00 AM - 2:00 PM (CST)</span>
              </div>
              <div class="flex justify-between">
                <span>Sunday</span>
                <span class="text-gray-600">Closed</span>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Links</h3>
            <div class="space-y-2">
              <router-link to="/search" class="block text-blue-600 hover:text-blue-800">
                Search Parts
              </router-link>
              <router-link to="/quote" class="block text-blue-600 hover:text-blue-800">
                Request Quote
              </router-link>
              <router-link to="/track" class="block text-blue-600 hover:text-blue-800">
                Track Order
              </router-link>
              <a href="/panel/" class="block text-blue-600 hover:text-blue-800">
                Admin Panel
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Contact',
  data() {
    return {
      form: {
        name: '',
        email: '',
        subject: '',
        message: ''
      },
      loading: false
    }
  },
  methods: {
    async submitContact() {
      this.loading = true
      
      try {
        // Simulate API call - replace with actual API integration
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        // Show success message
        alert('Message sent successfully! We will get back to you soon.')
        
        // Reset form
        this.form = {
          name: '',
          email: '',
          subject: '',
          message: ''
        }
      } catch (error) {
        console.error('Contact submission error:', error)
        alert('Failed to send message. Please try again.')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
