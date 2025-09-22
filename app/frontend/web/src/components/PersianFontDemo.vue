<template>
  <div class="max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-lg">
    <h1 class="text-3xl font-bold text-gray-800 mb-8 font-persian-bold font-persian font-persian" class="font-persian-bold text-rtl">
      نمایش فونت‌های فارسی
    </h1>
    
    <div class="space-y-6">
      <!-- Persian Text Examples -->
      <div class="border-b pb-6">
        <h2 class="text-xl font-semibold text-gray-700 mb-4 font-persian font-persian font-persian" class="font-persian-bold text-rtl">
          نمونه متن‌های فارسی
        </h2>
        <div class="space-y-3">
          <p class="text-lg font-persian text-rtl font-persian font-persian" class="font-persian text-rtl">
            این یک متن نمونه فارسی است که با فونت وزیرمتن نمایش داده می‌شود.
          </p>
          <p class="text-base font-persian text-rtl font-persian font-persian" class="font-persian text-rtl">
            فونت وزیرمتن یکی از بهترین فونت‌های فارسی است که برای وب طراحی شده است.
          </p>
          <p class="text-sm font-persian text-rtl text-gray-600 font-persian font-persian" class="font-persian text-rtl">
            این فونت از Google Fonts بارگذاری می‌شود و کاملاً بهینه است.
          </p>
        </div>
      </div>
      
      <!-- Mixed Language Example -->
      <div class="border-b pb-6">
        <h2 class="text-xl font-semibold text-gray-700 mb-4 font-persian font-persian font-persian" class="font-persian-bold text-rtl">
          متن ترکیبی فارسی و انگلیسی
        </h2>
        <div class="space-y-3">
          <p class="font-persian text-rtl font-persian font-persian" class="font-persian text-rtl">
            خوش آمدید به <span class="font-bold font-persian">China Car Parts</span> - بهترین منبع قطعات خودرو
          </p>
          <p class="font-persian text-rtl font-persian font-persian" class="font-persian text-rtl">
            <span class="text-blue-600 font-bold font-persian font-persian">Customer Portal</span> و <span class="text-green-600 font-bold font-persian font-persian">Admin Panel</span> با پشتیبانی کامل از زبان فارسی
          </p>
        </div>
      </div>
      
      <!-- Font Weight Examples -->
      <div class="border-b pb-6">
        <h2 class="text-xl font-semibold text-gray-700 mb-4 font-persian font-persian font-persian" class="font-persian-bold text-rtl">
          نمونه وزن‌های مختلف فونت
        </h2>
        <div class="space-y-2">
          <p class="font-persian text-rtl font-persian font-persian" style="font-weight: 100;" class="font-persian text-rtl">وزن 100 - بسیار نازک</p>
          <p class="font-persian text-rtl font-persian font-persian" style="font-weight: 300;" class="font-persian text-rtl">وزن 300 - نازک</p>
          <p class="font-persian text-rtl font-persian font-persian" style="font-weight: 400;" class="font-persian text-rtl">وزن 400 - معمولی</p>
          <p class="font-persian text-rtl font-persian font-persian" style="font-weight: 500;" class="font-persian text-rtl">وزن 500 - متوسط</p>
          <p class="font-persian text-rtl font-persian font-persian" style="font-weight: 600;" class="font-persian text-rtl">وزن 600 - نیمه ضخیم</p>
          <p class="font-persian text-rtl font-persian font-persian" style="font-weight: 700;" class="font-persian text-rtl">وزن 700 - ضخیم</p>
          <p class="font-persian text-rtl font-persian font-persian" style="font-weight: 800;" class="font-persian text-rtl">وزن 800 - بسیار ضخیم</p>
          <p class="font-persian text-rtl font-persian font-persian" style="font-weight: 900;" class="font-persian text-rtl">وزن 900 - فوق‌العاده ضخیم</p>
        </div>
      </div>
      
      <!-- Usage Instructions -->
      <div>
        <h2 class="text-xl font-semibold text-gray-700 mb-4 font-persian font-persian font-persian" class="font-persian-bold text-rtl">
          نحوه استفاده
        </h2>
        <div class="bg-gray-100 p-4 rounded-lg">
          <h3 class="font-persian-bold text-rtl mb-2 font-persian font-persian" class="font-persian-bold text-rtl">کلاس‌های CSS:</h3>
          <ul class="space-y-1 text-sm font-mono font-persian font-persian">
            <li><code>.font-persian</code> - فونت فارسی</li>
            <li><code>.font-persian-bold</code> - فونت فارسی ضخیم</li>
            <li><code>.text-rtl</code> - راست به چپ</li>
            <li><code>.text-ltr</code> - چپ به راست</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PersianFontDemo',
  mounted() {
    console.log('Persian Font Demo loaded successfully!');
  }
}
</script>

<style scoped>
/* Additional Persian-specific styles can be added here */
</style>
