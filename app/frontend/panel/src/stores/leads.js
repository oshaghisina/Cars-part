import { defineStore } from "pinia";
import axios from "axios";

const API_BASE = "http://localhost:8001/api/v1";

export const useLeadsStore = defineStore("leads", {
  state: () => ({
    leads: [],
    currentLead: null,
    loading: false,
    error: null,
    pagination: {
      page: 1,
      limit: 20,
      total: 0,
      totalPages: 0,
    },
    filters: {
      search: "",
      status: "",
      dateFrom: "",
      dateTo: "",
      city: "",
      hasOrders: null, // null for all, true for leads with orders, false for leads without orders
    },
    stats: {
      totalLeads: 0,
      newLeads: 0,
      activeLeads: 0,
      convertedLeads: 0,
      totalOrders: 0,
      conversionRate: 0,
      averageOrderValue: 0,
    },
  }),

  getters: {
    leadsCount: (state) => state.leads.length,

    // Get filtered leads based on current filters
    filteredLeads: (state) => {
      let filtered = state.leads;

      if (state.filters.search) {
        const search = state.filters.search.toLowerCase();
        filtered = filtered.filter(
          (lead) =>
            lead.first_name?.toLowerCase().includes(search) ||
            lead.last_name?.toLowerCase().includes(search) ||
            lead.phone_e164?.toLowerCase().includes(search) ||
            lead.telegram_user_id?.toLowerCase().includes(search) ||
            lead.city?.toLowerCase().includes(search) ||
            lead.notes?.toLowerCase().includes(search),
        );
      }

      if (state.filters.city) {
        filtered = filtered.filter((lead) => lead.city === state.filters.city);
      }

      if (state.filters.dateFrom) {
        filtered = filtered.filter(
          (lead) =>
            new Date(lead.created_at) >= new Date(state.filters.dateFrom),
        );
      }

      if (state.filters.dateTo) {
        filtered = filtered.filter(
          (lead) => new Date(lead.created_at) <= new Date(state.filters.dateTo),
        );
      }

      return filtered;
    },

    // Get leads by status (mock status based on orders)
    leadsByStatus: (state) => {
      const statusGroups = {
        new: [],
        active: [],
        converted: [],
        inactive: [],
      };

      state.leads.forEach((lead) => {
        // Mock status logic - would be based on actual lead status field
        if (lead.orders && lead.orders.length > 0) {
          statusGroups.converted.push(lead);
        } else if (
          new Date(lead.created_at) >
          new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        ) {
          statusGroups.new.push(lead);
        } else {
          statusGroups.active.push(lead);
        }
      });

      return statusGroups;
    },

    // Get recent leads (last 7 days)
    recentLeads: (state) => {
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return state.leads.filter((lead) => new Date(lead.created_at) >= weekAgo);
    },

    // Get leads with orders
    leadsWithOrders: (state) => {
      return state.leads.filter(
        (lead) => lead.orders && lead.orders.length > 0,
      );
    },

    // Get leads without orders
    leadsWithoutOrders: (state) => {
      return state.leads.filter(
        (lead) => !lead.orders || lead.orders.length === 0,
      );
    },

    // Get unique cities
    uniqueCities: (state) => {
      const cities = state.leads
        .map((lead) => lead.city)
        .filter((city) => city && city.trim() !== "")
        .filter((city, index, self) => self.indexOf(city) === index);
      return cities.sort();
    },
  },

  actions: {
    async fetchLeads(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const queryParams = new URLSearchParams({
          skip: ((params.page || 1) - 1) * (params.limit || 20),
          limit: params.limit || 20,
          ...params,
        });

        const response = await axios.get(`${API_BASE}/leads/?${queryParams}`);
        this.leads = response.data;

        // Fetch orders for each lead to determine status
        await this.fetchLeadOrders();

        this.pagination = {
          page: params.page || 1,
          limit: params.limit || 20,
          total: response.headers["x-total-count"] || response.data.length,
          totalPages: Math.ceil(
            (response.headers["x-total-count"] || response.data.length) /
              (params.limit || 20),
          ),
        };

        // Calculate stats
        this.calculateStats();
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch leads";
        console.error("Error fetching leads:", error);
      } finally {
        this.loading = false;
      }
    },

    async getLead(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE}/leads/${id}`);
        this.currentLead = response.data;

        // Fetch orders for this lead
        if (response.data.id) {
          await this.fetchLeadOrders(response.data.id);
        }

        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch lead";
        console.error("Error fetching lead:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async createLead(leadData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(`${API_BASE}/leads/`, leadData);
        this.leads.push(response.data);
        this.calculateStats();
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to create lead";
        console.error("Error creating lead:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateLead(id, leadData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.put(`${API_BASE}/leads/${id}`, leadData);
        const index = this.leads.findIndex((lead) => lead.id === id);
        if (index !== -1) {
          this.leads[index] = response.data;
        }
        if (this.currentLead && this.currentLead.id === id) {
          this.currentLead = response.data;
        }
        this.calculateStats();
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to update lead";
        console.error("Error updating lead:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteLead(id) {
      this.loading = true;
      this.error = null;
      try {
        await axios.delete(`${API_BASE}/leads/${id}`);
        this.leads = this.leads.filter((lead) => lead.id !== id);
        if (this.currentLead && this.currentLead.id === id) {
          this.currentLead = null;
        }
        this.calculateStats();
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to delete lead";
        console.error("Error deleting lead:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchLeadOrders(leadId = null) {
      try {
        if (leadId) {
          // Fetch orders for a specific lead
          const response = await axios.get(
            `${API_BASE}/orders/?lead_id=${leadId}`,
          );
          const lead = this.leads.find((l) => l.id === leadId);
          if (lead) {
            lead.orders = response.data;
          }
          if (this.currentLead && this.currentLead.id === leadId) {
            this.currentLead.orders = response.data;
          }
        } else {
          // Fetch orders for all leads
          const response = await axios.get(`${API_BASE}/orders/`);
          const orders = response.data;

          // Group orders by lead_id
          const ordersByLead = {};
          orders.forEach((order) => {
            if (order.lead_id) {
              if (!ordersByLead[order.lead_id]) {
                ordersByLead[order.lead_id] = [];
              }
              ordersByLead[order.lead_id].push(order);
            }
          });

          // Assign orders to leads
          this.leads.forEach((lead) => {
            lead.orders = ordersByLead[lead.id] || [];
          });
        }
      } catch (error) {
        console.error("Error fetching lead orders:", error);
      }
    },

    async getLeadOrders(leadId) {
      try {
        const response = await axios.get(
          `${API_BASE}/orders/?lead_id=${leadId}`,
        );
        return response.data;
      } catch (error) {
        console.error("Error fetching lead orders:", error);
        return [];
      }
    },

    // Calculate lead statistics
    calculateStats() {
      this.stats.totalLeads = this.leads.length;

      // Calculate status-based stats
      const statusGroups = this.leadsByStatus;
      this.stats.newLeads = statusGroups.new.length;
      this.stats.activeLeads = statusGroups.active.length;
      this.stats.convertedLeads = statusGroups.converted.length;

      // Calculate conversion rate
      this.stats.conversionRate =
        this.stats.totalLeads > 0
          ? (this.stats.convertedLeads / this.stats.totalLeads) * 100
          : 0;

      // Calculate total orders and average order value
      const totalOrders = this.leads.reduce(
        (total, lead) => total + (lead.orders?.length || 0),
        0,
      );
      this.stats.totalOrders = totalOrders;

      // Mock average order value calculation
      this.stats.averageOrderValue = totalOrders > 0 ? 150 : 0; // Mock value
    },

    // Filter actions
    setFilter(key, value) {
      this.filters[key] = value;
      this.pagination.page = 1;
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters };
      this.pagination.page = 1;
    },

    clearFilters() {
      this.filters = {
        search: "",
        status: "",
        dateFrom: "",
        dateTo: "",
        city: "",
        hasOrders: null,
      };
      this.pagination.page = 1;
    },

    // Pagination actions
    setPage(page) {
      this.pagination.page = page;
    },

    setLimit(limit) {
      this.pagination.limit = limit;
      this.pagination.page = 1;
    },

    // Utility actions
    setCurrentLead(lead) {
      this.currentLead = lead;
    },

    clearCurrentLead() {
      this.currentLead = null;
    },

    // Get lead status based on orders and activity
    getLeadStatus(lead) {
      if (lead.orders && lead.orders.length > 0) {
        return "converted";
      } else if (
        new Date(lead.created_at) >
        new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      ) {
        return "new";
      } else if (
        new Date(lead.created_at) >
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      ) {
        return "active";
      } else {
        return "inactive";
      }
    },

    // Get status color for UI
    getStatusColor(status) {
      const colors = {
        new: "green",
        active: "blue",
        converted: "purple",
        inactive: "gray",
      };
      return colors[status] || "gray";
    },

    // Get status text for UI
    getStatusText(status) {
      const texts = {
        new: "New",
        active: "Active",
        converted: "Converted",
        inactive: "Inactive",
      };
      return texts[status] || status;
    },

    // Get full name
    getFullName(lead) {
      const firstName = lead.first_name || "";
      const lastName = lead.last_name || "";
      return `${firstName} ${lastName}`.trim() || "Unknown Customer";
    },

    // Get display phone
    getDisplayPhone(phone) {
      return phone || "Not provided";
    },

    // Get display city
    getDisplayCity(city) {
      return city || "Not specified";
    },

    // Get lead summary
    getLeadSummary(lead) {
      const orders = lead.orders || [];
      const totalOrders = orders.length;
      const totalValue = orders.reduce((total, order) => {
        return total + this.calculateOrderValue(order);
      }, 0);

      return {
        totalOrders,
        totalValue,
        lastOrderDate:
          orders.length > 0 ? orders[orders.length - 1].created_at : null,
        status: this.getLeadStatus(lead),
      };
    },

    // Calculate order value (mock implementation)
    calculateOrderValue(order) {
      return (
        order.items?.reduce((total, item) => {
          return total + item.qty * 100; // Mock price of $100 per item
        }, 0) || 0
      );
    },

    // Export leads data
    exportLeads(format = "csv") {
      const data = this.filteredLeads.map((lead) => ({
        id: lead.id,
        name: this.getFullName(lead),
        phone: lead.phone_e164,
        city: lead.city,
        telegram_id: lead.telegram_user_id,
        status: this.getLeadStatus(lead),
        orders_count: lead.orders?.length || 0,
        created_at: lead.created_at,
      }));

      if (format === "csv") {
        const csvContent = this.convertToCSV(data);
        this.downloadFile(csvContent, "leads.csv", "text/csv");
      }

      return data;
    },

    // Convert data to CSV
    convertToCSV(data) {
      if (data.length === 0) return "";

      const headers = Object.keys(data[0]);
      const csvRows = [
        headers.join(","),
        ...data.map((row) =>
          headers.map((header) => `"${row[header] || ""}"`).join(","),
        ),
      ];

      return csvRows.join("\n");
    },

    // Download file
    downloadFile(content, filename, mimeType) {
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    },
  },
});
