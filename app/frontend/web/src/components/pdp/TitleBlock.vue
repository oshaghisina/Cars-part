<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <div class="flex items-start justify-between mb-4">
      <div class="flex-1">
        <h1 class="text-2xl font-bold text-gray-900 mb-2 font-persian-bold text-rtl">{{ part.name }}</h1>
        <p class="text-gray-600 font-persian text-rtl">{{ part.brand || 'برند OEM' }}</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="badge in badges"
          :key="badge.type"
          :class="badgeClasses[badge.type]"
          class="px-2 py-1 text-xs rounded-full font-persian"
        >
          {{ badge.text }}
        </span>
      </div>
    </div>
    
    <!-- Product Identifiers -->
    <div class="space-y-2 text-sm text-gray-600 font-persian">
      <div class="flex justify-between items-center">
        <span class="font-persian text-rtl"><strong>کد قطعه:</strong></span>
        <span class="font-mono text-gray-900">{{ part.oemCode }}</span>
      </div>
      <div class="flex justify-between items-center">
        <span class="font-persian text-rtl"><strong>دسته‌بندی:</strong></span>
        <span class="font-persian text-rtl">{{ part.category }}</span>
      </div>
      <div v-if="part.sku" class="flex justify-between items-center">
        <span class="font-persian text-rtl"><strong>SKU:</strong></span>
        <span class="font-mono text-gray-900">{{ part.sku }}</span>
      </div>
      <div v-if="part.ean" class="flex justify-between items-center">
        <span class="font-persian text-rtl"><strong>EAN:</strong></span>
        <span class="font-mono text-gray-900">{{ part.ean }}</span>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="mt-4 flex items-center space-x-4">
      <button
        @click="toggleWishlist"
        :class="[
          'flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
          isInWishlist ? 'bg-red-100 text-red-700 hover:bg-red-200' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        <svg class="w-4 h-4" :fill="isInWishlist ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
        <span class="font-persian">{{ isInWishlist ? 'حذف از علاقه‌مندی‌ها' : 'افزودن به علاقه‌مندی‌ها' }}</span>
      </button>
      
      <button
        @click="toggleCompare"
        :class="[
          'flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
          isInCompare ? 'bg-blue-100 text-blue-700 hover:bg-blue-200' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <span class="font-persian">{{ isInCompare ? 'حذف از مقایسه' : 'افزودن به مقایسه' }}</span>
      </button>
    </div>

    <!-- Share Actions -->
    <div class="mt-4 pt-4 border-t border-gray-200">
      <div class="flex items-center justify-between">
        <span class="text-sm text-gray-600 font-persian text-rtl">اشتراک‌گذاری:</span>
        <div class="flex items-center space-x-2">
          <button
            @click="shareOnWhatsApp"
            class="p-2 text-green-600 hover:bg-green-50 rounded-full transition-colors"
            title="اشتراک در واتساپ"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
            </svg>
          </button>
          <button
            @click="shareOnTelegram"
            class="p-2 text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
            title="اشتراک در تلگرام"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
            </svg>
          </button>
          <button
            @click="copyLink"
            class="p-2 text-gray-600 hover:bg-gray-50 rounded-full transition-colors"
            title="کپی لینک"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'TitleBlock',
  props: {
    part: {
      type: Object,
      required: true
    }
  },
  emits: ['wishlist-toggle', 'compare-toggle'],
  setup(props, { emit }) {
    const isInWishlist = ref(false)
    const isInCompare = ref(false)

    // Computed properties
    const badges = computed(() => {
      const badgeList = []
      
      if (props.part.isOEM) {
        badgeList.push({ type: 'oem', text: 'اصلی' })
      }
      
      if (props.part.isBestSeller) {
        badgeList.push({ type: 'bestseller', text: 'پرفروش' })
      }
      
      if (props.part.isNew) {
        badgeList.push({ type: 'new', text: 'جدید' })
      }
      
      if (props.part.isAuthorized) {
        badgeList.push({ type: 'authorized', text: 'مجاز' })
      }
      
      return badgeList
    })

    const badgeClasses = {
      oem: 'bg-green-100 text-green-800',
      bestseller: 'bg-blue-100 text-blue-800',
      new: 'bg-purple-100 text-purple-800',
      authorized: 'bg-yellow-100 text-yellow-800'
    }

    // Methods
    const toggleWishlist = () => {
      isInWishlist.value = !isInWishlist.value
      emit('wishlist-toggle', {
        part: props.part,
        isInWishlist: isInWishlist.value
      })
    }

    const toggleCompare = () => {
      isInCompare.value = !isInCompare.value
      emit('compare-toggle', {
        part: props.part,
        isInCompare: isInCompare.value
      })
    }

    const shareOnWhatsApp = () => {
      const url = encodeURIComponent(window.location.href)
      const text = encodeURIComponent(`نگاه کنید به این قطعه: ${props.part.name}`)
      window.open(`https://wa.me/?text=${text}%20${url}`, '_blank')
    }

    const shareOnTelegram = () => {
      const url = encodeURIComponent(window.location.href)
      const text = encodeURIComponent(`نگاه کنید به این قطعه: ${props.part.name}`)
      window.open(`https://t.me/share/url?url=${url}&text=${text}`, '_blank')
    }

    const copyLink = async () => {
      try {
        await navigator.clipboard.writeText(window.location.href)
        // Show success message
        console.log('Link copied to clipboard')
      } catch (error) {
        console.error('Failed to copy link:', error)
      }
    }

    return {
      isInWishlist,
      isInCompare,
      badges,
      badgeClasses,
      toggleWishlist,
      toggleCompare,
      shareOnWhatsApp,
      shareOnTelegram,
      copyLink
    }
  }
}
</script>
