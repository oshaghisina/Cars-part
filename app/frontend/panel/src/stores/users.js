import { defineStore } from "pinia";
import axios from "axios";

const API_BASE = "http://localhost:8001/api/v1";

export const useUsersStore = defineStore("users", {
  state: () => ({
    users: [],
    loading: false,
    error: null,
    pagination: {
      currentPage: 1,
      pageSize: 20,
      totalItems: 0,
      totalPages: 0,
    },
    filters: {
      search: "",
      role: "",
      isActive: null,
    },
    statistics: {
      totalUsers: 0,
      activeUsers: 0,
      verifiedUsers: 0,
      recentLogins: 0,
      roleDistribution: {},
    },
    currentUser: null,
  }),

  getters: {
    getUserById: (state) => (id) => {
      return state.users.find((user) => user.id === id);
    },
    getUsersByRole: (state) => (role) => {
      return state.users.filter((user) => user.role === role);
    },
    filteredUsers: (state) => {
      let filtered = state.users;

      if (state.filters.search) {
        const search = state.filters.search.toLowerCase();
        filtered = filtered.filter(
          (user) =>
            user.username.toLowerCase().includes(search) ||
            user.email.toLowerCase().includes(search) ||
            user.first_name.toLowerCase().includes(search) ||
            user.last_name.toLowerCase().includes(search),
        );
      }

      if (state.filters.role) {
        filtered = filtered.filter((user) => user.role === state.filters.role);
      }

      if (state.filters.isActive !== null) {
        filtered = filtered.filter(
          (user) => user.is_active === state.filters.isActive,
        );
      }

      return filtered;
    },
    getPaginatedUsers: (state) => {
      const startIndex =
        (state.pagination.currentPage - 1) * state.pagination.pageSize;
      const endIndex = startIndex + state.pagination.pageSize;
      return state.filteredUsers.slice(startIndex, endIndex);
    },
  },

  actions: {
    async fetchUsers() {
      this.loading = true;
      this.error = null;
      try {
        const token = localStorage.getItem("access_token");
        const params = {
          skip: (this.pagination.currentPage - 1) * this.pagination.pageSize,
          limit: this.pagination.pageSize,
          search: this.filters.search || undefined,
        };
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const response = await axios.get(`${API_BASE}/users/`, {
          params,
          headers,
        });
        this.users = response.data.users;
        this.pagination.totalItems = response.data.total;
        this.pagination.totalPages = response.data.total_pages;
      } catch (error) {
        this.error = `Failed to fetch users: ${error.message}`;
        console.error("Error fetching users:", error);
      } finally {
        this.loading = false;
      }
    },

    async fetchUserById(id) {
      this.loading = true;
      this.error = null;
      try {
        const token = localStorage.getItem("access_token");
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const response = await axios.get(`${API_BASE}/users/${id}`, {
          headers,
        });
        return response.data;
      } catch (error) {
        this.error = `Failed to fetch user ${id}: ${error.message}`;
        console.error(`Error fetching user ${id}:`, error);
        return null;
      } finally {
        this.loading = false;
      }
    },

    async createUser(userData) {
      this.loading = true;
      this.error = null;
      try {
        const token = localStorage.getItem("access_token");
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const response = await axios.post(`${API_BASE}/users/`, userData, {
          headers,
        });
        this.fetchUsers(); // Refresh list
        return response.data;
      } catch (error) {
        this.error = `Failed to create user: ${error.message}`;
        console.error("Error creating user:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateUser(id, userData) {
      this.loading = true;
      this.error = null;
      try {
        const token = localStorage.getItem("access_token");
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const response = await axios.put(`${API_BASE}/users/${id}`, userData, {
          headers,
        });
        this.fetchUsers(); // Refresh list
        return response.data;
      } catch (error) {
        this.error = `Failed to update user ${id}: ${error.message}`;
        console.error(`Error updating user ${id}:`, error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteUser(id) {
      this.loading = true;
      this.error = null;
      try {
        const token = localStorage.getItem("access_token");
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        await axios.delete(`${API_BASE}/users/${id}`, { headers });
        this.fetchUsers(); // Refresh list
      } catch (error) {
        this.error = `Failed to delete user ${id}: ${error.message}`;
        console.error(`Error deleting user ${id}:`, error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchUserStatistics() {
      try {
        const token = localStorage.getItem("access_token");
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const response = await axios.get(
          `${API_BASE}/users/statistics/overview`,
          { headers },
        );
        this.statistics = response.data;
      } catch (error) {
        console.error("Error fetching user statistics:", error);
      }
    },

    async login(credentials) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE}/users/login`,
          credentials,
        );
        this.currentUser = response.data.user;

        // Store token in localStorage
        localStorage.setItem("access_token", response.data.access_token);

        return response.data;
      } catch (error) {
        this.error = `Login failed: ${error.message}`;
        console.error("Login error:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        const token = localStorage.getItem("access_token");
        if (token) {
          await axios.post(
            `${API_BASE}/users/logout`,
            {},
            {
              headers: { Authorization: `Bearer ${token}` },
            },
          );
        }
      } catch (error) {
        console.error("Logout error:", error);
      } finally {
        this.currentUser = null;
        localStorage.removeItem("access_token");
      }
    },

    async getCurrentUser() {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) return null;

        const response = await axios.get(`${API_BASE}/users/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.currentUser = response.data;
        return response.data;
      } catch (error) {
        console.error("Error getting current user:", error);
        this.logout(); // Clear invalid token
        return null;
      }
    },

    async changePassword(passwordData) {
      this.loading = true;
      this.error = null;
      try {
        const token = localStorage.getItem("access_token");
        const response = await axios.post(
          `${API_BASE}/users/change-password`,
          passwordData,
          {
            headers: { Authorization: `Bearer ${token}` },
          },
        );
        return response.data;
      } catch (error) {
        this.error = `Failed to change password: ${error.message}`;
        console.error("Error changing password:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    setCurrentPage(page) {
      if (page > 0 && page <= this.pagination.totalPages) {
        this.pagination.currentPage = page;
        this.fetchUsers();
      }
    },

    setPageSize(size) {
      this.pagination.pageSize = size;
      this.pagination.currentPage = 1; // Reset to first page
      this.fetchUsers();
    },

    setFilter(key, value) {
      this.filters[key] = value;
      this.pagination.currentPage = 1; // Reset to first page on filter change
      this.fetchUsers();
    },

    clearFilters() {
      this.filters = {
        search: "",
        role: "",
        isActive: null,
      };
      this.pagination.currentPage = 1;
      this.fetchUsers();
    },

    // Role management
    async assignRoleToUser(userId, roleName) {
      try {
        const token = localStorage.getItem("access_token");
        await axios.post(
          `${API_BASE}/users/${userId}/roles/${roleName}`,
          {},
          {
            headers: { Authorization: `Bearer ${token}` },
          },
        );
        this.fetchUsers(); // Refresh list
      } catch (error) {
        this.error = `Failed to assign role: ${error.message}`;
        console.error("Error assigning role:", error);
        throw error;
      }
    },

    async removeRoleFromUser(userId, roleName) {
      try {
        const token = localStorage.getItem("access_token");
        await axios.delete(`${API_BASE}/users/${userId}/roles/${roleName}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.fetchUsers(); // Refresh list
      } catch (error) {
        this.error = `Failed to remove role: ${error.message}`;
        console.error("Error removing role:", error);
        throw error;
      }
    },

    // Utility methods
    getRoleDisplayName(role) {
      const roleNames = {
        super_admin: "Super Admin",
        admin: "Admin",
        manager: "Manager",
        user: "User",
      };
      return roleNames[role] || role;
    },

    getRoleColor(role) {
      const roleColors = {
        super_admin: "red",
        admin: "blue",
        manager: "green",
        user: "gray",
      };
      return roleColors[role] || "gray";
    },

    isUserActive(user) {
      return user.is_active && !user.is_locked();
    },

    formatLastLogin(lastLogin) {
      if (!lastLogin) return "Never";
      return new Date(lastLogin).toLocaleDateString();
    },
  },
});
