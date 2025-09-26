import { defineStore } from "pinia";
import axios from "axios";

import { API_BASE_URL } from "../api/baseUrl";

const API_BASE = API_BASE_URL;

export const useVehicleBrandsStore = defineStore("vehicleBrands", {
  state: () => ({
    brands: [],
    loading: false,
    error: null,
    currentBrand: null,
  }),

  getters: {
    brandsCount: (state) => state.brands.length,
    activeBrands: (state) => state.brands.filter((brand) => brand.is_active),
    brandsWithModels: (state) =>
      state.brands.filter((brand) => brand.models && brand.models.length > 0),
  },

  actions: {
    async fetchBrands() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE}/vehicles/brands`);
        this.brands = response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch brands";
        console.error("Error fetching brands:", error);
      } finally {
        this.loading = false;
      }
    },

    async createBrand(brandData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE}/vehicles/brands`,
          brandData,
        );
        this.brands.push(response.data);
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to create brand";
        console.error("Error creating brand:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateBrand(id, brandData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.put(
          `${API_BASE}/vehicles/brands/${id}`,
          brandData,
        );
        const index = this.brands.findIndex((brand) => brand.id === id);
        if (index !== -1) {
          this.brands[index] = response.data;
        }
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to update brand";
        console.error("Error updating brand:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteBrand(id) {
      this.loading = true;
      this.error = null;
      try {
        await axios.delete(`${API_BASE}/vehicles/brands/${id}`);
        this.brands = this.brands.filter((brand) => brand.id !== id);
        return true;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to delete brand";
        console.error("Error deleting brand:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async getBrand(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE}/vehicles/brands/${id}`);
        this.currentBrand = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch brand";
        console.error("Error fetching brand:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});

export const useVehicleModelsStore = defineStore("vehicleModels", {
  state: () => ({
    models: [],
    loading: false,
    error: null,
    currentModel: null,
  }),

  getters: {
    modelsCount: (state) => state.models.length,
    activeModels: (state) => state.models.filter((model) => model.is_active),
    modelsByBrand: (state) => (brandId) =>
      state.models.filter((model) => model.brand_id === brandId),
  },

  actions: {
    async fetchModels(brandId = null) {
      this.loading = true;
      this.error = null;
      try {
        const url = brandId
          ? `${API_BASE}/vehicles/brands/${brandId}/models`
          : `${API_BASE}/vehicles/models`;
        const response = await axios.get(url);
        this.models = response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch models";
        console.error("Error fetching models:", error);
      } finally {
        this.loading = false;
      }
    },

    async createModel(modelData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE}/vehicles/models`,
          modelData,
        );
        this.models.push(response.data);
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to create model";
        console.error("Error creating model:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateModel(id, modelData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.put(
          `${API_BASE}/vehicles/models/${id}`,
          modelData,
        );
        const index = this.models.findIndex((model) => model.id === id);
        if (index !== -1) {
          this.models[index] = response.data;
        }
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to update model";
        console.error("Error updating model:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteModel(id) {
      this.loading = true;
      this.error = null;
      try {
        await axios.delete(`${API_BASE}/vehicles/models/${id}`);
        this.models = this.models.filter((model) => model.id !== id);
        return true;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to delete model";
        console.error("Error deleting model:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async getModel(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE}/vehicles/models/${id}`);
        this.currentModel = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch model";
        console.error("Error fetching model:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});

export const useVehicleTrimsStore = defineStore("vehicleTrims", {
  state: () => ({
    trims: [],
    loading: false,
    error: null,
    currentTrim: null,
  }),

  getters: {
    trimsCount: (state) => state.trims.length,
    activeTrims: (state) => state.trims.filter((trim) => trim.is_active),
    trimsByModel: (state) => (modelId) =>
      state.trims.filter((trim) => trim.model_id === modelId),
  },

  actions: {
    async fetchTrims(modelId = null) {
      this.loading = true;
      this.error = null;
      try {
        const url = modelId
          ? `${API_BASE}/vehicles/models/${modelId}/trims`
          : `${API_BASE}/vehicles/trims`;
        const response = await axios.get(url);
        this.trims = response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch trims";
        console.error("Error fetching trims:", error);
      } finally {
        this.loading = false;
      }
    },

    async createTrim(trimData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE}/vehicles/trims`,
          trimData,
        );
        this.trims.push(response.data);
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to create trim";
        console.error("Error creating trim:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateTrim(id, trimData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.put(
          `${API_BASE}/vehicles/trims/${id}`,
          trimData,
        );
        const index = this.trims.findIndex((trim) => trim.id === id);
        if (index !== -1) {
          this.trims[index] = response.data;
        }
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to update trim";
        console.error("Error updating trim:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteTrim(id) {
      this.loading = true;
      this.error = null;
      try {
        await axios.delete(`${API_BASE}/vehicles/trims/${id}`);
        this.trims = this.trims.filter((trim) => trim.id !== id);
        return true;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to delete trim";
        console.error("Error deleting trim:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async getTrim(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE}/vehicles/trims/${id}`);
        this.currentTrim = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch trim";
        console.error("Error fetching trim:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});
