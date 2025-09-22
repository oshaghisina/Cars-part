<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
          <p class="text-gray-600 mt-2">
            Manage application settings and preferences
          </p>
        </div>
      </div>
    </div>

    <!-- Settings Content -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="space-y-6">
        <!-- AI Search Settings -->
        <div class="border-b border-gray-200 pb-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            AI Search Settings
          </h3>
          <div class="flex items-center justify-between">
            <div>
              <label class="text-sm font-medium text-gray-700"
                >Enable AI Search</label
              >
              <p class="text-sm text-gray-500">
                Use AI-powered semantic search for better results
              </p>
            </div>
            <div class="flex items-center">
              <input
                v-model="aiEnabled"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                @change="updateAISettings"
              />
            </div>
          </div>
        </div>

        <!-- Bulk Search Settings -->
        <div class="border-b border-gray-200 pb-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            Bulk Search Settings
          </h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Maximum Bulk Search Items</label
              >
              <input
                v-model.number="bulkLimit"
                type="number"
                min="1"
                max="50"
                class="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                @change="updateBulkSettings"
              />
              <p class="text-sm text-gray-500 mt-1">
                Maximum number of items that can be searched in bulk
              </p>
            </div>
          </div>
        </div>

        <!-- Telegram Bot Settings -->
        <div class="border-b border-gray-200 pb-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            Telegram Bot Settings
          </h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Admin Telegram IDs</label
              >
              <textarea
                v-model="adminIds"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter Telegram IDs separated by commas (e.g., 123456789, 987654321)"
                @change="updateAdminSettings"
              ></textarea>
              <p class="text-sm text-gray-500 mt-1">
                Telegram user IDs that have admin access to the bot
              </p>
            </div>
          </div>
        </div>

        <!-- System Information -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            System Information
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="font-medium text-gray-900">Database</h4>
              <p class="text-sm text-gray-600">SQLite (Development)</p>
              <p class="text-sm text-gray-500">PostgreSQL (Production Ready)</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="font-medium text-gray-900">API Status</h4>
              <p class="text-sm text-green-600">✅ Online</p>
              <p class="text-sm text-gray-500">Running on localhost:8001</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="font-medium text-gray-900">Bot Status</h4>
              <p class="text-sm text-green-600">✅ Active</p>
              <p class="text-sm text-gray-500">@ChinaCarPartBot</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="font-medium text-gray-900">Frontend</h4>
              <p class="text-sm text-green-600">✅ Running</p>
              <p class="text-sm text-gray-500">localhost:5173</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";

export default {
  name: "Settings",
  setup() {
    const _authStore = useAuthStore();
    const aiEnabled = ref(true);
    const bulkLimit = ref(20);
    const adminIds = ref("");

    // Load current settings
    const loadSettings = async () => {
      try {
        // Load from API
        const response = await fetch("/api/v1/admin/settings", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          const settings = data.settings;

          // Update local state with API settings
          aiEnabled.value = settings.AI_ENABLED === "true";
          bulkLimit.value = parseInt(settings.BULK_LIMIT_DEFAULT) || 10;
          // Add more settings as needed
        }
      } catch (error) {
        console.error("Error loading settings:", error);
      }
    };

    // Update AI settings
    const updateAISettings = async () => {
      try {
        // Update via API
        const response = await fetch("/api/v1/admin/settings", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            AI_ENABLED: aiEnabled.value.toString(),
          }),
        });

        if (response.ok) {
          console.log("AI Settings updated:", aiEnabled.value);
        } else {
          throw new Error("Failed to update AI settings");
        }
      } catch (error) {
        console.error("Error updating AI settings:", error);
      }
    };

    // Update bulk search settings
    const updateBulkSettings = async () => {
      try {
        // Update via API
        const response = await fetch("/api/v1/admin/settings", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            BULK_LIMIT_DEFAULT: bulkLimit.value.toString(),
          }),
        });

        if (response.ok) {
          console.log("Bulk Settings updated:", bulkLimit.value);
        } else {
          throw new Error("Failed to update bulk settings");
        }
      } catch (error) {
        console.error("Error updating bulk settings:", error);
      }
    };

    // Update admin settings
    const updateAdminSettings = async () => {
      try {
        // Update via API
        const response = await fetch("/api/v1/admin/settings", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            ADMIN_USER_IDS: adminIds.value,
          }),
        });

        if (response.ok) {
          console.log("Admin Settings updated:", adminIds.value);
        } else {
          throw new Error("Failed to update admin settings");
        }
      } catch (error) {
        console.error("Error updating admin settings:", error);
      }
    };

    onMounted(() => {
      loadSettings();
    });

    return {
      aiEnabled,
      bulkLimit,
      adminIds,
      updateAISettings,
      updateBulkSettings,
      updateAdminSettings,
    };
  },
};
</script>
