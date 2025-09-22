<template>
  <div class="space-y-6">
    <!-- Inventory Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Total Parts -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div
              class="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center"
            >
              <CubeIcon class="w-5 h-5 text-blue-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Parts</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ formatNumber(analytics.total_parts) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Low Stock Items -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div
              class="w-8 h-8 bg-red-100 rounded-md flex items-center justify-center"
            >
              <ExclamationTriangleIcon class="w-5 h-5 text-red-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Low Stock Items</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ analytics.low_stock_items.length }}
            </p>
          </div>
        </div>
      </div>

      <!-- Categories Count -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div
              class="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center"
            >
              <TagIcon class="w-5 h-5 text-green-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Categories</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ analytics.parts_by_category.length }}
            </p>
          </div>
        </div>
      </div>

      <!-- Brands Count -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div
              class="w-8 h-8 bg-purple-100 rounded-md flex items-center justify-center"
            >
              <BuildingStorefrontIcon class="w-5 h-5 text-purple-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Brands</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ analytics.parts_by_brand.length }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Parts by Category Chart -->
      <div class="chart-container">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Parts by Category</h3>
          <button
            :disabled="loading"
            class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
            @click="$emit('refresh')"
          >
            Refresh
          </button>
        </div>
        <div v-if="loading" class="h-64 flex items-center justify-center">
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
        </div>
        <div v-else class="h-64">
          <PartsByCategoryChart />
        </div>
      </div>

      <!-- Parts by Brand Chart -->
      <div class="chart-container">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Top Brands</h3>
          <button
            :disabled="loading"
            class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
            @click="$emit('refresh')"
          >
            Refresh
          </button>
        </div>
        <div v-if="loading" class="h-64 flex items-center justify-center">
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
        </div>
        <div v-else class="h-64">
          <PartsByBrandChart :data="analytics.parts_by_brand" />
        </div>
      </div>
    </div>

    <!-- Price Distribution -->
    <div class="chart-container">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">Price Distribution</h3>
        <button
          :disabled="loading"
          class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
          @click="$emit('refresh')"
        >
          Refresh
        </button>
      </div>

      <div v-if="loading" class="space-y-3">
        <div v-for="i in 5" :key="i" class="loading-skeleton h-8"></div>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="(count, range) in analytics.price_distribution"
          :key="range"
          class="flex items-center"
        >
          <div class="w-24 text-sm text-gray-600">{{ range }}</div>
          <div class="flex-1 mx-4">
            <div class="bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full"
                :style="{ width: `${(count / getMaxPriceCount) * 100}%` }"
              ></div>
            </div>
          </div>
          <div class="w-16 text-sm text-gray-900 text-right">
            {{ formatNumber(count) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Low Stock Items Table -->
    <div v-if="analytics.low_stock_items.length > 0" class="chart-container">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">Low Stock Items</h3>
        <button
          :disabled="loading"
          class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
          @click="$emit('refresh')"
        >
          Refresh
        </button>
      </div>

      <div v-if="loading" class="space-y-3">
        <div v-for="i in 5" :key="i" class="loading-skeleton h-12"></div>
      </div>

      <div v-else class="overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Part Name
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Brand/OEM
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                OEM Code
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Stock Quantity
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="item in analytics.low_stock_items.slice(0, 10)"
              :key="item.id"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ item.part_name }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ item.brand_oem }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ item.oem_code }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                >
                  {{ item.stock_quantity }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Status Distribution -->
    <div class="chart-container">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">Status Distribution</h3>
        <button
          :disabled="loading"
          class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
          @click="$emit('refresh')"
        >
          Refresh
        </button>
      </div>

      <div v-if="loading" class="h-64 flex items-center justify-center">
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
        ></div>
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div
          v-for="(count, status) in analytics.status_distribution"
          :key="status"
          class="text-center"
        >
          <div class="text-2xl font-semibold text-gray-900">
            {{ formatNumber(count) }}
          </div>
          <div class="text-sm text-gray-500 capitalize">{{ status }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import {
  CubeIcon,
  ExclamationTriangleIcon,
  TagIcon,
  BuildingStorefrontIcon,
} from "@heroicons/vue/24/outline";
import PartsByCategoryChart from "./charts/PartsByCategoryChart.vue";
import PartsByBrandChart from "./charts/PartsByBrandChart.vue";

// Props
const props = defineProps({
  analytics: {
    type: Object,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

// Emits
defineEmits(["refresh"]);

// Computed
const getMaxPriceCount = computed(() => {
  const counts = Object.values(props.analytics.price_distribution);
  return Math.max(...counts, 1);
});

// Utility functions
const formatNumber = (value) => {
  return new Intl.NumberFormat("en-US").format(value);
};
</script>
