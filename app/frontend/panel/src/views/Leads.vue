<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900">Customers</h1>
      <p class="text-gray-600 mt-2">Manage customer information and leads</p>
    </div>

    <!-- Leads Table -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div v-if="leadsStore.loading" class="text-center py-8">
          <div
            class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
          <p class="mt-2 text-sm text-gray-500">Loading customers...</p>
        </div>

        <div v-else-if="leadsStore.error" class="text-center py-8">
          <p class="text-red-500">{{ leadsStore.error }}</p>
          <button
            class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            @click="leadsStore.fetchLeads()"
          >
            Retry
          </button>
        </div>

        <div v-else-if="leadsStore.leads.length === 0" class="text-center py-8">
          <p class="text-gray-500">No customers found</p>
        </div>

        <div
          v-else
          class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg"
        >
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Customer ID
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Name
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Phone
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Telegram ID
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
              <tr v-for="lead in leadsStore.leads" :key="lead.id">
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
                >
                  #{{ lead.id.toString().padStart(3, "0") }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ lead.first_name || "N/A" }} {{ lead.last_name || "" }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ lead.phone_e164 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ lead.telegram_user_id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(lead.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    class="text-blue-600 hover:text-blue-900"
                    @click="viewCustomer(lead.id)"
                  >
                    View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted } from "vue";
import { useLeadsStore } from "../stores/leads";

export default {
  name: "Leads",
  setup() {
    const leadsStore = useLeadsStore();

    onMounted(() => {
      leadsStore.fetchLeads();
    });

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString();
    };

    const viewCustomer = (leadId) => {
      // Navigate to customer detail view
      console.log("View customer:", leadId);
    };

    return {
      leadsStore,
      formatDate,
      viewCustomer,
    };
  },
};
</script>
