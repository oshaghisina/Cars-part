<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">اتصال حساب تلگرام</h3>
      <div class="flex items-center space-x-2 space-x-reverse">
        <div
          :class="[
            'w-3 h-3 rounded-full',
            isLinked ? 'bg-green-500' : 'bg-gray-400',
          ]"
        ></div>
        <span class="text-sm text-gray-600">
          {{ isLinked ? "متصل" : "غیر متصل" }}
        </span>
      </div>
    </div>

    <!-- Linked Account Info -->
    <div
      v-if="isLinked && telegramUser"
      class="mb-6 p-4 bg-green-50 rounded-lg"
    >
      <div class="flex items-center space-x-3 space-x-reverse">
        <div
          class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center"
        >
          <svg
            class="w-5 h-5 text-green-600"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.568 8.16l-1.61 7.59c-.12.54-.44.68-.89.42l-2.46-1.81-1.19 1.15c-.13.13-.24.24-.49.24l.18-2.55 4.57-4.13c.2-.18-.04-.28-.31-.1l-5.64 3.55-2.43-.76c-.53-.16-.54-.53.11-.79l9.57-3.69c.44-.16.83.1.69.79z"
            />
          </svg>
        </div>
        <div>
          <p class="font-medium text-gray-900">
            {{ telegramUser.first_name }} {{ telegramUser.last_name }}
          </p>
          <p class="text-sm text-gray-600">@{{ telegramUser.username }}</p>
          <p class="text-xs text-gray-500">
            ID: {{ telegramUser.telegram_id }}
          </p>
        </div>
      </div>
    </div>

    <!-- Link Account Section -->
    <div v-if="!isLinked" class="mb-6">
      <div class="mb-4">
        <label
          for="telegram-id"
          class="block text-sm font-medium text-gray-700 mb-2"
        >
          شناسه تلگرام شما
        </label>
        <input
          id="telegram-id"
          v-model="telegramId"
          type="number"
          placeholder="مثال: 176007160"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <p class="mt-1 text-xs text-gray-500">
          برای پیدا کردن شناسه تلگرام خود، به ربات @userinfobot پیام دهید
        </p>
      </div>

      <button
        :disabled="loading || !telegramId"
        class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        @click="linkAccount"
      >
        <div
          v-if="loading"
          class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"
        ></div>
        <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path
            d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.568 8.16l-1.61 7.59c-.12.54-.44.68-.89.42l-2.46-1.81-1.19 1.15c-.13.13-.24.24-.49.24l.18-2.55 4.57-4.13c.2-.18-.04-.28-.31-.1l-5.64 3.55-2.43-.76c-.53-.16-.54-.53.11-.79l9.57-3.69c.44-.16.83.1.69.79z"
          />
        </svg>
        {{ loading ? "در حال اتصال..." : "اتصال حساب تلگرام" }}
      </button>
    </div>

    <!-- Unlink Button -->
    <div v-if="isLinked" class="mb-6">
      <button
        :disabled="loading"
        class="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        @click="unlinkAccount"
      >
        <div
          v-if="loading"
          class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"
        ></div>
        <svg
          v-else
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
        {{ loading ? "در حال قطع اتصال..." : "قطع اتصال حساب تلگرام" }}
      </button>
    </div>

    <!-- Instructions -->
    <div class="bg-blue-50 rounded-lg p-4">
      <h4 class="font-medium text-blue-900 mb-2">راهنمای اتصال:</h4>
      <ol class="text-sm text-blue-800 space-y-1 list-decimal list-inside">
        <li>شناسه تلگرام خود را در فیلد بالا وارد کنید</li>
        <li>روی دکمه "اتصال حساب تلگرام" کلیک کنید</li>
        <li>در تلگرام روی دکمه تأیید کلیک کنید</li>
        <li>حساب شما با موفقیت متصل خواهد شد</li>
      </ol>
    </div>

    <!-- Error Message -->
    <div
      v-if="error"
      class="mt-4 bg-red-50 border border-red-200 rounded-md p-3"
    >
      <p class="text-sm text-red-600">{{ error }}</p>
    </div>

    <!-- Success Message -->
    <div
      v-if="successMessage"
      class="mt-4 bg-green-50 border border-green-200 rounded-md p-3"
    >
      <p class="text-sm text-green-600">{{ successMessage }}</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth.js";

export default {
  name: "TelegramAccountLinking",
  setup() {
    const authStore = useAuthStore();

    const telegramId = ref("");
    const loading = ref(false);
    const error = ref("");
    const successMessage = ref("");

    const isLinked = computed(() => {
      return authStore.user?.telegram_user != null;
    });

    const telegramUser = computed(() => {
      return authStore.user?.telegram_user;
    });

    const linkAccount = async () => {
      if (!telegramId.value) {
        error.value = "لطفاً شناسه تلگرام خود را وارد کنید";
        return;
      }

      loading.value = true;
      error.value = "";
      successMessage.value = "";

      try {
        const result = await authStore.linkTelegramAccount(
          parseInt(telegramId.value),
        );

        if (result.success) {
          successMessage.value =
            "لینک اتصال ارسال شد. لطفاً در تلگرام تأیید کنید.";
          telegramId.value = "";
        } else {
          error.value = result.message || "خطا در اتصال حساب تلگرام";
        }
      } catch (err) {
        console.error("Link account error:", err);
        error.value = "خطا در اتصال حساب تلگرام";
      } finally {
        loading.value = false;
      }
    };

    const unlinkAccount = async () => {
      loading.value = true;
      error.value = "";
      successMessage.value = "";

      try {
        const result = await authStore.unlinkTelegramAccount();

        if (result.success) {
          successMessage.value = "حساب تلگرام با موفقیت قطع شد";
        } else {
          error.value = result.message || "خطا در قطع اتصال حساب تلگرام";
        }
      } catch (err) {
        console.error("Unlink account error:", err);
        error.value = "خطا در قطع اتصال حساب تلگرام";
      } finally {
        loading.value = false;
      }
    };

    // Check for pending verification on mount
    onMounted(() => {
      const linkToken = localStorage.getItem("telegram_link_token");
      if (linkToken) {
        verifyPendingLink(linkToken);
      }
    });

    const verifyPendingLink = async (token) => {
      loading.value = true;
      error.value = "";
      successMessage.value = "";

      try {
        const result = await authStore.verifyTelegramLink(token);

        if (result.success) {
          successMessage.value = "حساب تلگرام با موفقیت متصل شد";
        } else {
          error.value = result.message || "خطا در تأیید اتصال";
        }
      } catch (err) {
        console.error("Verify link error:", err);
        error.value = "خطا در تأیید اتصال";
      } finally {
        loading.value = false;
      }
    };

    return {
      telegramId,
      loading,
      error,
      successMessage,
      isLinked,
      telegramUser,
      linkAccount,
      unlinkAccount,
    };
  },
};
</script>
