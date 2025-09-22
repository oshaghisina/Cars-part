import { defineStore } from "pinia";
import axios from "axios";

export const useAnalyticsStore = defineStore("analytics", {
  state: () => ({
    // Dashboard metrics
    dashboardMetrics: {
      total_parts: 0,
      active_parts: 0,
      total_vehicles: 0,
      total_categories: 0,
      total_orders: 0,
      pending_orders: 0,
      completed_orders: 0,
      total_revenue: 0,
      total_leads: 0,
      new_leads: 0,
      total_users: 0,
      active_users: 0,
      date_range: {},
    },

    // Sales analytics
    salesAnalytics: {
      period: "30d",
      total_revenue: 0,
      revenue_growth: 0,
      total_orders: 0,
      revenue_trends: [],
      status_distribution: {},
      top_customers: [],
    },

    // Inventory analytics
    inventoryAnalytics: {
      total_parts: 0,
      parts_by_category: [],
      parts_by_brand: [],
      price_distribution: {},
      status_distribution: {},
      low_stock_items: [],
    },

    // Customer analytics
    customerAnalytics: {
      period: "30d",
      total_leads: 0,
      converted_leads: 0,
      conversion_rate: 0,
      acquisition_trends: [],
      geographic_distribution: {},
      lead_sources: {},
    },

    // Performance metrics
    performanceMetrics: {
      api: {},
      database: {},
      bot: {},
      last_updated: "",
    },

    // Charts data
    chartsData: {
      partsByCategory: null,
      salesTrend: null,
      revenueChart: null,
      customerChart: null,
    },

    // Reports
    reports: [],
    currentReport: null,

    // UI state
    loading: {
      dashboard: false,
      sales: false,
      inventory: false,
      customers: false,
      performance: false,
      charts: false,
      reports: false,
    },

    error: null,

    // Filters
    filters: {
      dateFrom: null,
      dateTo: null,
      period: "30d",
      category: null,
      brand: null,
      status: null,
    },
  }),

  getters: {
    // Dashboard metrics
    getDashboardMetrics: (state) => state.dashboardMetrics,
    isDashboardLoading: (state) => state.loading.dashboard,

    // Sales analytics
    getSalesAnalytics: (state) => state.salesAnalytics,
    isSalesLoading: (state) => state.loading.sales,
    getRevenueGrowthColor: (state) => {
      const growth = state.salesAnalytics.revenue_growth;
      if (growth > 0) return "text-green-600";
      if (growth < 0) return "text-red-600";
      return "text-gray-600";
    },

    // Inventory analytics
    getInventoryAnalytics: (state) => state.inventoryAnalytics,
    isInventoryLoading: (state) => state.loading.inventory,
    getLowStockCount: (state) =>
      state.inventoryAnalytics.low_stock_items.length,

    // Customer analytics
    getCustomerAnalytics: (state) => state.customerAnalytics,
    isCustomerLoading: (state) => state.loading.customers,
    getConversionRateColor: (state) => {
      const rate = state.customerAnalytics.conversion_rate;
      if (rate >= 20) return "text-green-600";
      if (rate >= 10) return "text-yellow-600";
      return "text-red-600";
    },

    // Performance metrics
    getPerformanceMetrics: (state) => state.performanceMetrics,
    isPerformanceLoading: (state) => state.loading.performance,

    // Charts
    getChartsData: (state) => state.chartsData,
    isChartsLoading: (state) => state.loading.charts,

    // Reports
    getReports: (state) => state.reports,
    getCurrentReport: (state) => state.currentReport,
    isReportsLoading: (state) => state.loading.reports,

    // General
    hasError: (state) => !!state.error,
    getError: (state) => state.error,
  },

  actions: {
    // Dashboard metrics
    async fetchDashboardMetrics(dateFrom = null, dateTo = null) {
      this.loading.dashboard = true;
      this.error = null;

      try {
        const params = new URLSearchParams();
        if (dateFrom) params.append("date_from", dateFrom);
        if (dateTo) params.append("date_to", dateTo);

        const response = await axios.get(
          `/api/v1/analytics/dashboard/metrics?${params}`,
        );
        this.dashboardMetrics = response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch dashboard metrics";
        console.error("Error fetching dashboard metrics:", error);
      } finally {
        this.loading.dashboard = false;
      }
    },

    // Sales analytics
    async fetchSalesAnalytics(period = "30d") {
      this.loading.sales = true;
      this.error = null;

      try {
        const response = await axios.get(
          `/api/v1/analytics/sales/analytics?period=${period}`,
        );
        this.salesAnalytics = response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch sales analytics";
        console.error("Error fetching sales analytics:", error);
      } finally {
        this.loading.sales = false;
      }
    },

    // Inventory analytics
    async fetchInventoryAnalytics() {
      this.loading.inventory = true;
      this.error = null;

      try {
        const response = await axios.get(
          "/api/v1/analytics/inventory/analytics",
        );
        this.inventoryAnalytics = response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch inventory analytics";
        console.error("Error fetching inventory analytics:", error);
      } finally {
        this.loading.inventory = false;
      }
    },

    // Customer analytics
    async fetchCustomerAnalytics(period = "30d") {
      this.loading.customers = true;
      this.error = null;

      try {
        const response = await axios.get(
          `/api/v1/analytics/customers/analytics?period=${period}`,
        );
        this.customerAnalytics = response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch customer analytics";
        console.error("Error fetching customer analytics:", error);
      } finally {
        this.loading.customers = false;
      }
    },

    // Performance metrics
    async fetchPerformanceMetrics() {
      this.loading.performance = true;
      this.error = null;

      try {
        const response = await axios.get(
          "/api/v1/analytics/performance/metrics",
        );
        this.performanceMetrics = response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch performance metrics";
        console.error("Error fetching performance metrics:", error);
      } finally {
        this.loading.performance = false;
      }
    },

    // Charts data
    async fetchPartsByCategoryChart() {
      this.loading.charts = true;
      this.error = null;

      try {
        const response = await axios.get(
          "/api/v1/analytics/charts/parts-by-category",
        );
        this.chartsData.partsByCategory = response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail ||
          "Failed to fetch parts by category chart";
        console.error("Error fetching parts by category chart:", error);
      } finally {
        this.loading.charts = false;
      }
    },

    async fetchSalesTrendChart(period = "30d") {
      this.loading.charts = true;
      this.error = null;

      try {
        const response = await axios.get(
          `/api/v1/analytics/charts/sales-trend?period=${period}`,
        );
        this.chartsData.salesTrend = response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch sales trend chart";
        console.error("Error fetching sales trend chart:", error);
      } finally {
        this.loading.charts = false;
      }
    },

    // Reports
    async generateReport(reportRequest) {
      this.loading.reports = true;
      this.error = null;

      try {
        const response = await axios.post(
          "/api/v1/analytics/reports/generate",
          reportRequest,
        );
        this.currentReport = response.data;
        return response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to generate report";
        console.error("Error generating report:", error);
        throw error;
      } finally {
        this.loading.reports = false;
      }
    },

    async exportData(exportRequest) {
      this.loading.reports = true;
      this.error = null;

      try {
        const response = await axios.post(
          "/api/v1/analytics/export",
          exportRequest,
          {
            responseType: "blob",
          },
        );

        // Create download link
        const blob = new Blob([response.data]);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;

        const filename =
          response.headers["content-disposition"]?.split("filename=")[1] ||
          "export.xlsx";
        link.download = filename;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        return { success: true, filename };
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to export data";
        console.error("Error exporting data:", error);
        throw error;
      } finally {
        this.loading.reports = false;
      }
    },

    // Bulk data fetch
    async fetchAllAnalytics(period = "30d") {
      try {
        await Promise.all([
          this.fetchDashboardMetrics(),
          this.fetchSalesAnalytics(period),
          this.fetchInventoryAnalytics(),
          this.fetchCustomerAnalytics(period),
          this.fetchPerformanceMetrics(),
          this.fetchPartsByCategoryChart(),
          this.fetchSalesTrendChart(period),
        ]);
      } catch (error) {
        console.error("Error fetching all analytics:", error);
      }
    },

    // Filter management
    setFilter(key, value) {
      this.filters[key] = value;
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters };
    },

    clearFilters() {
      this.filters = {
        dateFrom: null,
        dateTo: null,
        period: "30d",
        category: null,
        brand: null,
        status: null,
      };
    },

    // Utility methods
    formatCurrency(amount) {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount);
    },

    formatPercentage(value, decimals = 1) {
      return `${value.toFixed(decimals)}%`;
    },

    formatNumber(value) {
      return new Intl.NumberFormat("en-US").format(value);
    },

    // Error handling
    clearError() {
      this.error = null;
    },
  },
});
