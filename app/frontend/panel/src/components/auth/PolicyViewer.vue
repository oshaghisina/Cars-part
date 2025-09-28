<template>
  <div class="policy-viewer p-6 bg-white rounded-lg shadow-sm">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-900 font-persian text-rtl">
        تنظیمات احراز هویت
      </h2>
      <button
        :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-persian"
        @click="refreshConfig"
      >
        <div
          v-if="loading"
          class="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2"
        ></div>
        {{ loading ? "در حال بارگذاری..." : "بروزرسانی" }}
      </button>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-8">
      <div
        class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
      ></div>
      <span class="ml-2 text-gray-600 font-persian text-rtl"
        >در حال بارگذاری تنظیمات...</span
      >
    </div>

    <div
      v-else-if="error"
      class="bg-red-50 border border-red-200 rounded-md p-4 mb-6"
    >
      <div class="flex">
        <svg
          class="h-5 w-5 text-red-400"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
            clip-rule="evenodd"
          />
        </svg>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800 font-persian text-rtl">
            خطا در بارگذاری تنظیمات
          </h3>
          <p class="mt-1 text-sm text-red-700 font-persian text-rtl">
            {{ error }}
          </p>
        </div>
      </div>
    </div>

    <div v-else class="space-y-6">
      <!-- JWT Configuration -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h3
          class="text-lg font-semibold text-gray-900 mb-4 font-persian text-rtl"
        >
          تنظیمات JWT
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >کتابخانه JWT</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.jwt?.library || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >الگوریتم</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.jwt?.algorithm || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >مدت اعتبار توکن (دقیقه)</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.jwt?.access_token_expire_minutes || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >طول کلید مخفی</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.jwt?.secret_key_length || "نامشخص" }} کاراکتر
            </p>
          </div>
        </div>
      </div>

      <!-- Claims Configuration -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h3
          class="text-lg font-semibold text-gray-900 mb-4 font-persian text-rtl"
        >
          تنظیمات Claims
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >فرمت استاندارد</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.claims?.canonical_format || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >پشتیبانی از فرمت قدیمی</label
            >
            <span
              class="mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="
                config.claims?.legacy_support
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              "
            >
              {{ config.claims?.legacy_support ? "فعال" : "غیرفعال" }}
            </span>
          </div>
        </div>
        <div class="mt-4">
          <label
            class="block text-sm font-medium text-gray-700 font-persian text-rtl"
            >Claims مورد نیاز</label
          >
          <div class="mt-1 flex flex-wrap gap-2">
            <span
              v-for="claim in config.claims?.required_claims || []"
              :key="claim"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              {{ claim }}
            </span>
          </div>
        </div>
      </div>

      <!-- Security Configuration -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h3
          class="text-lg font-semibold text-gray-900 mb-4 font-persian text-rtl"
        >
          تنظیمات امنیتی
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >صادرکننده</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.security?.issuer || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >مخاطب</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.security?.audience || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >اعتبارسنجی توکن</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.security?.token_validation || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >پشتیبانی از توکن قدیمی</label
            >
            <span
              class="mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="
                config.security?.legacy_token_support
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              "
            >
              {{ config.security?.legacy_token_support ? "فعال" : "غیرفعال" }}
            </span>
          </div>
        </div>
      </div>

      <!-- Features Configuration -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h3
          class="text-lg font-semibold text-gray-900 mb-4 font-persian text-rtl"
        >
          ویژگی‌های فعال
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="(enabled, feature) in config.features || {}"
            :key="feature"
            class="flex items-center"
          >
            <span
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="
                enabled
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              "
            >
              {{ enabled ? "فعال" : "غیرفعال" }}
            </span>
            <span class="mr-2 text-sm text-gray-700 font-persian text-rtl">
              {{ getFeatureName(feature) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Storage Configuration -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h3
          class="text-lg font-semibold text-gray-900 mb-4 font-persian text-rtl"
        >
          تنظیمات ذخیره‌سازی
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >کلید Frontend</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.storage?.frontend_key || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >نوع ذخیره‌سازی</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.storage?.storage_type || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >مهاجرت کامل</label
            >
            <span
              class="mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="
                config.storage?.migration_complete
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              "
            >
              {{
                config.storage?.migration_complete
                  ? "تکمیل شده"
                  : "در حال انجام"
              }}
            </span>
          </div>
        </div>
      </div>

      <!-- Rate Limiting Configuration -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h3
          class="text-lg font-semibold text-gray-900 mb-4 font-persian text-rtl"
        >
          محدودیت نرخ
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >درخواست OTP (ساعت)</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.rate_limiting?.otp_requests_per_hour || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >تلاش ورود (15 دقیقه)</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.rate_limiting?.login_attempts_per_15min || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >لینک تلگرام (روز)</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.rate_limiting?.telegram_links_per_day || "نامشخص" }}
            </p>
          </div>
        </div>
      </div>

      <!-- Metadata -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h3
          class="text-lg font-semibold text-gray-900 mb-4 font-persian text-rtl"
        >
          اطلاعات متا
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >نسخه پیکربندی</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ config.metadata?.config_version || "نامشخص" }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >آخرین بروزرسانی</label
            >
            <p class="mt-1 text-sm text-gray-900 font-persian text-rtl">
              {{ formatDate(config.metadata?.last_updated) }}
            </p>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 font-persian text-rtl"
              >محیط</label
            >
            <span
              class="mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="getEnvironmentClass(config.metadata?.environment)"
            >
              {{ config.metadata?.environment || "نامشخص" }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { adminApi } from "@/api/client.js";

export default {
  name: "PolicyViewer",
  setup() {
    const config = ref({});
    const loading = ref(false);
    const error = ref("");

    const loadConfig = async () => {
      loading.value = true;
      error.value = "";
      try {
        config.value = await adminApi.getAuthConfig();
      } catch (err) {
        error.value = err.message || "خطا در بارگذاری تنظیمات";
        console.error("Error loading auth config:", err);
      } finally {
        loading.value = false;
      }
    };

    const refreshConfig = () => {
      loadConfig();
    };

    const getFeatureName = (feature) => {
      const names = {
        telegram_sso: "ورود با تلگرام",
        otp_enabled: "احراز هویت OTP",
        phone_auth: "احراز هویت تلفن",
        account_linking: "اتصال حساب‌ها",
      };
      return names[feature] || feature;
    };

    const getEnvironmentClass = (env) => {
      switch (env) {
        case "production":
          return "bg-red-100 text-red-800";
        case "staging":
          return "bg-yellow-100 text-yellow-800";
        case "development":
          return "bg-green-100 text-green-800";
        default:
          return "bg-gray-100 text-gray-800";
      }
    };

    const formatDate = (dateString) => {
      if (!dateString) return "نامشخص";
      try {
        return new Date(dateString).toLocaleString("fa-IR");
      } catch {
        return dateString;
      }
    };

    onMounted(() => {
      loadConfig();
    });

    return {
      config,
      loading,
      error,
      refreshConfig,
      getFeatureName,
      getEnvironmentClass,
      formatDate,
    };
  },
};
</script>
