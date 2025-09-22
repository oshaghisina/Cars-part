<template>
  <div class="iran-delivery-map">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <!-- Content Section -->
        <div class="space-y-8">
          <div class="space-y-4">
            <h2 class="text-sm font-semibold text-orange-500 uppercase tracking-wide font-persian text-rtl">
              مناطق تحت پوشش
            </h2>
            <h3 class="text-4xl font-bold text-white font-persian-bold text-rtl">
              ارسال به سراسر ایران
            </h3>
            <p class="text-xl text-gray-300 font-persian text-rtl leading-relaxed">
              با شبکه گسترده توزیع خود، قطعات خودرو را به تمام نقاط کشور ارسال می‌کنیم
            </p>
          </div>
          
          <!-- Regions List -->
          <div class="space-y-4">
            <div 
              v-for="region in regions" 
              :key="region.id"
              class="flex items-center space-x-4 space-x-reverse group cursor-pointer hover:bg-gray-800/50 p-3 rounded-lg transition-all duration-300"
            >
              <div 
                :class="region.colorClass"
                class="w-4 h-4 rounded-full flex-shrink-0"
              ></div>
              <span class="text-white font-medium font-persian text-rtl group-hover:text-orange-400 transition-colors">
                {{ region.name }}
              </span>
              <svg class="w-5 h-5 text-gray-400 group-hover:text-orange-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </div>
        </div>
        
        <!-- Map Section -->
        <div class="relative">
          <div class="bg-gray-900 rounded-2xl p-8 shadow-2xl">
            <!-- Iran Map SVG -->
            <svg 
              viewBox="0 0 800 600" 
              class="w-full h-auto max-h-96"
              xmlns="http://www.w3.org/2000/svg"
            >
              <!-- Iran Map Paths -->
              <g>
                <!-- Tehran Province -->
                <path 
                  d="M400 200 L420 190 L440 200 L430 220 L410 230 L390 220 Z" 
                  :class="getRegionColor('tehran')"
                  class="transition-all duration-300 hover:opacity-80 cursor-pointer"
                  @click="selectRegion('tehran')"
                />
                
                <!-- Isfahan Province -->
                <path 
                  d="M350 280 L380 270 L400 280 L390 300 L370 310 L350 300 Z" 
                  :class="getRegionColor('isfahan')"
                  class="transition-all duration-300 hover:opacity-80 cursor-pointer"
                  @click="selectRegion('isfahan')"
                />
                
                <!-- Fars Province -->
                <path 
                  d="M300 350 L330 340 L350 350 L340 370 L320 380 L300 370 Z" 
                  :class="getRegionColor('fars')"
                  class="transition-all duration-300 hover:opacity-80 cursor-pointer"
                  @click="selectRegion('fars')"
                />
                
                <!-- Khorasan Province -->
                <path 
                  d="M500 250 L530 240 L550 250 L540 270 L520 280 L500 270 Z" 
                  :class="getRegionColor('khorasan')"
                  class="transition-all duration-300 hover:opacity-80 cursor-pointer"
                  @click="selectRegion('khorasan')"
                />
                
                <!-- Gilan Province -->
                <path 
                  d="M350 150 L380 140 L400 150 L390 170 L370 180 L350 170 Z" 
                  :class="getRegionColor('gilan')"
                  class="transition-all duration-300 hover:opacity-80 cursor-pointer"
                  @click="selectRegion('gilan')"
                />
                
                <!-- Kerman Province -->
                <path 
                  d="M250 400 L280 390 L300 400 L290 420 L270 430 L250 420 Z" 
                  :class="getRegionColor('kerman')"
                  class="transition-all duration-300 hover:opacity-80 cursor-pointer"
                  @click="selectRegion('kerman')"
                />
                
                <!-- Other Provinces (simplified) -->
                <path 
                  d="M200 200 L230 190 L250 200 L240 220 L220 230 L200 220 Z" 
                  class="fill-gray-700 transition-all duration-300 hover:opacity-80 cursor-pointer"
                />
                <path 
                  d="M600 200 L630 190 L650 200 L640 220 L620 230 L600 220 Z" 
                  class="fill-gray-700 transition-all duration-300 hover:opacity-80 cursor-pointer"
                />
                <path 
                  d="M200 300 L230 290 L250 300 L240 320 L220 330 L200 320 Z" 
                  class="fill-gray-700 transition-all duration-300 hover:opacity-80 cursor-pointer"
                />
                <path 
                  d="M600 300 L630 290 L650 300 L640 320 L620 330 L600 320 Z" 
                  class="fill-gray-700 transition-all duration-300 hover:opacity-80 cursor-pointer"
                />
              </g>
            </svg>
            
            <!-- Map Legend -->
            <div class="mt-6 flex flex-wrap gap-4 justify-center">
              <div class="flex items-center space-x-2 space-x-reverse">
                <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span class="text-sm text-gray-300 font-persian text-rtl">شهرهای اصلی</span>
              </div>
              <div class="flex items-center space-x-2 space-x-reverse">
                <div class="w-3 h-3 bg-gray-700 rounded-full"></div>
                <span class="text-sm text-gray-300 font-persian text-rtl">سایر استان‌ها</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IranDeliveryMap',
  data() {
    return {
      selectedRegion: null,
      regions: [
        {
          id: 1,
          name: 'تهران و استان مرکزی',
          colorClass: 'bg-blue-500',
          regionKey: 'tehran',
          description: 'ارسال سریع به تهران و شهرهای اطراف'
        },
        {
          id: 2,
          name: 'اصفهان و مرکز',
          colorClass: 'bg-blue-600',
          regionKey: 'isfahan',
          description: 'پوشش کامل استان اصفهان و شهرهای مرکزی'
        },
        {
          id: 3,
          name: 'فارس و جنوب',
          colorClass: 'bg-blue-400',
          regionKey: 'fars',
          description: 'ارسال به شیراز و تمام استان‌های جنوبی'
        },
        {
          id: 4,
          name: 'خراسان و شرق',
          colorClass: 'bg-blue-700',
          regionKey: 'khorasan',
          description: 'پوشش مشهد و استان‌های شرقی کشور'
        },
        {
          id: 5,
          name: 'گیلان و شمال',
          colorClass: 'bg-blue-300',
          regionKey: 'gilan',
          description: 'ارسال به رشت و تمام استان‌های شمالی'
        },
        {
          id: 6,
          name: 'کرمان و جنوب شرق',
          colorClass: 'bg-blue-800',
          regionKey: 'kerman',
          description: 'پوشش کرمان و استان‌های جنوب شرقی'
        }
      ]
    }
  },
  methods: {
    selectRegion(regionKey) {
      this.selectedRegion = regionKey
      // You can add more functionality here, like showing region details
      console.log('Selected region:', regionKey)
    },
    
    getRegionColor(regionKey) {
      const region = this.regions.find(r => r.regionKey === regionKey)
      if (region) {
        return region.colorClass
      }
      return 'fill-gray-700'
    }
  }
}
</script>

<style scoped>
.iran-delivery-map {
  @apply bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900;
}

/* Custom hover effects for map regions */
svg path:hover {
  transform: scale(1.05);
  filter: brightness(1.2);
}

/* Smooth transitions */
svg path {
  transition: all 0.3s ease;
}
</style>
