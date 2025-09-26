import { defineStore } from "pinia";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const useCategoriesStore = defineStore("categories", {
  state: () => ({
    categories: [],
    categoryTree: [],
    currentCategory: null,
    loading: false,
    error: null,
    expandedNodes: new Set(),
    selectedCategory: null,
  }),

  getters: {
    categoriesCount: (state) => state.categories.length,
    rootCategories: (state) => state.categories.filter((cat) => !cat.parent_id),
    activeCategories: (state) =>
      state.categories.filter((cat) => cat.is_active),

    // Get children of a specific category
    getChildren: (state) => (parentId) => {
      return state.categories.filter((cat) => cat.parent_id === parentId);
    },

    // Get category path (breadcrumb)
    getCategoryPath: (state) => (categoryId) => {
      const path = [];
      let current = state.categories.find((cat) => cat.id === categoryId);

      while (current) {
        path.unshift(current);
        current = current.parent_id
          ? state.categories.find((cat) => cat.id === current.parent_id)
          : null;
      }

      return path;
    },

    // Check if category has children
    hasChildren: (state) => (categoryId) => {
      return state.categories.some((cat) => cat.parent_id === categoryId);
    },

    // Get all descendants of a category
    getDescendants: (state) => (categoryId) => {
      const descendants = [];
      const children = state.categories.filter(
        (cat) => cat.parent_id === categoryId,
      );

      children.forEach((child) => {
        descendants.push(child);
        descendants.push(...state.getDescendants(child.id));
      });

      return descendants;
    },
  },

  actions: {
    async fetchCategories() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE}/categories/`);
        this.categories = response.data;
        this.buildCategoryTree();
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch categories";
        console.error("Error fetching categories:", error);
      } finally {
        this.loading = false;
      }
    },

    async fetchCategoryTree() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE}/categories/tree/`);
        this.categoryTree = response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch category tree";
        console.error("Error fetching category tree:", error);
      } finally {
        this.loading = false;
      }
    },

    async createCategory(categoryData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE}/categories`,
          categoryData,
        );
        this.categories.push(response.data);
        this.buildCategoryTree();
        return response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to create category";
        console.error("Error creating category:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateCategory(id, categoryData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.put(
          `${API_BASE}/categories/${id}`,
          categoryData,
        );
        const index = this.categories.findIndex((cat) => cat.id === id);
        if (index !== -1) {
          this.categories[index] = response.data;
        }
        this.buildCategoryTree();
        return response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to update category";
        console.error("Error updating category:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteCategory(id) {
      this.loading = true;
      this.error = null;
      try {
        await axios.delete(`${API_BASE}/categories/${id}`);
        this.categories = this.categories.filter((cat) => cat.id !== id);
        this.buildCategoryTree();
        return true;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to delete category";
        console.error("Error deleting category:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async getCategory(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE}/categories/${id}`);
        this.currentCategory = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch category";
        console.error("Error fetching category:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async getCategoryChildren(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(
          `${API_BASE}/categories/${id}/children`,
        );
        return response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch category children";
        console.error("Error fetching category children:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async getCategoryPath(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE}/categories/${id}/path`);
        return response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to fetch category path";
        console.error("Error fetching category path:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async searchCategories(query) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(
          `${API_BASE}/categories/search?q=${encodeURIComponent(query)}`,
        );
        return response.data;
      } catch (error) {
        this.error =
          error.response?.data?.detail || "Failed to search categories";
        console.error("Error searching categories:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Build category tree structure
    buildCategoryTree() {
      const categoryMap = new Map();
      const rootCategories = [];

      // Create a map of all categories
      this.categories.forEach((category) => {
        categoryMap.set(category.id, { ...category, children: [] });
      });

      // Build the tree structure
      this.categories.forEach((category) => {
        const categoryNode = categoryMap.get(category.id);
        if (category.parent_id && categoryMap.has(category.parent_id)) {
          categoryMap.get(category.parent_id).children.push(categoryNode);
        } else {
          rootCategories.push(categoryNode);
        }
      });

      this.categoryTree = rootCategories;
    },

    // Toggle node expansion in tree view
    toggleNodeExpansion(nodeId) {
      if (this.expandedNodes.has(nodeId)) {
        this.expandedNodes.delete(nodeId);
      } else {
        this.expandedNodes.add(nodeId);
      }
    },

    // Expand all nodes
    expandAll() {
      this.categories.forEach((cat) => {
        this.expandedNodes.add(cat.id);
      });
    },

    // Collapse all nodes
    collapseAll() {
      this.expandedNodes.clear();
    },

    // Set selected category
    setSelectedCategory(category) {
      this.selectedCategory = category;
    },

    // Clear selected category
    clearSelectedCategory() {
      this.selectedCategory = null;
    },
  },
});
