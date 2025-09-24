<template>
  <div class="flex items-center gap-2">
    <div :class="indicatorClasses" class="w-2 h-2 rounded-full"></div>
    <span :class="textClasses" class="text-sm font-medium font-persian">
      {{ message }}
    </span>
    <span v-if="showQuantity && quantity > 0" class="text-xs text-gray-500 font-persian">
      ({{ quantity }} عدد)
    </span>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'StockIndicator',
  props: {
    stock: {
      type: Number,
      required: true
    },
    showQuantity: {
      type: Boolean,
      default: true
    }
  },
  setup(props) {
    const message = computed(() => {
      if (props.stock === 0) return 'ناموجود'
      if (props.stock <= 5) return 'کم موجود'
      return 'موجود'
    })

    const indicatorClasses = computed(() => {
      if (props.stock === 0) return 'bg-red-500'
      if (props.stock <= 5) return 'bg-orange-500'
      return 'bg-green-500'
    })

    const textClasses = computed(() => {
      if (props.stock === 0) return 'text-red-700'
      if (props.stock <= 5) return 'text-orange-700'
      return 'text-green-700'
    })

    return {
      message,
      indicatorClasses,
      textClasses,
      quantity: props.stock
    }
  }
}
</script>
