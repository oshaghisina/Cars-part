<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
  >
    <div
      class="relative top-4 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white"
    >
      <div class="mt-3">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900">
              Order #{{ order.id.toString().padStart(5, "0") }}
            </h3>
            <p class="text-sm text-gray-500">
              {{ formatDate(order.created_at) }} at
              {{ formatTime(order.created_at) }}
            </p>
          </div>
          <button
            class="text-gray-400 hover:text-gray-600"
            @click="$emit('close')"
          >
            <svg
              class="w-6 h-6"
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
          </button>
        </div>

        <!-- Order Status and Actions -->
        <div class="mb-6 p-4 bg-gray-50 rounded-lg">
          <div class="flex justify-between items-center">
            <div class="flex items-center space-x-4">
              <span class="text-sm font-medium text-gray-700">Status:</span>
              <span
                :class="[
                  getStatusBadgeClass(order.status),
                  'inline-flex px-3 py-1 text-sm font-semibold rounded-full',
                ]"
              >
                {{ getStatusText(order.status) }}
              </span>
            </div>
            <div class="flex space-x-2">
              <button
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                @click="updateStatus"
              >
                Update Status
              </button>
              <button
                class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                @click="addItem"
              >
                Add Item
              </button>
            </div>
          </div>
        </div>

        <!-- Customer Information -->
        <div class="mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">
            Customer Information
          </h4>
          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div v-if="customer" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700"
                  >Name</label
                >
                <p class="mt-1 text-sm text-gray-900">
                  {{ customer.first_name }} {{ customer.last_name }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700"
                  >Phone</label
                >
                <p class="mt-1 text-sm text-gray-900">
                  {{ customer.phone_e164 }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700"
                  >Telegram ID</label
                >
                <p class="mt-1 text-sm text-gray-900">
                  {{ customer.telegram_user_id }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700"
                  >City</label
                >
                <p class="mt-1 text-sm text-gray-900">
                  {{ customer.city || "Not specified" }}
                </p>
              </div>
            </div>
            <div v-else class="text-center py-4">
              <p class="text-gray-500">Customer information not available</p>
            </div>
          </div>
        </div>

        <!-- Order Items -->
        <div class="mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">Order Items</h4>
          <div
            class="bg-white border border-gray-200 rounded-lg overflow-hidden"
          >
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Line
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Query
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Part
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Qty
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Unit
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Notes
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-if="order.items.length === 0">
                  <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    No items in this order
                  </td>
                </tr>
                <tr v-for="item in order.items" v-else :key="item.line_no">
                  <td
                    class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
                  >
                    {{ item.line_no }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900">
                    <div class="max-w-xs truncate" :title="item.query_text">
                      {{ item.query_text }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div v-if="item.matched_part_id">
                      Part #{{ item.matched_part_id }}
                    </div>
                    <div v-else class="text-gray-400">Not matched</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ item.qty }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ item.unit }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900">
                    <div class="max-w-xs truncate" :title="item.notes">
                      {{ item.notes || "-" }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex space-x-2">
                      <button
                        class="text-indigo-600 hover:text-indigo-900"
                        @click="editItem(item)"
                      >
                        Edit
                      </button>
                      <button
                        class="text-red-600 hover:text-red-900"
                        @click="removeItem(item.line_no)"
                      >
                        Remove
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Order Notes -->
        <div class="mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">Order Notes</h4>
          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div v-if="order.notes" class="text-sm text-gray-900">
              {{ order.notes }}
            </div>
            <div v-else class="text-gray-500 italic">
              No notes for this order
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">Order Summary</h4>
          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700"
                  >Total Items</label
                >
                <p class="mt-1 text-lg font-semibold text-gray-900">
                  {{ order.items.length }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700"
                  >Total Quantity</label
                >
                <p class="mt-1 text-lg font-semibold text-gray-900">
                  {{ getTotalQuantity(order.items) }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700"
                  >Estimated Value</label
                >
                <p class="mt-1 text-lg font-semibold text-gray-900">
                  ${{ formatCurrency(calculateOrderValue(order)) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-4 rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg
                class="h-5 w-5 text-red-400"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error</h3>
              <div class="mt-2 text-sm text-red-700">{{ error }}</div>
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            @click="$emit('close')"
          >
            Close
          </button>
          <button
            type="button"
            :disabled="loading"
            class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            @click="saveOrder"
          >
            <svg
              v-if="loading"
              class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
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
            {{ loading ? "Saving..." : "Save Changes" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useOrdersStore } from "../../stores/orders";

export default {
  name: "OrderDetailModal",
  props: {
    order: {
      type: Object,
      required: true,
    },
  },
  emits: ["close", "updated", "updateStatus", "addItem", "editItem"],
  setup(props, { emit }) {
    const ordersStore = useOrdersStore();

    const loading = ref(false);
    const error = ref(null);
    const customer = ref(null);

    const getTotalQuantity = (items) => {
      return items.reduce((total, item) => total + (item.qty || 0), 0);
    };

    const calculateOrderValue = (order) => {
      return ordersStore.calculateOrderValue(order);
    };

    const getStatusBadgeClass = (status) => {
      const color = ordersStore.getStatusColor(status);
      const classes = {
        yellow: "bg-yellow-100 text-yellow-800",
        blue: "bg-blue-100 text-blue-800",
        purple: "bg-purple-100 text-purple-800",
        green: "bg-green-100 text-green-800",
        red: "bg-red-100 text-red-800",
        gray: "bg-gray-100 text-gray-800",
      };
      return classes[color] || classes.gray;
    };

    const getStatusText = (status) => {
      return ordersStore.getStatusText(status);
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString();
    };

    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    const formatCurrency = (amount) => {
      return parseFloat(amount || 0).toFixed(2);
    };

    const updateStatus = () => {
      // Emit event to show status update modal
      emit("updateStatus", props.order);
    };

    const addItem = () => {
      // Emit event to show add item modal
      emit("addItem", props.order);
    };

    const editItem = (item) => {
      // Emit event to show edit item modal
      emit("editItem", props.order, item);
    };

    const removeItem = async (lineNo) => {
      if (confirm("Are you sure you want to remove this item?")) {
        loading.value = true;
        error.value = null;
        try {
          await ordersStore.removeOrderItem(props.order.id, lineNo);
          emit("updated");
        } catch (err) {
          error.value = err.message || "Failed to remove item";
        } finally {
          loading.value = false;
        }
      }
    };

    const saveOrder = async () => {
      loading.value = true;
      error.value = null;
      try {
        // Any pending changes would be saved here
        emit("updated");
      } catch (err) {
        error.value = err.message || "Failed to save order";
      } finally {
        loading.value = false;
      }
    };

    const fetchCustomer = async () => {
      if (props.order.lead_id) {
        try {
          customer.value = await ordersStore.getOrderCustomer(props.order.id);
        } catch (err) {
          console.error("Failed to fetch customer:", err);
        }
      }
    };

    onMounted(() => {
      fetchCustomer();
    });

    return {
      ordersStore,
      loading,
      error,
      customer,
      getTotalQuantity,
      calculateOrderValue,
      getStatusBadgeClass,
      getStatusText,
      formatDate,
      formatTime,
      formatCurrency,
      updateStatus,
      addItem,
      editItem,
      removeItem,
      saveOrder,
    };
  },
};
</script>
