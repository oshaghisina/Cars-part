<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl font-bold text-gray-900 font-persian-bold text-rtl">
        مرجع‌های متقابل و قطعات جایگزین
      </h3>
      <div class="flex gap-2">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'px-4 py-2 text-sm rounded-lg font-persian transition-all',
            activeTab === tab.key 
              ? 'bg-blue-100 text-blue-700 border border-blue-200' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          {{ tab.label }}
          <span v-if="tab.count" class="ml-1 px-2 py-0.5 bg-current bg-opacity-20 rounded-full text-xs">
            {{ tab.count }}
          </span>
        </button>
      </div>
    </div>

    <!-- OEM References Tab -->
    <div v-if="activeTab === 'oem'" class="space-y-4">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-center gap-2 mb-3">
          <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <h4 class="text-lg font-semibold text-blue-800 font-persian-bold text-rtl">
            شماره‌های قطعه اصلی (OEM)
          </h4>
        </div>
        <p class="text-sm text-blue-700 font-persian text-rtl mb-4">
          این قطعه با شماره‌های اصلی زیر سازگار است و می‌تواند جایگزین آنها شود.
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="oem in oemReferences"
            :key="oem.id"
            class="bg-white rounded-lg border border-blue-200 p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="font-semibold text-gray-900 font-persian">{{ oem.brand }}</span>
              <span :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                oem.status === 'active' ? 'bg-green-100 text-green-800' :
                oem.status === 'superseded' ? 'bg-orange-100 text-orange-800' :
                'bg-gray-100 text-gray-800'
              ]">
                {{ getStatusLabel(oem.status) }}
              </span>
            </div>
            <div class="space-y-1">
              <p class="font-mono text-lg text-blue-600 font-semibold">{{ oem.partNumber }}</p>
              <p class="text-sm text-gray-600 font-persian text-rtl">{{ oem.description }}</p>
              <div class="flex items-center justify-between mt-2">
                <span class="text-xs text-gray-500 font-persian">{{ oem.years }}</span>
                <button
                  @click="copyPartNumber(oem.partNumber)"
                  class="text-xs text-blue-600 hover:text-blue-700 font-persian"
                >
                  کپی
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Alternatives Tab -->
    <div v-if="activeTab === 'alternatives'" class="space-y-4">
      <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <div class="flex items-center gap-2 mb-3">
          <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" clip-rule="evenodd" />
          </svg>
          <h4 class="text-lg font-semibold text-green-800 font-persian-bold text-rtl">
            قطعات جایگزین
          </h4>
        </div>
        <p class="text-sm text-green-700 font-persian text-rtl mb-4">
          قطعات زیر می‌توانند جایگزین مناسبی برای این محصول باشند.
        </p>

        <div class="space-y-3">
          <div
            v-for="alternative in alternatives"
            :key="alternative.id"
            class="bg-white rounded-lg border border-green-200 p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <img
                    v-if="alternative.image"
                    :src="alternative.image"
                    :alt="alternative.name"
                    class="w-12 h-12 object-cover rounded border"
                  />
                  <div class="flex-1">
                    <h5 class="font-semibold text-gray-900 font-persian text-rtl">{{ alternative.name }}</h5>
                    <p class="text-sm text-gray-600 font-persian text-rtl">{{ alternative.brand }} - {{ alternative.sku }}</p>
                  </div>
                </div>
                
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  <div>
                    <span class="text-gray-500 font-persian">قیمت:</span>
                    <span class="font-semibold text-blue-600 font-persian mr-1">{{ formatPrice(alternative.price) }}</span>
                  </div>
                  <div>
                    <span class="text-gray-500 font-persian">موجودی:</span>
                    <span :class="[
                      'font-semibold mr-1',
                      alternative.stock > 0 ? 'text-green-600' : 'text-red-600'
                    ]">
                      {{ alternative.stock > 0 ? `${alternative.stock} عدد` : 'ناموجود' }}
                    </span>
                  </div>
                  <div>
                    <span class="text-gray-500 font-persian">سازگاری:</span>
                    <span :class="[
                      'font-semibold mr-1',
                      alternative.compatibility === 'exact' ? 'text-green-600' :
                      alternative.compatibility === 'similar' ? 'text-yellow-600' :
                      'text-orange-600'
                    ]">
                      {{ getCompatibilityLabel(alternative.compatibility) }}
                    </span>
                  </div>
                  <div>
                    <span class="text-gray-500 font-persian">کیفیت:</span>
                    <span class="font-semibold text-purple-600 mr-1">{{ alternative.quality }}</span>
                  </div>
                </div>

                <div v-if="alternative.notes" class="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600 font-persian text-rtl">
                  {{ alternative.notes }}
                </div>
              </div>

              <div class="flex flex-col gap-2 ml-4">
                <button
                  @click="viewAlternative(alternative)"
                  class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors font-persian"
                >
                  مشاهده
                </button>
                <button
                  v-if="alternative.stock > 0"
                  @click="addAlternativeToCart(alternative)"
                  class="px-3 py-1 border border-green-600 text-green-600 rounded text-sm hover:bg-green-50 transition-colors font-persian"
                >
                  افزودن
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Supersessions Tab -->
    <div v-if="activeTab === 'supersessions'" class="space-y-4">
      <div class="bg-orange-50 border border-orange-200 rounded-lg p-4">
        <div class="flex items-center gap-2 mb-3">
          <svg class="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          <h4 class="text-lg font-semibold text-orange-800 font-persian-bold text-rtl">
            جایگزینی‌ها و به‌روزرسانی‌ها
          </h4>
        </div>
        <p class="text-sm text-orange-700 font-persian text-rtl mb-4">
          تاریخچه تغییرات و نسخه‌های جدید این قطعه.
        </p>

        <div class="space-y-4">
          <div
            v-for="supersession in supersessions"
            :key="supersession.id"
            class="bg-white rounded-lg border border-orange-200 p-4"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <span :class="[
                  'w-3 h-3 rounded-full',
                  supersession.type === 'superseded_by' ? 'bg-green-500' :
                  supersession.type === 'supersedes' ? 'bg-blue-500' :
                  'bg-orange-500'
                ]"></span>
                <span class="font-semibold text-gray-900 font-persian">
                  {{ getSupersessionTypeLabel(supersession.type) }}
                </span>
              </div>
              <span class="text-sm text-gray-500 font-persian">{{ supersession.date }}</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <div>
                  <span class="text-sm text-gray-500 font-persian">شماره قطعه:</span>
                  <span class="font-mono text-lg text-gray-900 mr-2">{{ supersession.partNumber }}</span>
                </div>
                <div>
                  <span class="text-sm text-gray-500 font-persian">برند:</span>
                  <span class="text-gray-900 mr-2 font-persian">{{ supersession.brand }}</span>
                </div>
                <div>
                  <span class="text-sm text-gray-500 font-persian">دلیل تغییر:</span>
                  <span class="text-gray-900 mr-2 font-persian">{{ supersession.reason }}</span>
                </div>
              </div>
              
              <div class="space-y-2">
                <div v-if="supersession.improvements" class="text-sm">
                  <span class="text-gray-500 font-persian">بهبودها:</span>
                  <ul class="text-gray-700 mr-4 font-persian text-rtl">
                    <li v-for="improvement in supersession.improvements" :key="improvement" class="text-xs">
                      • {{ improvement }}
                    </li>
                  </ul>
                </div>
                <div class="flex gap-2 mt-3">
                  <button
                    @click="viewSupersession(supersession)"
                    class="px-3 py-1 bg-orange-600 text-white rounded text-sm hover:bg-orange-700 transition-colors font-persian"
                  >
                    مشاهده جزئیات
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compatibility Matrix Tab -->
    <div v-if="activeTab === 'compatibility'" class="space-y-4">
      <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div class="flex items-center gap-2 mb-3">
          <svg class="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V8zm0 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" clip-rule="evenodd" />
          </svg>
          <h4 class="text-lg font-semibold text-purple-800 font-persian-bold text-rtl">
            ماتریس سازگاری خودرو
          </h4>
        </div>
        <p class="text-sm text-purple-700 font-persian text-rtl mb-4">
          جدول کامل سازگاری این قطعه با مدل‌های مختلف خودرو.
        </p>

        <!-- Vehicle Filter -->
        <div class="flex flex-wrap gap-3 mb-4">
          <select
            v-model="selectedBrand"
            @change="filterCompatibility"
            class="px-3 py-2 border border-purple-300 rounded-lg text-sm font-persian text-rtl bg-white"
          >
            <option value="">همه برندها</option>
            <option v-for="brand in vehicleBrands" :key="brand" :value="brand">
              {{ brand }}
            </option>
          </select>
          
          <select
            v-model="selectedYear"
            @change="filterCompatibility"
            class="px-3 py-2 border border-purple-300 rounded-lg text-sm font-persian text-rtl bg-white"
          >
            <option value="">همه سال‌ها</option>
            <option v-for="year in availableYears" :key="year" :value="year">
              {{ year }}
            </option>
          </select>

          <button
            @click="clearFilters"
            class="px-3 py-2 text-sm text-purple-600 hover:text-purple-700 font-persian"
          >
            پاک کردن فیلتر
          </button>
        </div>

        <!-- Compatibility Table -->
        <div class="overflow-x-auto">
          <table class="w-full border border-purple-200 rounded-lg overflow-hidden">
            <thead class="bg-purple-100">
              <tr>
                <th class="px-4 py-3 text-right text-sm font-semibold text-purple-800 font-persian">برند</th>
                <th class="px-4 py-3 text-right text-sm font-semibold text-purple-800 font-persian">مدل</th>
                <th class="px-4 py-3 text-center text-sm font-semibold text-purple-800 font-persian">سال‌ها</th>
                <th class="px-4 py-3 text-center text-sm font-semibold text-purple-800 font-persian">موتور</th>
                <th class="px-4 py-3 text-center text-sm font-semibold text-purple-800 font-persian">سازگاری</th>
                <th class="px-4 py-3 text-center text-sm font-semibold text-purple-800 font-persian">یادداشت</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="vehicle in filteredCompatibility"
                :key="vehicle.id"
                class="border-t border-purple-200 hover:bg-purple-25"
              >
                <td class="px-4 py-3 text-sm text-gray-900 font-persian">{{ vehicle.brand }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 font-persian">{{ vehicle.model }}</td>
                <td class="px-4 py-3 text-sm text-gray-600 text-center">{{ vehicle.years }}</td>
                <td class="px-4 py-3 text-sm text-gray-600 text-center">{{ vehicle.engine }}</td>
                <td class="px-4 py-3 text-center">
                  <span :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    vehicle.compatibility === 'exact' ? 'bg-green-100 text-green-800' :
                    vehicle.compatibility === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  ]">
                    {{ getCompatibilityLabel(vehicle.compatibility) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 text-center font-persian">
                  {{ vehicle.notes || '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="filteredCompatibility.length === 0" class="text-center py-8 text-gray-500 font-persian">
          هیچ خودرویی با فیلتر انتخابی یافت نشد.
        </div>
      </div>
    </div>

    <!-- Analytics Footer -->
    <div class="mt-6 pt-4 border-t border-gray-200 text-center">
      <p class="text-xs text-gray-500 font-persian">
        💡 اطلاعات بیشتری نیاز دارید؟ 
        <button @click="contactSupport" class="text-blue-600 hover:text-blue-700 underline">
          با کارشناسان ما تماس بگیرید
        </button>
      </p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'CrossReferences',
  props: {
    part: {
      type: Object,
      required: true
    }
  },
  emits: ['view-alternative', 'add-to-cart', 'view-supersession', 'contact-support'],
  setup(props, { emit }) {
    // Tab management
    const activeTab = ref('oem')
    const selectedBrand = ref('')
    const selectedYear = ref('')

    // Tab configuration
    const tabs = ref([
      { key: 'oem', label: 'OEM اصلی', count: 8 },
      { key: 'alternatives', label: 'جایگزین', count: 12 },
      { key: 'supersessions', label: 'نسخه جدید', count: 3 },
      { key: 'compatibility', label: 'سازگاری', count: 45 }
    ])

    // Mock OEM references data
    const oemReferences = ref([
      {
        id: 1,
        brand: 'Toyota',
        partNumber: '04465-42070',
        description: 'لنت ترمز جلو',
        years: '2010-2020',
        status: 'active'
      },
      {
        id: 2,
        brand: 'Lexus',
        partNumber: '04465-42071',
        description: 'لنت ترمز جلو پریمیوم',
        years: '2012-2022',
        status: 'active'
      },
      {
        id: 3,
        brand: 'Aisin',
        partNumber: 'ASN-2142',
        description: 'لنت ترمز OEM',
        years: '2010-2018',
        status: 'superseded'
      },
      {
        id: 4,
        brand: 'Akebono',
        partNumber: 'AK-4465',
        description: 'لنت ترمز سرامیکی',
        years: '2015-2023',
        status: 'active'
      },
      {
        id: 5,
        brand: 'Genuine Toyota',
        partNumber: 'GT-04465-42070',
        description: 'لنت ترمز اصلی تویوتا',
        years: '2010-2020',
        status: 'active'
      },
      {
        id: 6,
        brand: 'TRW',
        partNumber: 'GDB3234',
        description: 'لنت ترمز TRW',
        years: '2010-2019',
        status: 'discontinued'
      },
      {
        id: 7,
        brand: 'Brembo',
        partNumber: 'P83077',
        description: 'لنت ترمز برمبو',
        years: '2012-2021',
        status: 'active'
      },
      {
        id: 8,
        brand: 'Bendix',
        partNumber: 'DB1465',
        description: 'لنت ترمز بندیکس',
        years: '2010-2020',
        status: 'active'
      }
    ])

    // Mock alternatives data
    const alternatives = ref([
      {
        id: 1,
        name: 'لنت ترمز سرامیکی پریمیوم',
        brand: 'Akebono',
        sku: 'AK-PREM-4465',
        price: 850000,
        stock: 15,
        compatibility: 'exact',
        quality: 'پریمیوم',
        image: 'https://via.placeholder.com/48x48/4CAF50/FFFFFF?text=AK',
        notes: 'عملکرد بهتر در شرایط سخت، عمر بیشتر'
      },
      {
        id: 2,
        name: 'لنت ترمز اقتصادی',
        brand: 'Sangsin',
        sku: 'SG-ECO-4465',
        price: 420000,
        stock: 8,
        compatibility: 'similar',
        quality: 'استاندارد',
        image: 'https://via.placeholder.com/48x48/2196F3/FFFFFF?text=SG',
        notes: 'گزینه اقتصادی با کیفیت مناسب'
      },
      {
        id: 3,
        name: 'لنت ترمز کربن سرامیک',
        brand: 'Brembo',
        sku: 'BR-CARBON-83077',
        price: 1250000,
        stock: 3,
        compatibility: 'exact',
        quality: 'بالا',
        image: 'https://via.placeholder.com/48x48/FF5722/FFFFFF?text=BR',
        notes: 'برای رانندگی ورزشی، کم‌نویز'
      },
      {
        id: 4,
        name: 'لنت ترمز ارگانیک',
        brand: 'Textar',
        sku: 'TX-ORG-2465',
        price: 680000,
        stock: 12,
        compatibility: 'similar',
        quality: 'خوب',
        image: 'https://via.placeholder.com/48x48/9C27B0/FFFFFF?text=TX',
        notes: 'دوستدار محیط زیست، نرم'
      }
    ])

    // Mock supersessions data
    const supersessions = ref([
      {
        id: 1,
        type: 'superseded_by',
        partNumber: '04465-42075',
        brand: 'Toyota',
        date: '1402/08/15',
        reason: 'بهبود فرمولاسیون',
        improvements: [
          'کاهش صدا و لرزش',
          'افزایش عمر مفید',
          'بهبود عملکرد در دماهای بالا'
        ]
      },
      {
        id: 2,
        type: 'supersedes',
        partNumber: '04465-42065',
        brand: 'Toyota',
        date: '1400/03/10',
        reason: 'نسخه قدیمی',
        improvements: [
          'فرمولاسیون جدید',
          'سازگاری بهتر'
        ]
      },
      {
        id: 3,
        type: 'related',
        partNumber: '04465-42080',
        brand: 'Lexus',
        date: '1402/12/01',
        reason: 'نسخه لوکس',
        improvements: [
          'پوشش ضد خوردگی',
          'بسته‌بندی پریمیوم',
          'گارانتی طولانی‌تر'
        ]
      }
    ])

    // Mock compatibility matrix data
    const compatibilityMatrix = ref([
      {
        id: 1,
        brand: 'تویوتا',
        model: 'کمری',
        years: '2010-2020',
        engine: '2.4L',
        compatibility: 'exact',
        notes: 'مناسب تمام تریم‌ها'
      },
      {
        id: 2,
        brand: 'تویوتا',
        model: 'کرولا',
        years: '2015-2023',
        engine: '1.8L',
        compatibility: 'exact',
        notes: null
      },
      {
        id: 3,
        brand: 'لکسوس',
        model: 'ES350',
        years: '2012-2021',
        engine: '3.5L V6',
        compatibility: 'exact',
        notes: 'فقط مدل‌های امریکایی'
      },
      {
        id: 4,
        brand: 'تویوتا',
        model: 'پریوس',
        years: '2016-2022',
        engine: 'Hybrid 1.8L',
        compatibility: 'partial',
        notes: 'نیاز به بررسی VIN'
      },
      {
        id: 5,
        brand: 'تویوتا',
        model: 'یاریس',
        years: '2018-2023',
        engine: '1.5L',
        compatibility: 'none',
        notes: 'اندازه متفاوت'
      }
    ])

    // Computed properties
    const vehicleBrands = computed(() => {
      return [...new Set(compatibilityMatrix.value.map(v => v.brand))].sort()
    })

    const availableYears = computed(() => {
      const allYears = compatibilityMatrix.value.flatMap(v => {
        const [start, end] = v.years.split('-').map(y => parseInt(y))
        const years = []
        for (let year = start; year <= end; year++) {
          years.push(year.toString())
        }
        return years
      })
      return [...new Set(allYears)].sort((a, b) => b - a)
    })

    const filteredCompatibility = computed(() => {
      let filtered = compatibilityMatrix.value

      if (selectedBrand.value) {
        filtered = filtered.filter(v => v.brand === selectedBrand.value)
      }

      if (selectedYear.value) {
        filtered = filtered.filter(v => {
          const [start, end] = v.years.split('-').map(y => parseInt(y))
          const year = parseInt(selectedYear.value)
          return year >= start && year <= end
        })
      }

      return filtered
    })

    // Methods
    const formatPrice = (price) => {
      if (!price) return '0'
      return new Intl.NumberFormat('fa-IR').format(price)
    }

    const getStatusLabel = (status) => {
      const labels = {
        active: 'فعال',
        superseded: 'جایگزین شده',
        discontinued: 'توقف تولید'
      }
      return labels[status] || status
    }

    const getCompatibilityLabel = (compatibility) => {
      const labels = {
        exact: 'کامل',
        similar: 'مشابه',
        partial: 'جزئی',
        none: 'نامناسب'
      }
      return labels[compatibility] || compatibility
    }

    const getSupersessionTypeLabel = (type) => {
      const labels = {
        superseded_by: 'جایگزین شده با',
        supersedes: 'جایگزین',
        related: 'مرتبط'
      }
      return labels[type] || type
    }

    const copyPartNumber = async (partNumber) => {
      try {
        await navigator.clipboard.writeText(partNumber)
        console.log('Part number copied:', partNumber)
        // Show toast notification here
      } catch (error) {
        console.error('Failed to copy:', error)
      }
    }

    const viewAlternative = (alternative) => {
      console.log('view_cross_reference event:', {
        sku: props.part.oemCode,
        alternativeId: alternative.id,
        alternativeSku: alternative.sku,
        type: 'alternative'
      })
      
      emit('view-alternative', alternative)
    }

    const addAlternativeToCart = (alternative) => {
      console.log('add_alternative_to_cart event:', {
        originalSku: props.part.oemCode,
        alternativeId: alternative.id,
        alternativeSku: alternative.sku,
        price: alternative.price
      })
      
      emit('add-to-cart', {
        part: alternative,
        quantity: 1,
        type: 'alternative'
      })
    }

    const viewSupersession = (supersession) => {
      console.log('view_supersession event:', {
        sku: props.part.oemCode,
        supersessionId: supersession.id,
        supersessionPartNumber: supersession.partNumber,
        type: supersession.type
      })
      
      emit('view-supersession', supersession)
    }

    const filterCompatibility = () => {
      console.log('compatibility_filter event:', {
        sku: props.part.oemCode,
        brand: selectedBrand.value,
        year: selectedYear.value,
        resultCount: filteredCompatibility.value.length
      })
    }

    const clearFilters = () => {
      selectedBrand.value = ''
      selectedYear.value = ''
      console.log('compatibility_filter_clear event:', {
        sku: props.part.oemCode
      })
    }

    const contactSupport = () => {
      console.log('contact_support event:', {
        sku: props.part.oemCode,
        reason: 'cross_reference_help'
      })
      
      emit('contact-support', {
        part: props.part,
        reason: 'cross_reference_help'
      })
    }

    // Track tab views
    const trackTabView = (tab) => {
      console.log('cross_reference_tab_view event:', {
        sku: props.part.oemCode,
        tab,
        timestamp: new Date().toISOString()
      })
    }

    // Initialize
    onMounted(() => {
      trackTabView(activeTab.value)
    })

    // Watch tab changes
    const changeTab = (tab) => {
      activeTab.value = tab
      trackTabView(tab)
    }

    return {
      // Reactive data
      activeTab,
      selectedBrand,
      selectedYear,
      tabs,
      oemReferences,
      alternatives,
      supersessions,
      compatibilityMatrix,
      
      // Computed
      vehicleBrands,
      availableYears,
      filteredCompatibility,
      
      // Methods
      formatPrice,
      getStatusLabel,
      getCompatibilityLabel,
      getSupersessionTypeLabel,
      copyPartNumber,
      viewAlternative,
      addAlternativeToCart,
      viewSupersession,
      filterCompatibility,
      clearFilters,
      contactSupport,
      changeTab
    }
  }
}
</script>
