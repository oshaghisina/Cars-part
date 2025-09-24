<template>
  <div class="part-detail min-h-screen bg-gray-50">
    <!-- Breadcrumb Navigation -->
    <div class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <nav class="flex" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-4">
            <li>
              <router-link to="/" class="text-gray-400 hover:text-gray-500 font-persian">
                خانه
              </router-link>
            </li>
            <li>
              <div class="flex items-center">
                <svg class="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                <span class="ml-4 text-sm font-medium text-gray-500 font-persian">{{ part?.category || 'دسته‌بندی' }}</span>
              </div>
            </li>
            <li>
              <div class="flex items-center">
                <svg class="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                <span class="ml-4 text-sm font-medium text-gray-900 font-persian">{{ part?.name || 'نام قطعه' }}</span>
              </div>
            </li>
          </ol>
        </nav>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600 font-persian text-rtl">در حال بارگذاری جزئیات قطعه...</p>
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

    <!-- Error State -->
    <div v-else class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center">
        <div class="text-6xl mb-4">❌</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian-bold text-rtl">قطعه یافت نشد</h3>
        <p class="text-gray-600 mb-4 font-persian text-rtl">قطعه مورد نظر یافت نشد.</p>
        <router-link
          to="/search"
          class="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 font-persian"
        >
          بازگشت به جستجو
        </router-link>
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
      handleCrossReferencesLoaded
    }
  }
}
</script>
