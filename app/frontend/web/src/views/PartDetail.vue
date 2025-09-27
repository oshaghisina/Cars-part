<template>
  <div class="part-detail min-h-screen bg-gray-50">
    <!-- Enhanced Breadcrumb Navigation -->
    <div class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <nav class="flex" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-1 md:space-x-3">
            <!-- Home -->
            <li class="inline-flex items-center">
              <router-link 
                to="/" 
                class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
              >
                <svg class="w-3 h-3 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="m19.707 9.293-2-2-7-7a1 1 0 0 0-1.414 0l-7 7-2 2a1 1 0 0 0 1.414 1.414L2 10.414V18a2 2 0 0 0 2 2h3a1 1 0 0 0 1-1v-4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v4a1 1 0 0 0 1 1h3a2 2 0 0 0 2-2v-7.586l.293.293a1 1 0 0 0 1.414-1.414Z"/>
                </svg>
                <span class="font-persian">خانه</span>
              </router-link>
            </li>
            
            <!-- Products -->
            <li>
              <div class="flex items-center">
                <svg class="w-3 h-3 text-gray-400 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
                <router-link 
                  to="/products" 
                  class="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors font-persian"
                >
                  محصولات
                </router-link>
              </div>
            </li>
            
            <!-- Category (if available) -->
            <li v-if="part?.category">
              <div class="flex items-center">
                <svg class="w-3 h-3 text-gray-400 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
                <router-link 
                  :to="getCategoryLink()" 
                  class="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors font-persian"
                >
                  {{ part.category }}
                </router-link>
              </div>
            </li>
            
            <!-- Subcategory (if available) -->
            <li v-if="part?.subcategory">
              <div class="flex items-center">
                <svg class="w-3 h-3 text-gray-400 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
                <router-link 
                  :to="getSubcategoryLink()" 
                  class="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors font-persian"
                >
                  {{ part.subcategory }}
                </router-link>
              </div>
            </li>
            
            <!-- Vehicle Make/Model (if available) -->
            <li v-if="part?.vehicle_make && part?.vehicle_model">
              <div class="flex items-center">
                <svg class="w-3 h-3 text-gray-400 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
                <router-link 
                  :to="getVehicleLink()" 
                  class="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors font-persian"
                >
                  {{ part.vehicle_make }} {{ part.vehicle_model }}
                </router-link>
              </div>
            </li>
            
            <!-- Current Product -->
            <li>
              <div class="flex items-center">
                <svg class="w-3 h-3 text-gray-400 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
                <span class="ml-1 text-sm font-medium text-gray-500 truncate max-w-xs font-persian" :title="part?.name">
                  {{ part?.name || 'نام قطعه' }}
                </span>
              </div>
            </li>
          </ol>
        </nav>
      </div>
    </div>

    <!-- Enhanced Loading State -->
    <div v-if="loading" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2 font-persian-bold text-rtl">در حال بارگذاری</h3>
        <p class="text-gray-600 font-persian text-rtl mb-4">در حال بارگذاری جزئیات قطعه...</p>
        
        <!-- Loading skeleton -->
        <div class="mt-8 max-w-4xl mx-auto">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Image skeleton -->
            <div class="space-y-4">
              <div class="bg-gray-200 rounded-lg h-64 animate-pulse"></div>
              <div class="flex space-x-2 space-x-reverse">
                <div class="bg-gray-200 rounded h-16 w-16 animate-pulse"></div>
                <div class="bg-gray-200 rounded h-16 w-16 animate-pulse"></div>
                <div class="bg-gray-200 rounded h-16 w-16 animate-pulse"></div>
              </div>
            </div>
            
            <!-- Content skeleton -->
            <div class="space-y-6">
              <div class="space-y-2">
                <div class="bg-gray-200 h-6 rounded animate-pulse"></div>
                <div class="bg-gray-200 h-4 rounded animate-pulse w-3/4"></div>
                <div class="bg-gray-200 h-4 rounded animate-pulse w-1/2"></div>
              </div>
              <div class="bg-gray-200 h-12 rounded animate-pulse"></div>
              <div class="bg-gray-200 h-32 rounded animate-pulse"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main PDP Content -->
    <div v-else-if="part" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Fitment Bar (Critical) -->
      <FitmentBar
        @compatibility-changed="handleCompatibilityChanged"
      />

      <!-- Main Product Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Media Gallery -->
        <MediaGallery :part="part" />

        <!-- Product Information & Buy Box -->
        <div class="space-y-6">
          <!-- Title Block -->
          <TitleBlock
            :part="part"
            @wishlist-toggle="handleWishlistToggle"
            @compare-toggle="handleCompareToggle"
          />

          <!-- Buy Box -->
          <BuyBox
            :part="part"
            :compatibility-status="compatibilityStatus"
            :is-pro-user="isProUser"
            @add-to-cart="handleAddToCart"
            @buy-now="handleBuyNow"
            @add-to-quote="handleAddToQuote"
          />
        </div>
      </div>

      <!-- Product Details Sections -->
      <div class="mt-8 space-y-8">
        <!-- Specifications -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 font-persian-bold text-rtl">مشخصات فنی</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="spec in specifications" :key="spec.name" class="flex flex-col p-3 bg-gray-50 rounded-lg">
              <span class="text-sm font-medium text-gray-700 font-persian text-rtl mb-1">{{ spec.name }}</span>
              <span class="text-gray-900 font-semibold font-persian text-rtl">{{ spec.value }}</span>
            </div>
          </div>
        </div>

        <!-- Enhanced Cross References Component (Lazy Loaded) -->
        <LazyWrapper 
          skeleton-height="400px"
          root-margin="150px 0px"
          @visible="handleCrossReferencesVisible"
          @loaded="handleCrossReferencesLoaded"
        >
          <CrossReferences
            :part="part"
            @view-alternative="handleViewAlternative"
            @add-to-cart="handleAddAlternativeToCart"
            @view-supersession="handleViewSupersession"
            @contact-support="handleContactSupport"
          />
        </LazyWrapper>
      </div>

      <!-- PDP Test Component (Development Only - Lazy Loaded) -->
      <div v-if="showTestComponent" class="mt-8">
        <LazyWrapper 
          skeleton-height="200px"
          :show-skeleton-content="false"
          root-margin="50px 0px"
        >
          <PDPTest />
        </LazyWrapper>
      </div>
    </div>

    <!-- Enhanced Error State -->
    <div v-else class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center">
        <div class="text-6xl mb-4">❌</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian-bold text-rtl">
          {{ error ? 'خطا در بارگذاری قطعه' : 'قطعه یافت نشد' }}
        </h3>
        <p class="text-gray-600 mb-6 font-persian text-rtl max-w-md mx-auto">
          {{ error || 'قطعه مورد نظر یافت نشد. ممکن است این قطعه حذف شده یا در دسترس نباشد.' }}
        </p>
        
        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <router-link
            to="/products"
            class="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors font-persian"
          >
            مشاهده همه محصولات
          </router-link>
          <router-link
            to="/search"
            class="border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors font-persian"
          >
            جستجوی قطعات
          </router-link>
          <button
            @click="loadPart"
            class="border border-blue-300 text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors font-persian"
          >
            تلاش مجدد
          </button>
        </div>
        
        <!-- Help Text -->
        <div class="mt-8 p-4 bg-gray-50 rounded-lg max-w-lg mx-auto">
          <p class="text-sm text-gray-600 font-persian text-rtl">
            اگر مطمئن هستید که این قطعه باید موجود باشد، لطفاً با تیم پشتیبانی تماس بگیرید.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import FitmentBar from '@/components/pdp/FitmentBar.vue'
import MediaGallery from '@/components/pdp/MediaGallery.vue'
import TitleBlock from '@/components/pdp/TitleBlock.vue'
import BuyBox from '@/components/pdp/BuyBox.vue'
import CrossReferences from '@/components/pdp/CrossReferences.vue'
import PDPTest from '@/components/pdp/PDPTest.vue'
import LazyWrapper from '@/components/shared/LazyWrapper.vue'
import { usePDP } from '@/composables/usePDP.js'
import { useAnalytics } from '@/composables/useAnalytics.js'

export default {
  name: 'PartDetail',
  components: {
    FitmentBar,
    MediaGallery,
    TitleBlock,
    BuyBox,
    CrossReferences,
    PDPTest,
    LazyWrapper
  },
  setup() {
    const {
      part,
      loading,
      error,
      compatibilityStatus,
      isProUser,
      isAuthenticated,
      isInWishlist,
      isInCompare,
      canAddToCart,
      loadPart,
      checkCompatibility,
      addToCart,
      addToQuote,
      toggleWishlist,
      toggleCompare,
      loadUserData,
      trackPDPView
    } = usePDP()

    const { trackPDPView: trackView } = useAnalytics()

    // Mock data - will be replaced with API calls
    const specifications = ref([
      { name: 'جنس', value: 'سرامیک' },
      { name: 'ابعاد', value: '120x80x15 میلیمتر' },
      { name: 'وزن', value: '1.2 کیلوگرم' },
      { name: 'گارانتی', value: '12 ماه' },
      { name: 'کشور سازنده', value: 'چین' },
      { name: 'استاندارد', value: 'ISO 9001' }
    ])

    const oemReferences = ref([
      { brand: 'BYD', code: 'BP-F3-2020' },
      { brand: 'Chery', code: 'CH-BP-001' },
      { brand: 'Geely', code: 'GL-BP-F3' }
    ])

    // Development flag for test component
    const showTestComponent = ref(import.meta.env.DEV)

    // Event handlers for component events
    const handleCompatibilityChanged = async (data) => {
      if (data.method && data.result) {
        await checkCompatibility(data.method, data.vehicleId || '')
      }
    }

    const handleWishlistToggle = async (data) => {
      try {
        await toggleWishlist()
      } catch (error) {
        console.error('Error toggling wishlist:', error)
        alert('خطا در افزودن/حذف از علاقه‌مندی‌ها')
      }
    }

    const handleCompareToggle = async (data) => {
      try {
        await toggleCompare()
      } catch (error) {
        console.error('Error toggling compare:', error)
        alert('خطا در افزودن/حذف از مقایسه')
      }
    }

    const handleAddToCart = async (data) => {
      try {
        await addToCart(data.quantity, isProUser.value ? 'pro' : 'retail')
        alert(`افزوده شد به سبد خرید: ${data.quantity} عدد ${data.part.name}`)
      } catch (error) {
        console.error('Error adding to cart:', error)
        alert('خطا در افزودن به سبد خرید')
      }
    }

    const handleBuyNow = async (data) => {
      try {
        // For now, just add to cart and redirect to checkout
        await addToCart(data.quantity, isProUser.value ? 'pro' : 'retail')
        alert(`خرید فوری: ${data.quantity} عدد ${data.part.name}`)
        // TODO: Redirect to checkout page
      } catch (error) {
        console.error('Error with buy now:', error)
        alert('خطا در خرید فوری')
      }
    }

    const handleAddToQuote = async (data) => {
      try {
        await addToQuote(data.quantity)
        alert(`افزوده شد به پیش‌فاکتور: ${data.quantity} عدد ${data.part.name}`)
      } catch (error) {
        console.error('Error adding to quote:', error)
        alert('خطا در افزودن به پیش‌فاکتور')
      }
    }

    // CrossReferences event handlers
    const handleViewAlternative = (alternative) => {
      console.log('Viewing alternative part:', alternative)
      // Navigate to alternative part detail page
      // this.$router.push(`/part/${alternative.id}`)
    }

    const handleAddAlternativeToCart = async (data) => {
      try {
        await addToCart(data.part, data.quantity)
        alert(`قطعه جایگزین "${data.part.name}" به سبد خرید اضافه شد`)
      } catch (error) {
        console.error('Error adding alternative to cart:', error)
        alert('خطا در افزودن قطعه جایگزین به سبد خرید')
      }
    }

    const handleViewSupersession = (supersession) => {
      console.log('Viewing supersession:', supersession)
      // Navigate to supersession part detail page or show modal
      // this.$router.push(`/part/${supersession.partId}`)
    }

    const handleContactSupport = (data) => {
      console.log('Contacting support for cross-reference help:', data)
      // Open support modal or redirect to contact page
      // this.$router.push('/contact?reason=cross-reference-help')
      alert('ارتباط با پشتیبانی برای راهنمایی در مورد قطعات جایگزین')
    }

    // Lazy Loading Event Handlers
    const handleCrossReferencesVisible = () => {
      console.log('🔍 Cross References section is visible, starting to load...')
      // Track lazy loading analytics
      trackEvent('lazy_load_start', {
        component: 'cross_references',
        part_id: part.value?.id
      })
    }

    const handleCrossReferencesLoaded = () => {
      console.log('✅ Cross References loaded successfully')
      // Track successful lazy loading
      trackEvent('lazy_load_complete', {
        component: 'cross_references',
        part_id: part.value?.id
      })
    }

    // Breadcrumb link methods
    const getCategoryLink = () => {
      if (!part.value?.category) return '/products'
      // Convert category name to slug for filtering
      const categorySlug = part.value.category.toLowerCase().replace(/\s+/g, '-')
      return {
        name: 'Products',
        query: {
          category: categorySlug,
          categoryName: part.value.category
        }
      }
    }

    const getSubcategoryLink = () => {
      if (!part.value?.subcategory) return getCategoryLink()
      // Create a more specific filter for subcategory
      return {
        name: 'Products',
        query: {
          category: part.value.category,
          subcategory: part.value.subcategory,
          categoryName: `${part.value.category} - ${part.value.subcategory}`
        }
      }
    }

    const getVehicleLink = () => {
      if (!part.value?.vehicle_make || !part.value?.vehicle_model) return '/products'
      return {
        name: 'Products',
        query: {
          vehicleMake: part.value.vehicle_make,
          vehicleModel: part.value.vehicle_model,
          categoryName: `${part.value.vehicle_make} ${part.value.vehicle_model}`
        }
      }
    }

    // Lifecycle
    onMounted(async () => {
      await loadUserData()
      await loadPart()
      if (part.value) {
        await trackPDPView()
      }
    })

    return {
      part,
      loading,
      error,
      compatibilityStatus,
      isProUser,
      isAuthenticated,
      isInWishlist,
      isInCompare,
      canAddToCart,
      specifications,
      showTestComponent,
      handleCompatibilityChanged,
      handleWishlistToggle,
      handleCompareToggle,
      handleAddToCart,
      handleBuyNow,
      handleAddToQuote,
      handleViewAlternative,
      handleAddAlternativeToCart,
      handleViewSupersession,
      handleContactSupport,
      handleCrossReferencesVisible,
      handleCrossReferencesLoaded,
      getCategoryLink,
      getSubcategoryLink,
      getVehicleLink
    }
  }
}
</script>
