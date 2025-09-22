import { defineStore } from "pinia";
import axios from "axios";

const API_BASE = "http://localhost:8001/api/v1";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    token: localStorage.getItem("access_token"),
    isAuthenticated: false,
  }),

  actions: {
    async login(credentials) {
      try {
        const response = await axios.post(
          `${API_BASE}/users/login`,
          credentials,
        );

        if (response.data && response.data.access_token) {
          this.user = response.data.user;
          this.token = response.data.access_token;
          this.isAuthenticated = true;
          localStorage.setItem("access_token", this.token);
          return { success: true, user: this.user };
        } else {
          return { success: false, message: "Invalid response from server" };
        }
      } catch (error) {
        console.error("Login error:", error);
        const message = error.response?.data?.detail || "Login failed";
        return { success: false, message };
      }
    },

    async logout() {
      try {
        if (this.token) {
          await axios.post(
            `${API_BASE}/users/logout`,
            {},
            {
              headers: { Authorization: `Bearer ${this.token}` },
            },
          );
        }
      } catch (error) {
        console.error("Logout error:", error);
      } finally {
        this.user = null;
        this.token = null;
        this.isAuthenticated = false;
        localStorage.removeItem("access_token");
      }
    },

    async initializeAuth() {
      if (this.token) {
        try {
          const response = await axios.get(`${API_BASE}/users/me`, {
            headers: { Authorization: `Bearer ${this.token}` },
          });
          this.user = response.data;
          this.isAuthenticated = true;
        } catch (error) {
          console.error("Token validation failed:", error);
          this.logout();
        }
      }
    },
  },
});
