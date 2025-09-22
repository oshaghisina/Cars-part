<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">Bulk Operations</h3>
      <div class="flex items-center space-x-2">
        <span class="text-sm text-gray-500"
          >{{ selectedCount }} items selected</span
        >
        <button
          v-if="selectedCount > 0"
          class="text-sm text-gray-500 hover:text-gray-700"
          @click="clearSelection"
        >
          Clear Selection
        </button>
      </div>
    </div>

    <!-- Operation Tabs -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in operationTabs"
          :key="tab.id"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
          ]"
          @click="activeTab = tab.id"
        >
          <svg
            class="w-4 h-4 mr-2 inline"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              :d="tab.icon"
            />
          </svg>
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Import Operations -->
    <div v-show="activeTab === 'import'" class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- File Upload -->
        <div>
          <h4 class="text-md font-medium text-gray-900 mb-3">Import Data</h4>
          <div
            :class="[
              'border-2 border-dashed rounded-lg p-6 text-center transition-colors',
              isDragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300',
            ]"
            @drop="handleFileDrop"
            @dragover.prevent
            @dragenter.prevent
          >
            <svg
              class="mx-auto h-12 w-12 text-gray-400 mb-4"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <p class="text-sm text-gray-600 mb-2">
              Drag and drop files here, or
              <label class="text-blue-600 hover:text-blue-500 cursor-pointer">
                browse
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".csv,.xlsx,.json"
                  class="hidden"
                  @change="handleFileSelect"
                />
              </label>
            </p>
            <p class="text-xs text-gray-500">
              CSV, Excel, or JSON files up to 10MB
            </p>
          </div>

          <!-- Selected Files -->
          <div v-if="selectedFiles.length > 0" class="mt-4">
            <h5 class="text-sm font-medium text-gray-700 mb-2">
              Selected Files:
            </h5>
            <div class="space-y-2">
              <div
                v-for="(file, index) in selectedFiles"
                :key="index"
                class="flex items-center justify-between p-2 bg-gray-50 rounded"
              >
                <div class="flex items-center">
                  <svg
                    class="w-5 h-5 text-gray-400 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <span class="text-sm text-gray-700">{{ file.name }}</span>
                  <span class="ml-2 text-xs text-gray-500"
                    >({{ formatFileSize(file.size) }})</span
                  >
                </div>
                <button
                  class="text-red-500 hover:text-red-700"
                  @click="removeFile(index)"
                >
                  <svg
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
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Import Options -->
        <div>
          <h4 class="text-md font-medium text-gray-900 mb-3">Import Options</h4>
          <div class="space-y-4">
            <!-- Data Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Data Type</label
              >
              <select
                v-model="importOptions.dataType"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="vehicles">Vehicles</option>
                <option value="parts">Parts</option>
                <option value="categories">Categories</option>
                <option value="orders">Orders</option>
                <option value="leads">Leads</option>
              </select>
            </div>

            <!-- Import Mode -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Import Mode</label
              >
              <div class="space-y-2">
                <label class="flex items-center">
                  <input
                    v-model="importOptions.mode"
                    type="radio"
                    value="create"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span class="ml-2 text-sm text-gray-700"
                    >Create new records only</span
                  >
                </label>
                <label class="flex items-center">
                  <input
                    v-model="importOptions.mode"
                    type="radio"
                    value="update"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span class="ml-2 text-sm text-gray-700"
                    >Update existing records</span
                  >
                </label>
                <label class="flex items-center">
                  <input
                    v-model="importOptions.mode"
                    type="radio"
                    value="upsert"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span class="ml-2 text-sm text-gray-700"
                    >Create or update records</span
                  >
                </label>
              </div>
            </div>

            <!-- Validation Options -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Validation</label
              >
              <div class="space-y-2">
                <label class="flex items-center">
                  <input
                    v-model="importOptions.validateData"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700"
                    >Validate data before import</span
                  >
                </label>
                <label class="flex items-center">
                  <input
                    v-model="importOptions.skipErrors"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700"
                    >Skip rows with errors</span
                  >
                </label>
              </div>
            </div>

            <!-- Import Button -->
            <button
              :disabled="selectedFiles.length === 0 || isImporting"
              class="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              @click="startImport"
            >
              <svg
                v-if="isImporting"
                class="w-4 h-4 mr-2 inline animate-spin"
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
              <svg
                v-else
                class="w-4 h-4 mr-2 inline"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                />
              </svg>
              {{ isImporting ? "Importing..." : "Start Import" }}
            </button>
          </div>
        </div>
      </div>

      <!-- Import Progress -->
      <div v-if="importProgress.show" class="mt-6">
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">{{
              importProgress.message
            }}</span>
            <span class="text-sm text-gray-500"
              >{{ importProgress.percentage }}%</span
            >
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: importProgress.percentage + '%' }"
            ></div>
          </div>
          <div class="mt-2 text-sm text-gray-600">
            {{ importProgress.processed }} of {{ importProgress.total }} records
            processed
          </div>
        </div>
      </div>
    </div>

    <!-- Export Operations -->
    <div v-show="activeTab === 'export'" class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Export Options -->
        <div>
          <h4 class="text-md font-medium text-gray-900 mb-3">Export Options</h4>
          <div class="space-y-4">
            <!-- Data Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Data Type</label
              >
              <select
                v-model="exportOptions.dataType"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="vehicles">Vehicles</option>
                <option value="parts">Parts</option>
                <option value="categories">Categories</option>
                <option value="orders">Orders</option>
                <option value="leads">Leads</option>
                <option value="all">All Data</option>
              </select>
            </div>

            <!-- Format -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Export Format</label
              >
              <select
                v-model="exportOptions.format"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="csv">CSV</option>
                <option value="xlsx">Excel (XLSX)</option>
                <option value="json">JSON</option>
              </select>
            </div>

            <!-- Date Range -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Date Range</label
              >
              <div class="flex space-x-2">
                <input
                  v-model="exportOptions.dateFrom"
                  type="date"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <input
                  v-model="exportOptions.dateTo"
                  type="date"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <!-- Fields Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Fields to Export</label
              >
              <div
                class="max-h-32 overflow-y-auto border border-gray-300 rounded-md p-2"
              >
                <label
                  v-for="field in availableFields"
                  :key="field.id"
                  class="flex items-center mb-1"
                >
                  <input
                    v-model="exportOptions.fields"
                    :value="field.id"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700">{{
                    field.label
                  }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Export Actions -->
        <div>
          <h4 class="text-md font-medium text-gray-900 mb-3">Export Actions</h4>
          <div class="space-y-4">
            <button
              :disabled="isExporting"
              class="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              @click="startExport"
            >
              <svg
                v-if="isExporting"
                class="w-4 h-4 mr-2 inline animate-spin"
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
              <svg
                v-else
                class="w-4 h-4 mr-2 inline"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              {{ isExporting ? "Exporting..." : "Start Export" }}
            </button>

            <!-- Recent Exports -->
            <div v-if="recentExports.length > 0">
              <h5 class="text-sm font-medium text-gray-700 mb-2">
                Recent Exports
              </h5>
              <div class="space-y-2">
                <div
                  v-for="exportItem in recentExports"
                  :key="exportItem.id"
                  class="flex items-center justify-between p-2 bg-gray-50 rounded"
                >
                  <div class="flex items-center">
                    <svg
                      class="w-4 h-4 text-gray-400 mr-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    <div>
                      <div class="text-sm text-gray-700">
                        {{ exportItem.name }}
                      </div>
                      <div class="text-xs text-gray-500">
                        {{ formatDate(exportItem.createdAt) }}
                      </div>
                    </div>
                  </div>
                  <button
                    class="text-blue-600 hover:text-blue-800"
                    @click="downloadExport(exportItem)"
                  >
                    <svg
                      class="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Batch Operations -->
    <div v-show="activeTab === 'batch'" class="space-y-6">
      <div v-if="selectedCount === 0" class="text-center py-8 text-gray-500">
        <svg
          class="mx-auto h-12 w-12 text-gray-400 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p>Select items to perform batch operations</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Update Status -->
        <div class="p-4 border border-gray-200 rounded-lg">
          <h5 class="font-medium text-gray-900 mb-2">Update Status</h5>
          <select
            v-model="batchOperations.newStatus"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
          <button
            :disabled="!batchOperations.newStatus"
            class="mt-2 w-full px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            @click="batchUpdateStatus"
          >
            Update Status
          </button>
        </div>

        <!-- Assign Category -->
        <div class="p-4 border border-gray-200 rounded-lg">
          <h5 class="font-medium text-gray-900 mb-2">Assign Category</h5>
          <select
            v-model="batchOperations.category"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select Category</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
          <button
            :disabled="!batchOperations.category"
            class="mt-2 w-full px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            @click="batchAssignCategory"
          >
            Assign Category
          </button>
        </div>

        <!-- Delete Items -->
        <div class="p-4 border border-gray-200 rounded-lg">
          <h5 class="font-medium text-gray-900 mb-2">Delete Items</h5>
          <p class="text-sm text-gray-600 mb-2">This action cannot be undone</p>
          <button
            class="w-full px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            @click="confirmBatchDelete"
          >
            Delete Selected
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from "vue";

export default {
  name: "BulkOperations",
  props: {
    selectedItems: {
      type: Array,
      default: () => [],
    },
    categories: {
      type: Array,
      default: () => [],
    },
  },
  emits: [
    "import-complete",
    "export-complete",
    "batch-operation",
    "clear-selection",
  ],
  setup(props, { emit }) {
    const activeTab = ref("import");
    const selectedFiles = ref([]);
    const isDragOver = ref(false);
    const isImporting = ref(false);
    const isExporting = ref(false);

    const operationTabs = [
      {
        id: "import",
        name: "Import",
        icon: "M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10",
      },
      {
        id: "export",
        name: "Export",
        icon: "M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
      },
      {
        id: "batch",
        name: "Batch Operations",
        icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
      },
    ];

    const importOptions = ref({
      dataType: "parts",
      mode: "upsert",
      validateData: true,
      skipErrors: true,
    });

    const exportOptions = ref({
      dataType: "parts",
      format: "csv",
      dateFrom: "",
      dateTo: "",
      fields: [],
    });

    const batchOperations = ref({
      newStatus: "",
      category: "",
    });

    const importProgress = ref({
      show: false,
      percentage: 0,
      processed: 0,
      total: 0,
      message: "",
    });

    const recentExports = ref([
      {
        id: 1,
        name: "Parts Export - 2024-01-15.csv",
        createdAt: new Date("2024-01-15"),
        url: "/exports/parts-2024-01-15.csv",
      },
    ]);

    const availableFields = ref([
      { id: "id", label: "ID" },
      { id: "name", label: "Name" },
      { id: "description", label: "Description" },
      { id: "category", label: "Category" },
      { id: "price", label: "Price" },
      { id: "status", label: "Status" },
      { id: "created_at", label: "Created At" },
      { id: "updated_at", label: "Updated At" },
    ]);

    const selectedCount = computed(() => props.selectedItems.length);

    const handleFileDrop = (e) => {
      e.preventDefault();
      isDragOver.value = false;
      const files = Array.from(e.dataTransfer.files);
      addFiles(files);
    };

    const handleFileSelect = (e) => {
      const files = Array.from(e.target.files);
      addFiles(files);
    };

    const addFiles = (files) => {
      files.forEach((file) => {
        if (file.size <= 10 * 1024 * 1024) {
          // 10MB limit
          selectedFiles.value.push(file);
        }
      });
    };

    const removeFile = (index) => {
      selectedFiles.value.splice(index, 1);
    };

    const formatFileSize = (bytes) => {
      if (bytes === 0) return "0 Bytes";
      const k = 1024;
      const sizes = ["Bytes", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
    };

    const startImport = async () => {
      isImporting.value = true;
      importProgress.value = {
        show: true,
        percentage: 0,
        processed: 0,
        total: 100,
        message: "Starting import...",
      };

      try {
        // Simulate import progress
        for (let i = 0; i <= 100; i += 10) {
          await new Promise((resolve) => setTimeout(resolve, 200));
          importProgress.value = {
            ...importProgress.value,
            percentage: i,
            processed: i,
            message: `Processing records... ${i}%`,
          };
        }

        importProgress.value.message = "Import completed successfully!";
        emit("import-complete", { success: true, files: selectedFiles.value });

        // Clear files after successful import
        selectedFiles.value = [];
      } catch (error) {
        importProgress.value.message = `Import failed: ${error.message}`;
        emit("import-complete", { success: false, error: error.message });
      } finally {
        isImporting.value = false;
        setTimeout(() => {
          importProgress.value.show = false;
        }, 3000);
      }
    };

    const startExport = async () => {
      isExporting.value = true;

      try {
        // Implement actual export API call
        const response = await fetch("/api/v1/bulk-operations/export", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            dataType: exportOptions.value.dataType,
            format: exportOptions.value.format,
            filters: exportOptions.value.filters,
            fields: exportOptions.value.selectedFields,
          }),
        });

        if (!response.ok) {
          throw new Error(`Export failed: ${response.statusText}`);
        }

        const blob = await response.blob();
        const exportName = `${exportOptions.value.dataType}-export-${new Date().toISOString().split("T")[0]}.${exportOptions.value.format}`;

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = exportName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        // Add to recent exports
        recentExports.value.unshift({
          id: Date.now(),
          name: exportName,
          createdAt: new Date(),
          url,
          size: blob.size,
        });

        emit("export-complete", { success: true, fileName: exportName });
      } catch (error) {
        emit("export-complete", { success: false, error: error.message });
      } finally {
        isExporting.value = false;
      }
    };

    const downloadExport = (exportItem) => {
      // Implement actual download
      console.log("Downloading:", exportItem.name);

      // If we have a URL, create download link
      if (exportItem.url) {
        const link = document.createElement("a");
        link.href = exportItem.url;
        link.download = exportItem.name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // Fallback: trigger re-download from server
        fetch(`/api/v1/bulk-operations/download/${exportItem.id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        })
          .then((response) => response.blob())
          .then((blob) => {
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = exportItem.name;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
          })
          .catch((error) => {
            console.error("Download failed:", error);
          });
      }
    };

    const batchUpdateStatus = () => {
      emit("batch-operation", {
        type: "update-status",
        items: props.selectedItems,
        data: { status: batchOperations.value.newStatus },
      });
    };

    const batchAssignCategory = () => {
      emit("batch-operation", {
        type: "assign-category",
        items: props.selectedItems,
        data: { category: batchOperations.value.category },
      });
    };

    const confirmBatchDelete = () => {
      if (
        confirm(
          `Are you sure you want to delete ${props.selectedItems.length} items? This action cannot be undone.`,
        )
      ) {
        emit("batch-operation", {
          type: "delete",
          items: props.selectedItems,
        });
      }
    };

    const clearSelection = () => {
      emit("clear-selection");
    };

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString();
    };

    return {
      activeTab,
      operationTabs,
      selectedFiles,
      isDragOver,
      isImporting,
      isExporting,
      importOptions,
      exportOptions,
      batchOperations,
      importProgress,
      recentExports,
      availableFields,
      selectedCount,
      handleFileDrop,
      handleFileSelect,
      removeFile,
      formatFileSize,
      startImport,
      startExport,
      downloadExport,
      batchUpdateStatus,
      batchAssignCategory,
      confirmBatchDelete,
      clearSelection,
      formatDate,
    };
  },
};
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
