<template>
  <div class="bg-white overflow-hidden shadow rounded-lg">
    <div class="p-5">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div :class="[
            'w-8 h-8 rounded-md flex items-center justify-center',
            iconBgColor
          ]">
            <span class="text-white text-sm font-medium">{{ icon }}</span>
          </div>
        </div>
        <div class="ml-5 w-0 flex-1">
          <dl>
            <dt class="text-sm font-medium text-gray-500 truncate">{{ label }}</dt>
            <dd class="flex items-baseline">
              <div class="text-2xl font-semibold text-gray-900">{{ value }}</div>
              <div v-if="change" :class="[
                'ml-2 flex items-baseline text-sm font-semibold',
                change > 0 ? 'text-green-600' : 'text-red-600'
              ]">
                <svg v-if="change > 0" class="self-center flex-shrink-0 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="self-center flex-shrink-0 h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span class="sr-only">{{ change > 0 ? 'Increased' : 'Decreased' }} by</span>
                {{ Math.abs(change) }}%
              </div>
            </dd>
          </dl>
        </div>
      </div>
    </div>
    <div v-if="description" class="bg-gray-50 px-5 py-3">
      <div class="text-sm">
        <span class="text-gray-500">{{ description }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MetricCard',
  props: {
    icon: {
      type: String,
      required: true
    },
    label: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    change: {
      type: Number,
      default: null
    },
    description: {
      type: String,
      default: null
    },
    color: {
      type: String,
      default: 'blue'
    }
  },
  computed: {
    iconBgColor() {
      const colors = {
        blue: 'bg-blue-500',
        green: 'bg-green-500',
        purple: 'bg-purple-500',
        orange: 'bg-orange-500',
        red: 'bg-red-500',
        yellow: 'bg-yellow-500',
        indigo: 'bg-indigo-500',
        pink: 'bg-pink-500'
      }
      return colors[this.color] || colors.blue
    }
  }
}
</script>
