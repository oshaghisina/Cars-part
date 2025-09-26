import { defineStore } from "pinia";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const useDashboardStore = defineStore("dashboard", {
  state: () => ({
    loading: false,
    error: null,

    // Key Metrics
    metrics: {
      totalParts: 0,
      totalVehicles: 0,
      totalCategories: 0,
      totalOrders: 0,
      totalLeads: 0,
      activeParts: 0,
      pendingOrders: 0,
      newLeads: 0,
    },

    // Charts Data
    charts: {
      partsByCategory: [],
      partsByBrand: [],
      ordersOverTime: [],
      leadsOverTime: [],
      topCategories: [],
      topBrands: [],
      orderStatusDistribution: [],
      leadStatusDistribution: [],
    },

    // Recent Activity
    recentActivity: {
      recentOrders: [],
      recentLeads: [],
      recentParts: [],
      recentCategories: [],
    },

    // System Health
    systemHealth: {
      apiStatus: "healthy",
      databaseStatus: "healthy",
      botStatus: "healthy",
      lastUpdate: null,
    },
  }),

  getters: {
    // Computed metrics
    totalSystems: (state) =>
      state.metrics.totalParts +
      state.metrics.totalVehicles +
      state.metrics.totalCategories,

    // Health status
    overallHealth: (state) => {
      const statuses = [
        state.systemHealth.apiStatus,
        state.systemHealth.databaseStatus,
        state.systemHealth.botStatus,
      ];
      return statuses.every((status) => status === "healthy")
        ? "healthy"
        : "warning";
    },

    // Chart data for visualization
    chartDataReady: (state) => {
      return Object.values(state.charts).every((chart) => chart.length > 0);
    },

    // Activity summary
    hasRecentActivity: (state) => {
      const activities = [
        state.recentActivity.recentOrders,
        state.recentActivity.recentLeads,
        state.recentActivity.recentParts,
        state.recentActivity.recentCategories,
      ];
      return activities.some((activity) => activity.length > 0);
    },
  },

  actions: {
    async fetchDashboardData() {
      this.loading = true;
      this.error = null;

      try {
        // Fetch all dashboard data in parallel
        await Promise.all([
          this.fetchMetrics(),
          this.fetchChartsData(),
          this.fetchRecentActivity(),
          this.checkSystemHealth(),
        ]);

        this.systemHealth.lastUpdate = new Date().toISOString();
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch dashboard data";
        console.error("Error fetching dashboard data:", error);
      } finally {
        this.loading = false;
      }
    },

    async fetchMetrics() {
      try {
        // Fetch parts metrics
        const partsResponse = await axios.get(`${API_BASE}/parts/`);
        const parts = partsResponse.data;
        this.metrics.totalParts = parts.length;
        this.metrics.activeParts = parts.filter(
          (part) => part.status === "active",
        ).length;

        // Fetch vehicles metrics
        const [brandsResponse, modelsResponse, trimsResponse] =
          await Promise.all([
            axios.get(`${API_BASE}/vehicles/brands`),
            axios.get(`${API_BASE}/vehicles/models`),
            axios.get(`${API_BASE}/vehicles/trims`),
          ]);
        this.metrics.totalVehicles =
          brandsResponse.data.length +
          modelsResponse.data.length +
          trimsResponse.data.length;

        // Fetch categories metrics
        const categoriesResponse = await axios.get(`${API_BASE}/categories/`);
        this.metrics.totalCategories = categoriesResponse.data.length;

        // Fetch orders metrics
        const ordersResponse = await axios.get(`${API_BASE}/orders/`);
        const orders = ordersResponse.data;
        this.metrics.totalOrders = orders.length;
        this.metrics.pendingOrders = orders.filter((order) =>
          ["new", "in_progress", "quoted"].includes(order.status),
        ).length;

        // Fetch leads metrics (if available)
        try {
          const leadsResponse = await axios.get(`${API_BASE}/leads/`);
          const leads = leadsResponse.data;
          this.metrics.totalLeads = leads.length;
          this.metrics.newLeads = leads.filter(
            (lead) =>
              new Date(lead.created_at) >
              new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
          ).length;
        } catch (error) {
          // Leads API might not be available yet
          this.metrics.totalLeads = 0;
          this.metrics.newLeads = 0;
        }
      } catch (error) {
        console.error("Error fetching metrics:", error);
        throw error;
      }
    },

    async fetchChartsData() {
      try {
        // Fetch parts data for charts
        const partsResponse = await axios.get(`${API_BASE}/parts/`);
        const parts = partsResponse.data;

        // Parts by category
        const categoryCount = {};
        const brandCount = {};

        parts.forEach((part) => {
          // Category distribution
          if (part.category) {
            categoryCount[part.category] =
              (categoryCount[part.category] || 0) + 1;
          }

          // Brand distribution
          if (part.vehicle_make) {
            brandCount[part.vehicle_make] =
              (brandCount[part.vehicle_make] || 0) + 1;
          }
        });

        this.charts.partsByCategory = Object.entries(categoryCount)
          .map(([name, value]) => ({ name, value }))
          .sort((a, b) => b.value - a.value);

        this.charts.partsByBrand = Object.entries(brandCount)
          .map(([name, value]) => ({ name, value }))
          .sort((a, b) => b.value - a.value);

        // Top categories and brands
        this.charts.topCategories = this.charts.partsByCategory.slice(0, 5);
        this.charts.topBrands = this.charts.partsByBrand.slice(0, 5);

        // Orders over time (mock data for now)
        this.charts.ordersOverTime = this.generateTimeSeriesData("orders");
        this.charts.leadsOverTime = this.generateTimeSeriesData("leads");

        // Order status distribution
        const ordersResponse = await axios.get(`${API_BASE}/orders/`);
        const orders = ordersResponse.data;
        const orderStatusCount = {};

        orders.forEach((order) => {
          const status = order.status || "unknown";
          orderStatusCount[status] = (orderStatusCount[status] || 0) + 1;
        });

        this.charts.orderStatusDistribution = Object.entries(
          orderStatusCount,
        ).map(([name, value]) => ({ name, value }));

        // Lead status distribution (mock data for now)
        this.charts.leadStatusDistribution = [
          { name: "new", value: this.metrics.newLeads },
          {
            name: "contacted",
            value: Math.floor(this.metrics.totalLeads * 0.3),
          },
          {
            name: "qualified",
            value: Math.floor(this.metrics.totalLeads * 0.2),
          },
          { name: "closed", value: Math.floor(this.metrics.totalLeads * 0.1) },
        ];
      } catch (error) {
        console.error("Error fetching charts data:", error);
        throw error;
      }
    },

    async fetchRecentActivity() {
      try {
        // Fetch recent orders
        const ordersResponse = await axios.get(`${API_BASE}/orders/?limit=5`);
        this.recentActivity.recentOrders = ordersResponse.data;

        // Fetch recent parts
        const partsResponse = await axios.get(`${API_BASE}/parts/?limit=5`);
        this.recentActivity.recentParts = partsResponse.data;

        // Fetch recent categories
        const categoriesResponse = await axios.get(
          `${API_BASE}/categories/?limit=5`,
        );
        this.recentActivity.recentCategories = categoriesResponse.data;

        // Fetch recent leads (if available)
        try {
          const leadsResponse = await axios.get(`${API_BASE}/leads/?limit=5`);
          this.recentActivity.recentLeads = leadsResponse.data;
        } catch (error) {
          this.recentActivity.recentLeads = [];
        }
      } catch (error) {
        console.error("Error fetching recent activity:", error);
        throw error;
      }
    },

    async checkSystemHealth() {
      try {
        // Check API health by testing a known endpoint
        const startTime = Date.now();
        await axios.get(`${API_BASE}/categories/`);
        const responseTime = Date.now() - startTime;

        this.systemHealth.apiStatus =
          responseTime < 1000 ? "healthy" : "warning";

        // Check database health (same endpoint)
        this.systemHealth.databaseStatus = "healthy";

        // Bot status (mock for now - would need actual bot health endpoint)
        this.systemHealth.botStatus = "healthy";
      } catch (error) {
        this.systemHealth.apiStatus = "error";
        this.systemHealth.databaseStatus = "error";
        console.error("System health check failed:", error);
      }
    },

    // Helper method to generate time series data
    generateTimeSeriesData(type) {
      const data = [];
      const now = new Date();

      for (let i = 29; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);

        const value =
          type === "orders"
            ? Math.floor(Math.random() * 10) + 1
            : Math.floor(Math.random() * 5) + 1;

        data.push({
          date: date.toISOString().split("T")[0],
          value,
        });
      }

      return data;
    },

    // Refresh specific data
    async refreshMetrics() {
      await this.fetchMetrics();
    },

    async refreshCharts() {
      await this.fetchChartsData();
    },

    async refreshActivity() {
      await this.fetchRecentActivity();
    },

    async refreshHealth() {
      await this.checkSystemHealth();
    },

    // Get formatted metrics for display
    getFormattedMetric(metric, value) {
      switch (metric) {
        case "totalParts":
          return { value: value.toString(), label: "Parts", icon: "🔧" };
        case "totalVehicles":
          return { value: value.toString(), label: "Vehicles", icon: "🚗" };
        case "totalCategories":
          return { value: value.toString(), label: "Categories", icon: "📁" };
        case "totalOrders":
          return { value: value.toString(), label: "Orders", icon: "📦" };
        case "totalLeads":
          return { value: value.toString(), label: "Leads", icon: "👥" };
        case "activeParts":
          return { value: value.toString(), label: "Active Parts", icon: "✅" };
        case "pendingOrders":
          return {
            value: value.toString(),
            label: "Pending Orders",
            icon: "⏳",
          };
        case "newLeads":
          return { value: value.toString(), label: "New Leads", icon: "🆕" };
        default:
          return { value: value.toString(), label: metric, icon: "📊" };
      }
    },
  },
});
