import { defineStore } from "pinia";
import { adminApi } from "@/api/client.js";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    token: localStorage.getItem("access_token"),
    isAuthenticated: false,
  }),

  actions: {
    async login(credentials) {
      try {
        console.log("Auth store: Starting login process");
        const response = await adminApi.login(credentials);
        console.log("Auth store: API response received:", response);

        if (response && response.access_token) {
          console.log("Auth store: Setting authentication state");
          this.user = response.user;
          this.token = response.access_token;
          this.isAuthenticated = true;
          localStorage.setItem("access_token", this.token);
          console.log("Auth store: Authentication state updated:", {
            isAuthenticated: this.isAuthenticated,
            user: this.user,
            hasToken: !!this.token,
          });
          return { success: true, user: this.user };
        } else {
          console.log("Auth store: Invalid response from server");
          return { success: false, message: "Invalid response from server" };
        }
      } catch (error) {
        console.error("Auth store: Login error:", error);
        const message = error.message || "Login failed";
        return { success: false, message };
      }
    },

    async logout() {
      try {
        console.log("Auth store: Starting logout process");
        if (this.token) {
          await adminApi.logout();
        }
      } catch (error) {
        console.error("Logout error:", error);
      } finally {
        console.log("Auth store: Clearing authentication state");
        this.user = null;
        this.token = null;
        this.isAuthenticated = false;
        localStorage.removeItem("access_token");
        console.log(
          "Auth store: Logout completed, authentication state cleared",
        );
      }
    },

    async initializeAuth() {
      console.log("Auth store: Initializing authentication");
      if (this.token) {
        try {
          console.log("Auth store: Validating existing token");
          const user = await adminApi.getCurrentUser();
          this.user = user;
          this.isAuthenticated = true;
          console.log(
            "Auth store: Token validation successful, user authenticated",
          );
        } catch (error) {
          console.error("Auth store: Token validation failed:", error);
          this.logout();
        }
      } else {
        console.log("Auth store: No token found, user not authenticated");
      }
    },
  },
});
