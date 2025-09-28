import { defineStore } from "pinia";

import apiClient, { partsApi } from "../api/partsApi";

const sanitizeParams = (params) =>
  Object.fromEntries(
    Object.entries(params).filter(([, value]) => {
      if (value === null || value === undefined) return false;
      if (typeof value === "string" && value.trim() === "") return false;
      return true;
    }),
  );

const normalizeStatusFilter = (isActive) => {
  if (isActive === null || isActive === undefined) {
    return undefined;
  }
  return isActive ? "active" : "inactive";
};

export const usePartsStore = defineStore("parts", {
  state: () => ({
    parts: [],
    currentPart: null,
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
      category: "",
      brand: "",
      model: "",
      trim: "",
      priceMin: "",
      priceMax: "",
      isActive: null,
    },
  }),

  getters: {
    partsCount: (state) => state.parts.length,
    activeParts: (state) => state.parts.filter((part) => part.is_active),
    partsByCategory: (state) => (categoryId) =>
      state.parts.filter((part) => part.category_id === categoryId),
    partsByVehicle: (state) => (brandId, modelId, trimId) => {
      return state.parts.filter((part) => {
        if (brandId && part.brand_id !== brandId) return false;
        if (modelId && part.model_id !== modelId) return false;
        if (trimId && part.trim_id !== trimId) return false;
        return true;
      });
    },

    // Get filtered parts based on current filters
    filteredParts: (state) => {
      let filtered = state.parts;

      if (state.filters.search) {
        const search = state.filters.search.toLowerCase();
        filtered = filtered.filter(
          (part) =>
            part.part_name.toLowerCase().includes(search) ||
            (part.brand_oem && part.brand_oem.toLowerCase().includes(search)) ||
            (part.oem_code && part.oem_code.toLowerCase().includes(search)) ||
            (part.category && part.category.toLowerCase().includes(search)) ||
            (part.subcategory &&
              part.subcategory.toLowerCase().includes(search)),
        );
      }

      if (state.filters.category) {
        filtered = filtered.filter(
          (part) => part.category === state.filters.category,
        );
      }

      if (state.filters.brand) {
        filtered = filtered.filter(
          (part) => part.vehicle_make === state.filters.brand,
        );
      }

      if (state.filters.model) {
        filtered = filtered.filter(
          (part) => part.vehicle_model === state.filters.model,
        );
      }

      if (state.filters.trim) {
        filtered = filtered.filter(
          (part) => part.vehicle_trim === state.filters.trim,
        );
      }

      if (state.filters.isActive !== null) {
        const activeStatus = state.filters.isActive ? "active" : "inactive";
        filtered = filtered.filter((part) => part.status === activeStatus);
      }

      return filtered;
    },
  },

  actions: {
    async fetchParts(overrides = {}) {
      this.loading = true;
      this.error = null;

      const page = overrides.page || this.pagination.page || 1;
      const limit = overrides.limit || this.pagination.limit || 20;

      const baseFilters = {
        search: Object.prototype.hasOwnProperty.call(overrides, "search")
          ? overrides.search
          : this.filters.search,
        category: Object.prototype.hasOwnProperty.call(overrides, "category")
          ? overrides.category
          : this.filters.category,
        brand: Object.prototype.hasOwnProperty.call(overrides, "brand")
          ? overrides.brand
          : this.filters.brand,
        model: Object.prototype.hasOwnProperty.call(overrides, "model")
          ? overrides.model
          : this.filters.model,
        trim: Object.prototype.hasOwnProperty.call(overrides, "trim")
          ? overrides.trim
          : this.filters.trim,
        price_min: Object.prototype.hasOwnProperty.call(overrides, "price_min")
          ? overrides.price_min
          : this.filters.priceMin,
        price_max: Object.prototype.hasOwnProperty.call(overrides, "price_max")
          ? overrides.price_max
          : this.filters.priceMax,
      };

      const statusOverride = Object.prototype.hasOwnProperty.call(
        overrides,
        "status",
      )
        ? overrides.status
        : normalizeStatusFilter(this.filters.isActive);

      const additionalParams = sanitizeParams({ ...overrides });
      delete additionalParams.page;
      delete additionalParams.limit;
      delete additionalParams.search;
      delete additionalParams.category;
      delete additionalParams.brand;
      delete additionalParams.model;
      delete additionalParams.trim;
      delete additionalParams.price_min;
      delete additionalParams.price_max;
      delete additionalParams.status;

      const query = sanitizeParams({
        page,
        limit,
        ...baseFilters,
        status: statusOverride,
        ...additionalParams,
      });

      try {
        const response = await apiClient.get("/admin/parts", { params: query });

        let items = [];
        if (Array.isArray(response.data?.items)) {
          items = response.data.items;
        } else if (Array.isArray(response.data?.results)) {
          items = response.data.results;
        } else if (Array.isArray(response.data?.data)) {
          items = response.data.data;
        } else if (Array.isArray(response.data)) {
          items = response.data;
        }

        const totalFromBody =
          response.data?.pagination?.total ?? response.data?.total ?? null;
        const totalFromHeader = response.headers?.["x-total-count"] ?? null;
        const computedTotal = Number(
          totalFromBody ?? totalFromHeader ?? items.length ?? 0,
        );
        const total = Number.isFinite(computedTotal)
          ? computedTotal
          : items.length || 0;

        const resolvedPage = Number(response.data?.page ?? page) || page;
        const resolvedLimit = Number(response.data?.per_page ?? limit) || limit;

        this.parts = items;
        this.pagination = {
          page: resolvedPage,
          limit: resolvedLimit,
          total,
          totalPages: total
            ? Math.max(1, Math.ceil(total / resolvedLimit))
            : 1,
        };
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch parts";
        console.error("Error fetching parts:", error);
      } finally {
        this.loading = false;
      }
    },

    async createPart(partData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await partsApi.createPart(partData);
        if (response) {
          this.parts.unshift(response);
        }
        return response;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to create part";
        console.error("Error creating part:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updatePart(id, partData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await partsApi.updatePart(id, partData);
        const index = this.parts.findIndex((part) => part.id === id);
        if (index !== -1 && response) {
          this.parts[index] = response;
        }
        return response;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to update part";
        console.error("Error updating part:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deletePart(id) {
      this.loading = true;
      this.error = null;
      try {
        await partsApi.deletePart(id);
        this.parts = this.parts.filter((part) => part.id !== id);
        return true;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to delete part";
        console.error("Error deleting part:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async getPart(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await partsApi.getPart(id);
        this.currentPart = response;
        return response;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch part";
        console.error("Error fetching part:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async searchParts(query) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get("/admin/parts", {
          params: sanitizeParams({ search: query, limit: 50 }),
        });
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to search parts";
        console.error("Error searching parts:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async getPartsByCategory(categoryId) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get("/admin/parts", {
          params: sanitizeParams({ category_id: categoryId, limit: 100 }),
        });
        return response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch parts by category";
        console.error("Error fetching parts by category:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async getPartsByVehicle(brandId, modelId = null, trimId = null) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get("/admin/parts", {
          params: sanitizeParams({
            brand_id: brandId,
            model_id: modelId,
            trim_id: trimId,
          }),
        });
        return response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch parts by vehicle";
        console.error("Error fetching parts by vehicle:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Filter actions
    setFilter(key, value) {
      this.filters[key] = value;
      this.pagination.page = 1; // Reset to first page when filtering
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters };
      this.pagination.page = 1;
    },

    clearFilters() {
      this.filters = {
        search: "",
        category: "",
        brand: "",
        model: "",
        trim: "",
        priceMin: "",
        priceMax: "",
        isActive: null,
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
    setCurrentPart(part) {
      this.currentPart = part;
    },

    clearCurrentPart() {
      this.currentPart = null;
    },
  },
});
