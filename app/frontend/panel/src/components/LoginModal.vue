<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
  >
    <div class="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
      <div class="text-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900">Admin Login</h2>
        <p class="text-gray-600 mt-2">
          Enter your credentials to access the admin panel
        </p>
      </div>

      <form class="space-y-4" @submit.prevent="handleLogin">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700"
            >Username</label
          >
          <input
            id="username"
            ref="usernameInput"
            v-model="credentials.username_or_email"
            type="text"
            required
            autocomplete="username"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter username"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700"
            >Password</label
          >
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            required
            autocomplete="current-password"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter password"
          />
        </div>

        <div
          v-if="error"
          class="bg-red-50 border border-red-200 rounded-md p-3"
        >
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <div v-if="loading" class="text-center">
          <div
            class="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-blue-500 hover:bg-blue-400 transition ease-in-out duration-150 cursor-not-allowed"
          >
            <svg
              class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Logging in...
          </div>
        </div>

        <div v-else class="space-y-3">
          <button
            type="submit"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Sign In
          </button>
        </div>
      </form>

      <div class="mt-6 text-center text-sm text-gray-500">
        <p>Default credentials:</p>
        <p><strong>Username:</strong> admin</p>
        <p><strong>Password:</strong> P5DU%wRLzcbP</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from "vue";
import { useAuthStore } from "../stores/auth";

export default {
  name: "LoginModal",
  props: {
    show: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["close"],
  setup(props, { emit }) {
    const authStore = useAuthStore();
    const credentials = ref({
      username_or_email: "",
      password: "",
    });
    const error = ref("");
    const loading = ref(false);
    const usernameInput = ref(null);

    const handleLogin = async () => {
      loading.value = true;
      error.value = "";

      try {
        const result = await authStore.login(credentials.value);

        if (result.success) {
          emit("close");
        } else {
          error.value = result.message;
        }
      } catch (err) {
        error.value = "Login failed. Please try again.";
        console.error("Login error:", err);
      } finally {
        loading.value = false;
      }
    };

    // Auto-focus username input when modal opens
    onMounted(() => {
      if (props.show) {
        nextTick(() => {
          usernameInput.value?.focus();
        });
      }
    });

    return {
      credentials,
      error,
      loading,
      usernameInput,
      handleLogin,
    };
  },
};
</script>
