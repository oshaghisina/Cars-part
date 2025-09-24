<template>
  <div class="flex items-center gap-2">
    <div :class="iconClasses" class="flex-shrink-0">
      <svg v-if="status === 'compatible'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
      <svg v-else-if="status === 'incompatible'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
      </svg>
      <svg v-else-if="status === 'requires_verification'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
      </svg>
    </div>
    <span :class="textClasses" class="text-sm font-medium font-persian">
      {{ message }}
    </span>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'CompatibilityStatus',
  props: {
    status: {
      type: String,
      required: true,
      validator: (value) => ['compatible', 'incompatible', 'requires_verification', 'unknown'].includes(value)
    }
  },
  setup(props) {
    const message = computed(() => {
      switch (props.status) {
        case 'compatible': return 'مناسب خودروی شماست'
        case 'incompatible': return 'مناسب خودروی شما نیست'
        case 'requires_verification': return 'نیاز به تأیید سازگاری'
        case 'unknown': return 'سازگاری نامشخص'
        default: return 'نامشخص'
      }
    })

    const iconClasses = computed(() => {
      switch (props.status) {
        case 'compatible': return 'text-green-600'
        case 'incompatible': return 'text-red-600'
        case 'requires_verification': return 'text-yellow-600'
        case 'unknown': return 'text-gray-600'
        default: return 'text-gray-600'
      }
    })

    const textClasses = computed(() => {
      switch (props.status) {
        case 'compatible': return 'text-green-700'
        case 'incompatible': return 'text-red-700'
        case 'requires_verification': return 'text-yellow-700'
        case 'unknown': return 'text-gray-700'
        default: return 'text-gray-700'
      }
    })

    return {
      message,
      iconClasses,
      textClasses
    }
  }
}
</script>
