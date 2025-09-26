import { defineStore } from "pinia";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const useOrdersStore = defineStore("orders", {
  state: () => ({
    orders: [],
    currentOrder: null,
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
      customerName: "",
      orderValue: "",
    },
    stats: {
      totalOrders: 0,
      pendingOrders: 0,
      completedOrders: 0,
      totalValue: 0,
      averageOrderValue: 0,
    },
  }),

  getters: {
    ordersCount: (state) => state.orders.length,

    // Get filtered orders based on current filters
    filteredOrders: (state) => {
      let filtered = state.orders;

      if (state.filters.search) {
        const search = state.filters.search.toLowerCase();
        filtered = filtered.filter(
          (order) =>
            order.id.toString().includes(search) ||
            order.status.toLowerCase().includes(search) ||
            (order.notes && order.notes.toLowerCase().includes(search)),
        );
      }

      if (state.filters.status) {
        filtered = filtered.filter(
          (order) => order.status === state.filters.status,
        );
      }

      if (state.filters.dateFrom) {
        filtered = filtered.filter(
          (order) =>
            new Date(order.created_at) >= new Date(state.filters.dateFrom),
        );
      }

      if (state.filters.dateTo) {
        filtered = filtered.filter(
          (order) =>
            new Date(order.created_at) <= new Date(state.filters.dateTo),
        );
      }

      return filtered;
    },

    // Get orders by status
    ordersByStatus: (state) => {
      const statusGroups = {};
      state.orders.forEach((order) => {
        if (!statusGroups[order.status]) {
          statusGroups[order.status] = [];
        }
        statusGroups[order.status].push(order);
      });
      return statusGroups;
    },

    // Get recent orders (last 7 days)
    recentOrders: (state) => {
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return state.orders.filter(
        (order) => new Date(order.created_at) >= weekAgo,
      );
    },

    // Get pending orders
    pendingOrders: (state) => {
      return state.orders.filter((order) =>
        ["new", "in_progress", "quoted"].includes(order.status),
      );
    },

    // Get completed orders
    completedOrders: (state) => {
      return state.orders.filter((order) =>
        ["won", "completed"].includes(order.status),
      );
    },
  },

  actions: {
    async fetchOrders(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const queryParams = new URLSearchParams({
          skip: ((params.page || 1) - 1) * (params.limit || 20),
          limit: params.limit || 20,
          ...params,
        });

        const response = await axios.get(`${API_BASE}/orders/?${queryParams}`);
        this.orders = response.data;
        this.pagination = {
          page: params.page || 1,
          limit: params.limit || 20,
          total: response.headers["x-total-count"] || 0,
          totalPages: Math.ceil(
            (response.headers["x-total-count"] || 0) / (params.limit || 20),
          ),
        };

        // Calculate stats
        this.calculateStats();
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch orders";
        console.error("Error fetching orders:", error);
      } finally {
        this.loading = false;
      }
    },

    async getOrder(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE}/orders/${id}`);
        this.currentOrder = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch order";
        console.error("Error fetching order:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateOrder(id, orderData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.put(`${API_BASE}/orders/${id}`, orderData);
        const index = this.orders.findIndex((order) => order.id === id);
        if (index !== -1) {
          this.orders[index] = response.data;
        }
        if (this.currentOrder && this.currentOrder.id === id) {
          this.currentOrder = response.data;
        }
        this.calculateStats();
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to update order";
        console.error("Error updating order:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateOrderStatus(id, status, notes = null) {
      const updateData = { status };
      if (notes) {
        updateData.notes = notes;
      }
      return await this.updateOrder(id, updateData);
    },

    async addOrderItem(orderId, itemData) {
      this.loading = true;
      this.error = null;
      try {
        // Get current order
        const order = await this.getOrder(orderId);

        // Add new item to the items array
        const newItem = {
          line_no: order.items.length + 1,
          ...itemData,
        };

        const updatedItems = [...order.items, newItem];

        const response = await axios.put(`${API_BASE}/orders/${orderId}`, {
          items: updatedItems,
        });

        // Update local state
        const index = this.orders.findIndex((o) => o.id === orderId);
        if (index !== -1) {
          this.orders[index] = response.data;
        }
        if (this.currentOrder && this.currentOrder.id === orderId) {
          this.currentOrder = response.data;
        }

        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to add order item";
        console.error("Error adding order item:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateOrderItem(orderId, lineNo, itemData) {
      this.loading = true;
      this.error = null;
      try {
        // Get current order
        const order = await this.getOrder(orderId);

        // Update the specific item
        const updatedItems = order.items.map((item) =>
          item.line_no === lineNo ? { ...item, ...itemData } : item,
        );

        const response = await axios.put(`${API_BASE}/orders/${orderId}`, {
          items: updatedItems,
        });

        // Update local state
        const index = this.orders.findIndex((o) => o.id === orderId);
        if (index !== -1) {
          this.orders[index] = response.data;
        }
        if (this.currentOrder && this.currentOrder.id === orderId) {
          this.currentOrder = response.data;
        }

        return response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to update order item";
        console.error("Error updating order item:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async removeOrderItem(orderId, lineNo) {
      this.loading = true;
      this.error = null;
      try {
        // Get current order
        const order = await this.getOrder(orderId);

        // Remove the item and renumber remaining items
        const updatedItems = order.items
          .filter((item) => item.line_no !== lineNo)
          .map((item, index) => ({ ...item, line_no: index + 1 }));

        const response = await axios.put(`${API_BASE}/orders/${orderId}`, {
          items: updatedItems,
        });

        // Update local state
        const index = this.orders.findIndex((o) => o.id === orderId);
        if (index !== -1) {
          this.orders[index] = response.data;
        }
        if (this.currentOrder && this.currentOrder.id === orderId) {
          this.currentOrder = response.data;
        }

        return response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to remove order item";
        console.error("Error removing order item:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async getOrderCustomer(orderId) {
      try {
        const order = await this.getOrder(orderId);
        if (order.lead_id) {
          const response = await axios.get(
            `${API_BASE}/leads/${order.lead_id}`,
          );
          return response.data;
        }
        return null;
      } catch (error) {
        console.error("Error fetching order customer:", error);
        return null;
      }
    },

    async getOrdersByCustomer(customerId) {
      try {
        const response = await axios.get(
          `${API_BASE}/orders/?lead_id=${customerId}`,
        );
        return response.data;
      } catch (error) {
        console.error("Error fetching customer orders:", error);
        return [];
      }
    },

    // Calculate order statistics
    calculateStats() {
      this.stats.totalOrders = this.orders.length;
      this.stats.pendingOrders = this.pendingOrders.length;
      this.stats.completedOrders = this.completedOrders.length;

      // Calculate total value (mock calculation - would need actual pricing)
      this.stats.totalValue = this.orders.reduce((total, order) => {
        return total + this.calculateOrderValue(order);
      }, 0);

      this.stats.averageOrderValue =
        this.stats.totalOrders > 0
          ? this.stats.totalValue / this.stats.totalOrders
          : 0;
    },

    // Calculate order value (mock implementation)
    calculateOrderValue(order) {
      // This would need to be implemented based on actual pricing data
      return order.items.reduce((total, item) => {
        return total + item.qty * 100; // Mock price of $100 per item
      }, 0);
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
        customerName: "",
        orderValue: "",
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
    setCurrentOrder(order) {
      this.currentOrder = order;
    },

    clearCurrentOrder() {
      this.currentOrder = null;
    },

    // Get status color for UI
    getStatusColor(status) {
      const colors = {
        new: "yellow",
        in_progress: "blue",
        quoted: "purple",
        won: "green",
        completed: "green",
        lost: "red",
        cancelled: "gray",
      };
      return colors[status] || "gray";
    },

    // Get status text for UI
    getStatusText(status) {
      const texts = {
        new: "New",
        in_progress: "In Progress",
        quoted: "Quoted",
        won: "Won",
        completed: "Completed",
        lost: "Lost",
        cancelled: "Cancelled",
      };
      return texts[status] || status;
    },
  },
});
