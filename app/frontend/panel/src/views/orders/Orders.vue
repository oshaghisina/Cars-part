<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Order Management</h1>
          <p class="text-gray-600 mt-2">
            Track and manage customer orders with comprehensive details
          </p>
        </div>
        <div class="flex space-x-3">
          <button
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            @click="refreshData"
          >
            <svg
              class="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center"
              >
                <span class="text-white text-sm font-medium">📦</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Total Orders
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  {{ ordersStore.stats.totalOrders }}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center"
              >
                <span class="text-white text-sm font-medium">⏳</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Pending Orders
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  {{ ordersStore.stats.pendingOrders }}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center"
              >
                <span class="text-white text-sm font-medium">✅</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Completed Orders
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  {{ ordersStore.stats.completedOrders }}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center"
              >
                <span class="text-white text-sm font-medium">💰</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Total Value
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  ${{ formatCurrency(ordersStore.stats.totalValue) }}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Filters</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Search -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >Search</label
          >
          <input
            v-model="ordersStore.filters.search"
            type="text"
            placeholder="Search orders..."
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>

        <!-- Status -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >Status</label
          >
          <select
            v-model="ordersStore.filters.status"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">All Status</option>
            <option value="new">New</option>
            <option value="in_progress">In Progress</option>
            <option value="quoted">Quoted</option>
            <option value="won">Won</option>
            <option value="completed">Completed</option>
            <option value="lost">Lost</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        <!-- Date From -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >Date From</label
          >
          <input
            v-model="ordersStore.filters.dateFrom"
            type="date"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>

        <!-- Date To -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >Date To</label
          >
          <input
            v-model="ordersStore.filters.dateTo"
            type="date"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>

        <!-- Clear Filters -->
        <div class="flex items-end">
          <button
            class="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            @click="clearFilters"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Orders Table -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">Orders</h3>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-500">
              Showing {{ ordersStore.orders.length }} of
              {{ ordersStore.pagination.total }} orders
            </span>
            <select
              v-model="pageSize"
              class="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              @change="onPageSizeChange"
            >
              <option value="20">20 per page</option>
              <option value="50">50 per page</option>
              <option value="100">100 per page</option>
            </select>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Order ID
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Customer
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Items
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Value
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Created
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="ordersStore.loading">
              <td colspan="7" class="px-6 py-8 text-center">
                <div
                  class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
                ></div>
                <p class="mt-2 text-sm text-gray-500">Loading orders...</p>
              </td>
            </tr>

            <tr v-else-if="ordersStore.orders.length === 0">
              <td colspan="7" class="px-6 py-8 text-center">
                <svg
                  class="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                  />
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">
                  No orders found
                </h3>
                <p class="mt-1 text-sm text-gray-500">
                  Get started by creating a new order.
                </p>
              </td>
            </tr>

            <tr
              v-for="order in ordersStore.orders"
              v-else
              :key="order.id"
              class="hover:bg-gray-50"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  #{{ order.id.toString().padStart(5, "0") }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  {{ getCustomerName(order.lead_id) }}
                </div>
                <div class="text-xs text-gray-500">ID: {{ order.lead_id }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    getStatusBadgeClass(order.status),
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                  ]"
                >
                  {{ ordersStore.getStatusText(order.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  {{ order.items.length }} items
                </div>
                <div class="text-xs text-gray-500">
                  {{ getTotalQuantity(order.items) }} units
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  ${{ formatCurrency(calculateOrderValue(order)) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  {{ formatDate(order.created_at) }}
                </div>
                <div class="text-xs text-gray-500">
                  {{ formatTime(order.created_at) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <button
                    class="text-blue-600 hover:text-blue-900"
                    @click="viewOrder(order)"
                  >
                    View
                  </button>
                  <button
                    class="text-indigo-600 hover:text-indigo-900"
                    @click="editOrder(order)"
                  >
                    Edit
                  </button>
                  <button
                    class="text-green-600 hover:text-green-900"
                    @click="updateStatus(order)"
                  >
                    Status
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div
        v-if="ordersStore.pagination.totalPages > 1"
        class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6"
      >
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            :disabled="ordersStore.pagination.page === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            @click="goToPreviousPage"
          >
            Previous
          </button>
          <button
            :disabled="
              ordersStore.pagination.page === ordersStore.pagination.totalPages
            "
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            @click="goToNextPage"
          >
            Next
          </button>
        </div>
        <div
          class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between"
        >
          <div>
            <p class="text-sm text-gray-700">
              Showing
              <span class="font-medium">{{
                (ordersStore.pagination.page - 1) *
                  ordersStore.pagination.limit +
                1
              }}</span>
              to
              <span class="font-medium">{{
                Math.min(
                  ordersStore.pagination.page * ordersStore.pagination.limit,
                  ordersStore.pagination.total,
                )
              }}</span>
              of
              <span class="font-medium">{{
                ordersStore.pagination.total
              }}</span>
              results
            </p>
          </div>
          <div>
            <nav
              class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
              aria-label="Pagination"
            >
              <button
                :disabled="ordersStore.pagination.page === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                @click="goToPreviousPage"
              >
                <span class="sr-only">Previous</span>
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>

              <button
                v-for="page in visiblePages"
                :key="page"
                :class="[
                  page === ordersStore.pagination.page
                    ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                  'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                ]"
                @click="goToPage(page)"
              >
                {{ page }}
              </button>

              <button
                :disabled="
                  ordersStore.pagination.page ===
                  ordersStore.pagination.totalPages
                "
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                @click="goToNextPage"
              >
                <span class="sr-only">Next</span>
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Detail Modal will be added here -->
    <OrderDetailModal
      v-if="showOrderModal"
      :order="selectedOrder"
      @close="showOrderModal = false"
      @updated="onOrderUpdated"
    />

    <!-- Status Update Modal will be added here -->
    <StatusUpdateModal
      v-if="showStatusModal"
      :order="selectedOrder"
      @close="showStatusModal = false"
      @updated="onOrderUpdated"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from "vue";
import { useOrdersStore } from "../../stores/orders";
import { useLeadsStore } from "../../stores/leads";
import OrderDetailModal from "../../components/orders/OrderDetailModal.vue";
import StatusUpdateModal from "../../components/orders/StatusUpdateModal.vue";

export default {
  name: "Orders",
  components: {
    OrderDetailModal,
    StatusUpdateModal,
  },
  setup() {
    const ordersStore = useOrdersStore();
    const leadsStore = useLeadsStore();

    const showOrderModal = ref(false);
    const showStatusModal = ref(false);
    const selectedOrder = ref(null);
    const pageSize = ref(20);

    // Customer names cache
    const customerNames = ref({});

    const visiblePages = computed(() => {
      const current = ordersStore.pagination.page;
      const total = ordersStore.pagination.totalPages;
      const pages = [];

      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i);
        }
      } else {
        if (current <= 4) {
          for (let i = 1; i <= 5; i++) {
            pages.push(i);
          }
          pages.push("...");
          pages.push(total);
        } else if (current >= total - 3) {
          pages.push(1);
          pages.push("...");
          for (let i = total - 4; i <= total; i++) {
            pages.push(i);
          }
        } else {
          pages.push(1);
          pages.push("...");
          for (let i = current - 1; i <= current + 1; i++) {
            pages.push(i);
          }
          pages.push("...");
          pages.push(total);
        }
      }

      return pages;
    });

    const getCustomerName = (leadId) => {
      if (!leadId) return "Unknown Customer";
      return customerNames.value[leadId] || `Customer #${leadId}`;
    };

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

    const refreshData = async () => {
      await Promise.all([ordersStore.fetchOrders(), leadsStore.fetchLeads()]);

      // Build customer names cache
      leadsStore.leads.forEach((lead) => {
        customerNames.value[lead.id] =
          `${lead.first_name || ""} ${lead.last_name || ""}`.trim() ||
          "Unknown Customer";
      });
    };

    const onPageSizeChange = () => {
      ordersStore.setLimit(parseInt(pageSize.value));
      fetchOrdersWithFilters();
    };

    const clearFilters = () => {
      ordersStore.clearFilters();
      fetchOrdersWithFilters();
    };

    const fetchOrdersWithFilters = () => {
      const params = {
        page: ordersStore.pagination.page,
        limit: ordersStore.pagination.limit,
        ...ordersStore.filters,
      };
      ordersStore.fetchOrders(params);
    };

    const goToPage = (page) => {
      if (page !== "...") {
        ordersStore.setPage(page);
        fetchOrdersWithFilters();
      }
    };

    const goToPreviousPage = () => {
      if (ordersStore.pagination.page > 1) {
        ordersStore.setPage(ordersStore.pagination.page - 1);
        fetchOrdersWithFilters();
      }
    };

    const goToNextPage = () => {
      if (ordersStore.pagination.page < ordersStore.pagination.totalPages) {
        ordersStore.setPage(ordersStore.pagination.page + 1);
        fetchOrdersWithFilters();
      }
    };

    const viewOrder = (order) => {
      selectedOrder.value = order;
      showOrderModal.value = true;
    };

    const editOrder = (order) => {
      selectedOrder.value = order;
      showOrderModal.value = true;
    };

    const updateStatus = (order) => {
      selectedOrder.value = order;
      showStatusModal.value = true;
    };

    const onOrderUpdated = () => {
      showOrderModal.value = false;
      showStatusModal.value = false;
      selectedOrder.value = null;
      fetchOrdersWithFilters();
    };

    // Watch for filter changes
    watch(
      () => ordersStore.filters,
      () => {
        fetchOrdersWithFilters();
      },
      { deep: true },
    );

    onMounted(async () => {
      await refreshData();
    });

    return {
      ordersStore,
      leadsStore,
      showOrderModal,
      showStatusModal,
      selectedOrder,
      pageSize,
      customerNames,
      visiblePages,
      getCustomerName,
      getTotalQuantity,
      calculateOrderValue,
      getStatusBadgeClass,
      formatDate,
      formatTime,
      formatCurrency,
      refreshData,
      onPageSizeChange,
      clearFilters,
      goToPage,
      goToPreviousPage,
      goToNextPage,
      viewOrder,
      editOrder,
      updateStatus,
      onOrderUpdated,
    };
  },
};
</script>
