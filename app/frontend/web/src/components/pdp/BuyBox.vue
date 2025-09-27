<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <!-- Price Tiers Section -->
    <div class="mb-6">
      <!-- Price Display -->
      <div class="space-y-3">
        <!-- Retail Price -->
        <div v-if="!isProUser || showBothPrices" class="flex items-center justify-between">
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-bold text-gray-900 font-persian">{{ formatPrice(currentPrice) }}</span>
            <span class="text-sm text-gray-500 font-persian">{{ getCurrencySymbol(part.priceInfo?.currency || 'IRR') }}</span>
            <span v-if="originalPrice && originalPrice > currentPrice" class="text-sm text-gray-400 line-through font-persian">
              {{ formatPrice(originalPrice) }}
            </span>
          </div>
          <div class="text-right">
            <span v-if="!isProUser" class="text-xs text-gray-500 font-persian bg-gray-100 px-2 py-1 rounded">قیمت خرده</span>
          </div>
        </div>

        <!-- Pro Price (if pro user) -->
        <div v-if="isProUser" class="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div class="flex items-baseline gap-2">
            <span class="text-3xl font-bold text-blue-600 font-persian">{{ formatPrice(proPrice) }}</span>
            <span class="text-sm text-blue-500 font-persian">{{ getCurrencySymbol(part.priceInfo?.currency || 'IRR') }}</span>
            <span v-if="proSavings > 0" class="text-sm text-green-600 font-persian">
              ({{ proSavingsPercent }}% تخفیف حرفه‌ای)
            </span>
          </div>
          <div class="text-right">
            <span class="text-xs text-blue-600 font-persian bg-blue-100 px-2 py-1 rounded">قیمت حرفه‌ای</span>
          </div>
        </div>

        <!-- Quantity Breaks (if available) -->
        <div v-if="quantityBreaks.length > 0 && quantity >= 2" class="bg-green-50 border border-green-200 rounded-lg p-3">
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span class="text-sm font-medium text-green-800 font-persian">تخفیف مقداری فعال!</span>
          </div>
          <div class="text-sm text-green-700 font-persian">
            قیمت واحد: {{ formatPrice(quantityBreakPrice) }} تومان
            ({{ quantityBreakSavings }}% تخفیف)
          </div>
        </div>
      </div>

      <!-- Stock Information -->
      <div class="flex items-center justify-between mt-4 p-3 bg-gray-50 rounded-lg">
        <div class="flex items-center gap-2">
          <div :class="stockClasses" class="px-3 py-1 rounded-full text-sm font-medium font-persian">
            {{ stockMessage }}
          </div>
          <div v-if="part.stockInfo && part.stockInfo.in_stock" class="text-sm text-gray-600 font-persian">
            ({{ part.stockInfo.current_stock - part.stockInfo.reserved_quantity }} عدد موجود)
          </div>
        </div>
        
        <!-- Advanced Stock Info -->
        <div class="text-right">
          <div v-if="stockWarning" class="text-sm text-orange-600 font-persian mb-1">
            {{ stockWarning }}
          </div>
          <div v-if="nextStockDate" class="text-xs text-gray-500 font-persian">
            موجودی بعدی: {{ nextStockDate }}
          </div>
        </div>
      </div>
      
      <!-- Delivery Estimation -->
      <div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-sm font-medium text-blue-800 font-persian">تحویل در {{ deliveryEstimate }}</span>
          </div>
          <div class="text-right">
            <select 
              v-model="selectedCity" 
              @change="updateDeliveryEstimate"
              class="text-xs border border-blue-300 rounded px-2 py-1 font-persian text-rtl bg-white"
            >
              <option value="">انتخاب شهر</option>
              <option v-for="city in cities" :key="city.id" :value="city.id">
                {{ city.name }}
              </option>
            </select>
          </div>
        </div>
        <div v-if="expressDelivery" class="mt-2 text-xs text-blue-600 font-persian">
          💨 ارسال فوری {{ expressDelivery }} (هزینه اضافی {{ formatPrice(expressDelivery.cost) }} تومان)
        </div>
      </div>
    </div>

    <!-- Enhanced Quantity Selector -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <label class="text-sm font-medium text-gray-700 font-persian text-rtl">تعداد</label>
        <div v-if="totalPrice !== currentPrice * quantity" class="text-sm text-green-600 font-persian">
          جمع: {{ formatPrice(totalPrice) }} تومان
        </div>
      </div>
      
      <div class="flex items-center gap-3">
        <div class="flex items-center border border-gray-300 rounded-lg">
          <button
            @click="decreaseQuantity"
            :disabled="quantity <= minQuantity"
            class="w-10 h-10 flex items-center justify-center hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors rounded-r-lg"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
            </svg>
          </button>
          
          <input
            v-model.number="quantity"
            @blur="validateQuantity"
            @keyup.enter="validateQuantity"
            type="number"
            :min="minQuantity"
            :max="maxQuantity"
            class="w-16 h-10 text-center font-medium font-persian border-0 focus:ring-0"
          />
          
          <button
            @click="increaseQuantity"
            :disabled="quantity >= maxQuantity"
            class="w-10 h-10 flex items-center justify-center hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors rounded-l-lg"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
        </div>
        
        <!-- Quick Quantity Buttons -->
        <div v-if="quickQuantities.length > 0" class="flex gap-1">
          <button
            v-for="qty in quickQuantities"
            :key="qty"
            @click="setQuantity(qty)"
            :class="[
              'px-2 py-1 text-xs rounded border transition-colors font-persian',
              quantity === qty 
                ? 'bg-blue-100 text-blue-700 border-blue-300' 
                : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'
            ]"
          >
            {{ qty }}
          </button>
        </div>
      </div>
      
      <!-- Quantity Hints -->
      <div class="mt-2 space-y-1">
        <div v-if="moqWarning" class="text-sm text-orange-600 font-persian">
          {{ moqWarning }}
        </div>
        <div v-if="nextQuantityBreak" class="text-sm text-green-600 font-persian">
          💡 {{ nextQuantityBreak.message }}
        </div>
        <div v-if="bulkDiscountHint" class="text-sm text-blue-600 font-persian">
          🔥 {{ bulkDiscountHint }}
        </div>
      </div>
    </div>

    <!-- Enhanced Action Buttons -->
    <div class="space-y-3">
      <!-- Primary Add to Cart Button -->
      <button
        @click="addToCart"
        :disabled="!canAddToCart"
        :class="[
          'w-full py-3 rounded-lg font-semibold transition-all duration-200 font-persian flex items-center justify-center gap-2',
          canAddToCart 
            ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg transform hover:-translate-y-0.5' 
            : 'bg-gray-400 text-gray-200 cursor-not-allowed'
        ]"
      >
        <svg v-if="addingToCart" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13v6a1 1 0 001 1h9a1 1 0 001-1v-6M7 13H5a2 2 0 01-2-2V9a2 2 0 012-2h2" />
        </svg>
        {{ addingToCart ? 'در حال افزودن...' : addToCartText }}
      </button>
      
      <!-- Secondary Action Buttons -->
      <div class="grid grid-cols-2 gap-3">
        <!-- Buy Now Button -->
        <button
          @click="buyNow"
          :disabled="!canAddToCart"
          class="flex-1 border-2 border-blue-600 text-blue-600 py-2.5 rounded-lg font-semibold hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-persian flex items-center justify-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          خرید فوری
        </button>
        
        <!-- Compare/Wishlist Button -->
        <button
          @click="toggleWishlist"
          :class="[
            'flex-1 border-2 py-2.5 rounded-lg font-semibold transition-colors font-persian flex items-center justify-center gap-2',
            isInWishlist 
              ? 'border-red-600 text-red-600 bg-red-50' 
              : 'border-gray-300 text-gray-600 hover:bg-gray-50'
          ]"
        >
          <svg class="w-4 h-4" :class="{ 'fill-current': isInWishlist }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          {{ isInWishlist ? 'حذف' : 'علاقه' }}
        </button>
      </div>
      
      <!-- Alternative Actions (if out of stock or incompatible) -->
      <div v-if="!canAddToCart && part.stock === 0" class="space-y-2">
        <button
          @click="notifyWhenAvailable"
          class="w-full border-2 border-orange-500 text-orange-600 py-2.5 rounded-lg font-semibold hover:bg-orange-50 transition-colors font-persian flex items-center justify-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM5 12h14M5 8h14m-7 8h7" />
          </svg>
          اطلاع از موجود شدن
        </button>
        
        <!-- Alternative Products Button -->
        <button
          @click="showAlternatives"
          class="w-full border-2 border-green-500 text-green-600 py-2.5 rounded-lg font-semibold hover:bg-green-50 transition-colors font-persian flex items-center justify-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          مشاهده محصولات جایگزین
        </button>
      </div>

      <!-- Compatibility Warning Actions -->
      <div v-if="compatibilityStatus === 'incompatible'" class="p-3 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <span class="text-sm font-medium text-red-800 font-persian">قطعه مناسب خودروی شما نیست</span>
        </div>
        <button
          @click="showCompatibleParts"
          class="w-full bg-red-600 text-white py-2 rounded-lg font-semibold hover:bg-red-700 transition-colors font-persian text-sm"
        >
          مشاهده قطعات مناسب
        </button>
      </div>
    </div>

    <!-- Pro User Features -->
    <div v-if="isProUser" class="mt-6 pt-6 border-t border-gray-200">
      <h4 class="text-sm font-semibold text-gray-900 mb-3 font-persian-bold text-rtl">قیمت‌گذاری حرفه‌ای</h4>
      <div class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-600 font-persian text-rtl">قیمت خالص:</span>
          <span class="font-medium font-persian">{{ formatPrice(part.proNet || part.price) }}</span>
        </div>
        <div v-if="part.moq" class="flex justify-between">
          <span class="text-gray-600 font-persian text-rtl">حداقل سفارش:</span>
          <span class="font-medium font-persian">{{ part.moq }} عدد</span>
        </div>
      </div>
      
      <button
        @click="addToQuote"
        :disabled="!canAddToCart"
        class="w-full mt-3 bg-green-600 text-white py-2 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-persian"
      >
        افزودن به پیش‌فاکتور
      </button>
    </div>

    <!-- Trust Indicators -->
    <div class="mt-6 pt-6 border-t border-gray-200">
      <div class="flex items-center justify-center space-x-6 text-xs text-gray-500 font-persian">
        <div class="flex items-center gap-1">
          <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <span>گارانتی {{ part.warranty || '12' }} ماهه</span>
        </div>
        <div class="flex items-center gap-1">
          <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
          <span>ارسال سریع</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'BuyBox',
  props: {
    part: {
      type: Object,
      required: true
    },
    compatibilityStatus: {
      type: String,
      default: null
    },
    isProUser: {
      type: Boolean,
      default: false
    },
    userLocation: {
      type: Object,
      default: () => ({ city: 'tehran', cityName: 'تهران' })
    }
  },
  emits: ['add-to-cart', 'buy-now', 'add-to-quote', 'notify-when-available', 'show-alternatives', 'show-compatible-parts', 'toggle-wishlist'],
  setup(props, { emit }) {
    // Quantity and cart state
    const quantity = ref(1)
    const addingToCart = ref(false)
    const selectedCity = ref(props.userLocation?.city || 'tehran')
    const isInWishlist = ref(false)
    const showBothPrices = ref(false)

    // Delivery and pricing data
    const cities = ref([
      { id: 'tehran', name: 'تهران', deliveryDays: 1, expressHours: 3 },
      { id: 'mashhad', name: 'مشهد', deliveryDays: 2, expressHours: 6 },
      { id: 'isfahan', name: 'اصفهان', deliveryDays: 2, expressHours: 4 },
      { id: 'shiraz', name: 'شیراز', deliveryDays: 3, expressHours: 8 },
      { id: 'tabriz', name: 'تبریز', deliveryDays: 3, expressHours: 12 },
      { id: 'ahvaz', name: 'اهواز', deliveryDays: 3, expressHours: 10 }
    ])

    // Mock quantity breaks data
    const quantityBreaks = ref([
      { minQty: 2, discount: 5, price: 0 },
      { minQty: 5, discount: 10, price: 0 },
      { minQty: 10, discount: 15, price: 0 },
      { minQty: 20, discount: 20, price: 0 }
    ])

    // Initialize quantity breaks with actual prices
    const initializeQuantityBreaks = () => {
      if (props.part?.price) {
        quantityBreaks.value.forEach(qb => {
          qb.price = Math.round(props.part.price * (1 - qb.discount / 100))
        })
      }
    }

    // Computed properties for pricing
    const originalPrice = computed(() => props.part?.priceInfo?.list_price || 0)
    
    const retailPrice = computed(() => {
      if (props.part?.priceInfo) {
        return parseFloat(props.part.priceInfo.effective_price) || 0
      }
      return props.part?.price || 0 // Fallback to old price field
    })
    
    const proPrice = computed(() => {
      if (!props.isProUser) return retailPrice.value
      return props.part?.proPrice || Math.round(retailPrice.value * 0.85) // 15% pro discount
    })

    const currentPrice = computed(() => {
      return props.isProUser ? proPrice.value : retailPrice.value
    })

    const proSavings = computed(() => {
      if (!props.isProUser) return 0
      return retailPrice.value - proPrice.value
    })

    const proSavingsPercent = computed(() => {
      if (proSavings.value <= 0 || retailPrice.value <= 0) return 0
      return Math.round((proSavings.value / retailPrice.value) * 100)
    })

    // Quantity break logic
    const currentQuantityBreak = computed(() => {
      return quantityBreaks.value
        .filter(qb => quantity.value >= qb.minQty)
        .sort((a, b) => b.minQty - a.minQty)[0]
    })

    const quantityBreakPrice = computed(() => {
      return currentQuantityBreak.value?.price || currentPrice.value
    })

    const quantityBreakSavings = computed(() => {
      return currentQuantityBreak.value?.discount || 0
    })

    const nextQuantityBreak = computed(() => {
      const next = quantityBreaks.value.find(qb => qb.minQty > quantity.value)
      if (!next) return null
      
      const needed = next.minQty - quantity.value
      const savings = Math.round((currentPrice.value - next.price) * next.minQty)
      
      return {
        minQty: next.minQty,
        needed,
        discount: next.discount,
        savings,
        message: `${needed} عدد دیگر بخرید و ${next.discount}% تخفیف بگیرید (${formatPrice(savings)} تومان صرفه‌جویی)`
      }
    })

    const totalPrice = computed(() => {
      const unitPrice = quantityBreakPrice.value
      return unitPrice * quantity.value
    })

    // Stock and quantity validation
    const minQuantity = computed(() => {
      if (props.isProUser && props.part?.moq) {
        return props.part.moq
      }
      return 1
    })

    const maxQuantity = computed(() => {
      if (!props.part) return 1
      const availableStock = props.part?.stockInfo?.in_stock ? 
        (props.part.stockInfo.current_stock - props.part.stockInfo.reserved_quantity) : 0
      return Math.min(availableStock, 999) // Maximum 999 for UI purposes
    })

    const quickQuantities = computed(() => {
      if (!props.part) return []
      
      const base = [1, 2, 5, 10]
      const breaks = quantityBreaks.value.map(qb => qb.minQty)
      const moq = props.part.moq || 1
      
      const all = [...new Set([...base, ...breaks, moq])]
        .filter(q => q <= maxQuantity.value)
        .sort((a, b) => a - b)
      
      return all.slice(0, 6) // Show max 6 quick options
    })

    const stockMessage = computed(() => {
      if (!props.part) return ''
      const availableStock = props.part?.stockInfo?.in_stock ? 
        (props.part.stockInfo.current_stock - props.part.stockInfo.reserved_quantity) : 0
      
      if (availableStock === 0) return 'ناموجود'
      if (availableStock <= 5) return 'کم موجود'
      if (availableStock <= 20) return 'موجود محدود'
      return 'موجود'
    })

    const stockClasses = computed(() => {
      if (!props.part) return 'bg-gray-100 text-gray-800'
      const availableStock = props.part?.stockInfo?.in_stock ? 
        (props.part.stockInfo.current_stock - props.part.stockInfo.reserved_quantity) : 0
      
      if (availableStock === 0) return 'bg-red-100 text-red-800'
      if (availableStock <= 5) return 'bg-orange-100 text-orange-800'
      if (availableStock <= 20) return 'bg-yellow-100 text-yellow-800'
      return 'bg-green-100 text-green-800'
    })

    const stockWarning = computed(() => {
      if (!props.part) return ''
      const availableStock = props.part?.stockInfo?.in_stock ? 
        (props.part.stockInfo.current_stock - props.part.stockInfo.reserved_quantity) : 0
      
      if (availableStock <= 3 && availableStock > 0) {
        return `تنها ${availableStock} عدد باقی مانده!`
      }
      if (quantity.value > availableStock) {
        return `حداکثر ${availableStock} عدد موجود است`
      }
      return ''
    })

    const nextStockDate = computed(() => {
      if (props.part?.stock > 0) return ''
      // Mock next stock date
      const date = new Date()
      date.setDate(date.getDate() + 7)
      return date.toLocaleDateString('fa-IR')
    })

    const moqWarning = computed(() => {
      if (!props.isProUser || !props.part?.moq) return ''
      if (quantity.value < props.part.moq) {
        return `حداقل سفارش ${props.part.moq} عدد می‌باشد`
      }
      return ''
    })

    const bulkDiscountHint = computed(() => {
      if (quantity.value < 10) return ''
      const savings = Math.round(totalPrice.value * 0.02) // 2% bulk discount hint
      return `سفارش بالای 50 عدد: 2% تخفیف اضافی (${formatPrice(savings)} تومان)`
    })

    // Delivery estimation
    const selectedCityData = computed(() => {
      return cities.value.find(c => c.id === selectedCity.value) || cities.value[0]
    })

    const deliveryEstimate = computed(() => {
      const city = selectedCityData.value
      if (!city) return '2-3 روز کاری'
      
      if (city.deliveryDays === 1) return 'فردا'
      if (city.deliveryDays === 2) return 'پس‌فردا'
      return `${city.deliveryDays} روز کاری`
    })

    const expressDelivery = computed(() => {
      const city = selectedCityData.value
      if (!city || !city.expressHours) return null
      
      return {
        hours: city.expressHours,
        cost: 50000, // 50k toman express fee
        label: city.expressHours <= 6 ? `${city.expressHours} ساعته` : 'همان روز'
      }
    })

    // Add to cart validation
    const canAddToCart = computed(() => {
      if (!props.part) return false
      const availableStock = props.part?.stockInfo?.in_stock ? 
        (props.part.stockInfo.current_stock - props.part.stockInfo.reserved_quantity) : 0
      
      return availableStock > 0 && 
             quantity.value <= availableStock &&
             quantity.value >= minQuantity.value &&
             props.compatibilityStatus !== 'incompatible' &&
             !addingToCart.value
    })

    const addToCartText = computed(() => {
      const availableStock = props.part?.stockInfo?.in_stock ? 
        (props.part.stockInfo.current_stock - props.part.stockInfo.reserved_quantity) : 0
      
      if (availableStock === 0) return 'ناموجود'
      if (props.compatibilityStatus === 'incompatible') return 'غیرسازگار'
      if (quantity.value > availableStock) return 'موجودی کافی نیست'
      if (quantity.value < minQuantity.value) return `حداقل ${minQuantity.value} عدد`
      return 'افزودن به سبد خرید'
    })

    // Methods
    const formatPrice = (price) => {
      if (!price || price === 0) return '0'
      return new Intl.NumberFormat('fa-IR').format(price)
    }

    const getCurrencySymbol = (currency) => {
      const symbols = {
        'IRR': 'تومان',
        'USD': '$',
        'EUR': '€'
      }
      return symbols[currency] || currency
    }

    const setQuantity = (qty) => {
      if (qty >= minQuantity.value && qty <= maxQuantity.value) {
        quantity.value = qty
      }
    }

    const increaseQuantity = () => {
      if (quantity.value < maxQuantity.value) {
        quantity.value++
      }
    }

    const decreaseQuantity = () => {
      if (quantity.value > minQuantity.value) {
        quantity.value--
      }
    }

    const validateQuantity = () => {
      if (quantity.value < minQuantity.value) {
        quantity.value = minQuantity.value
      } else if (quantity.value > maxQuantity.value) {
        quantity.value = maxQuantity.value
      }
    }

    const updateDeliveryEstimate = () => {
      // Trigger reactivity for delivery estimation
      console.log('Delivery estimate updated for city:', selectedCity.value)
    }

    // Action handlers
    const addToCart = async () => {
      if (!canAddToCart.value) return
      
      addingToCart.value = true
      
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1200))
        
        // Track analytics event
        console.log('add_to_cart event:', {
          sku: props.part.oemCode,
          qty: quantity.value,
          unitPrice: quantityBreakPrice.value,
          totalPrice: totalPrice.value,
          priceTier: props.isProUser ? 'pro' : 'retail',
          quantityBreakDiscount: quantityBreakSavings.value,
          availability: {
            stockStatus: props.part.stock > 0 ? 'in_stock' : 'out_of_stock',
            availableQty: props.part.stock
          },
          compatible: props.compatibilityStatus === 'compatible',
          deliveryCity: selectedCity.value,
          deliveryEstimate: deliveryEstimate.value
        })
        
        // Emit event to parent
        emit('add-to-cart', {
          part: props.part,
          quantity: quantity.value,
          unitPrice: quantityBreakPrice.value,
          totalPrice: totalPrice.value,
          deliveryInfo: {
            city: selectedCity.value,
            estimate: deliveryEstimate.value
          }
        })
        
      } catch (error) {
        console.error('Error adding to cart:', error)
      } finally {
        addingToCart.value = false
      }
    }

    const buyNow = () => {
      if (!canAddToCart.value) return
      
      // Track analytics event
      console.log('buy_now event:', {
        sku: props.part.oemCode,
        qty: quantity.value,
        totalPrice: totalPrice.value,
        priceTier: props.isProUser ? 'pro' : 'retail'
      })
      
      // Emit event to parent
      emit('buy-now', {
        part: props.part,
        quantity: quantity.value,
        totalPrice: totalPrice.value
      })
    }

    const addToQuote = () => {
      if (!canAddToCart.value) return
      
      // Track analytics event
      console.log('add_to_quote event:', {
        sku: props.part.oemCode,
        qty: quantity.value,
        priceTier: 'pro'
      })
      
      // Emit event to parent
      emit('add-to-quote', {
        part: props.part,
        quantity: quantity.value
      })
    }

    const toggleWishlist = () => {
      isInWishlist.value = !isInWishlist.value
      
      console.log('wishlist_toggle event:', {
        sku: props.part.oemCode,
        action: isInWishlist.value ? 'add' : 'remove'
      })
      
      emit('toggle-wishlist', {
        part: props.part,
        inWishlist: isInWishlist.value
      })
    }

    const notifyWhenAvailable = () => {
      console.log('notify_when_available event:', {
        sku: props.part.oemCode
      })
      
      emit('notify-when-available', {
        part: props.part
      })
    }

    const showAlternatives = () => {
      console.log('show_alternatives event:', {
        sku: props.part.oemCode,
        reason: 'out_of_stock'
      })
      
      emit('show-alternatives', {
        part: props.part,
        reason: 'out_of_stock'
      })
    }

    const showCompatibleParts = () => {
      console.log('show_compatible_parts event:', {
        sku: props.part.oemCode,
        reason: 'incompatible'
      })
      
      emit('show-compatible-parts', {
        part: props.part,
        reason: 'incompatible'
      })
    }

    // Watch for part changes to reinitialize
    watch(() => props.part, () => {
      initializeQuantityBreaks()
      quantity.value = minQuantity.value
    }, { immediate: true })

    // Initialize
    initializeQuantityBreaks()

    return {
      // Reactive data
      quantity,
      addingToCart,
      selectedCity,
      isInWishlist,
      showBothPrices,
      cities,
      quantityBreaks,
      
      // Computed pricing
      originalPrice,
      retailPrice,
      proPrice,
      currentPrice,
      proSavings,
      proSavingsPercent,
      quantityBreakPrice,
      quantityBreakSavings,
      nextQuantityBreak,
      totalPrice,
      
      // Computed quantities and stock
      minQuantity,
      maxQuantity,
      quickQuantities,
      stockMessage,
      stockClasses,
      stockWarning,
      nextStockDate,
      moqWarning,
      bulkDiscountHint,
      
      // Computed delivery
      deliveryEstimate,
      expressDelivery,
      
      // Computed validation
      canAddToCart,
      addToCartText,
      
      // Methods
      formatPrice,
      getCurrencySymbol,
      setQuantity,
      increaseQuantity,
      decreaseQuantity,
      validateQuantity,
      updateDeliveryEstimate,
      addToCart,
      buyNow,
      addToQuote,
      toggleWishlist,
      notifyWhenAvailable,
      showAlternatives,
      showCompatibleParts
    }
  }
}
</script>
