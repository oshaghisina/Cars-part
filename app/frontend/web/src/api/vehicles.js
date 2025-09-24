/**
 * API client for vehicle-related endpoints
 * Provides methods to fetch brands, models, trims, and perform vehicle operations
 */

import axios from 'axios';
import { API_CONFIG, ENDPOINTS } from '../config/api.js';

class VehicleApiClient {
  constructor() {
    this.http = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: API_CONFIG.DEFAULT_HEADERS
    });
  }

  /**
   * Get all vehicle brands with filtering options
   * @param {Object} options - Filter options
   * @param {string} options.country - Filter by country
   * @param {string} options.search - Search brands by name
   * @param {boolean} options.active_only - Show only active brands
   * @returns {Promise<Array>} List of vehicle brands
   */
  async getBrands(options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.country) params.append('country', options.country);
      if (options.search) params.append('search', options.search);
      if (options.active_only !== undefined) params.append('active_only', options.active_only);

      const response = await this.http.get(`${ENDPOINTS.VEHICLES_ENHANCED.BRANDS}?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicle brands:', error);
      throw error;
    }
  }

  /**
   * Get all models for a specific brand
   * @param {number} brandId - Brand ID
   * @param {Object} options - Filter options
   * @param {string} options.search - Search models by name
   * @param {string} options.body_type - Filter by body type
   * @param {boolean} options.active_only - Show only active models
   * @returns {Promise<Array>} List of vehicle models
   */
  async getBrandModels(brandId, options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.search) params.append('search', options.search);
      if (options.body_type) params.append('body_type', options.body_type);
      if (options.active_only !== undefined) params.append('active_only', options.active_only);

      const response = await this.http.get(
        `${ENDPOINTS.VEHICLES_ENHANCED.BRAND_MODELS(brandId)}?${params}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicle models:', error);
      throw error;
    }
  }

  /**
   * Get all trims for a specific model
   * @param {number} modelId - Model ID
   * @param {Object} options - Filter options
   * @param {number} options.year - Filter by year
   * @param {string} options.engine_type - Filter by engine type
   * @param {string} options.fuel_type - Filter by fuel type
   * @param {string} options.transmission - Filter by transmission
   * @param {boolean} options.active_only - Show only active trims
   * @returns {Promise<Array>} List of vehicle trims
   */
  async getModelTrims(modelId, options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.year) params.append('year', options.year);
      if (options.engine_type) params.append('engine_type', options.engine_type);
      if (options.fuel_type) params.append('fuel_type', options.fuel_type);
      if (options.transmission) params.append('transmission', options.transmission);
      if (options.active_only !== undefined) params.append('active_only', options.active_only);

      const response = await this.http.get(
        `${ENDPOINTS.VEHICLES_ENHANCED.MODEL_TRIMS(modelId)}?${params}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicle trims:', error);
      throw error;
    }
  }

  /**
   * Search vehicles with multiple criteria
   * @param {Object} searchRequest - Search criteria
   * @param {string} searchRequest.make - Vehicle make/brand name
   * @param {string} searchRequest.model - Vehicle model name
   * @param {number} searchRequest.year - Vehicle year
   * @param {string} searchRequest.engine_code - Engine code
   * @param {string} searchRequest.body_type - Body type
   * @param {string} searchRequest.fuel_type - Fuel type
   * @param {number} searchRequest.limit - Maximum results to return
   * @returns {Promise<Object>} Search results with vehicles and metadata
   */
  async searchVehicles(searchRequest) {
    try {
      const response = await this.http.post(ENDPOINTS.VEHICLES_ENHANCED.SEARCH, searchRequest);
      return response.data;
    } catch (error) {
      console.error('Error searching vehicles:', error);
      throw error;
    }
  }

  /**
   * Decode VIN to extract vehicle information
   * @param {string} vin - Vehicle Identification Number
   * @returns {Promise<Object>} Decoded VIN information with matching vehicles
   */
  async decodeVIN(vin) {
    try {
      const response = await this.http.post(ENDPOINTS.VEHICLES_ENHANCED.DECODE_VIN, { vin });
      return response.data;
    } catch (error) {
      console.error('Error decoding VIN:', error);
      throw error;
    }
  }

  /**
   * Check compatibility between vehicle and parts
   * @param {Object} compatibilityRequest - Compatibility check request
   * @param {number} compatibilityRequest.trim_id - Vehicle trim ID
   * @param {string} compatibilityRequest.make - Vehicle make (if no trim_id)
   * @param {string} compatibilityRequest.model - Vehicle model (if no trim_id)
   * @param {string} compatibilityRequest.trim - Vehicle trim (if no trim_id)
   * @param {number} compatibilityRequest.year - Vehicle year
   * @param {string} compatibilityRequest.engine_code - Engine code
   * @returns {Promise<Object>} Compatibility results with compatible parts
   */
  async checkCompatibility(compatibilityRequest) {
    try {
      const response = await this.http.post(
        ENDPOINTS.VEHICLES_ENHANCED.CHECK_COMPATIBILITY,
        compatibilityRequest
      );
      return response.data;
    } catch (error) {
      console.error('Error checking vehicle compatibility:', error);
      throw error;
    }
  }

  /**
   * Get vehicle database statistics
   * @returns {Promise<Object>} Database statistics
   */
  async getStats() {
    try {
      const response = await this.http.get(ENDPOINTS.VEHICLES_ENHANCED.STATS);
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicle stats:', error);
      throw error;
    }
  }

  /**
   * Get years for a specific brand/model combination
   * This is a convenience method that aggregates year data from trims
   * @param {number} modelId - Model ID
   * @returns {Promise<Array>} List of available years
   */
  async getModelYears(modelId) {
    try {
      const trims = await this.getModelTrims(modelId, { active_only: true });
      
      // Extract unique years from trims
      const yearsSet = new Set();
      
      trims.forEach(trim => {
        if (trim.year_from && trim.year_to) {
          for (let year = trim.year_from; year <= trim.year_to; year++) {
            yearsSet.add(year);
          }
        }
      });
      
      // Convert to array and sort
      return Array.from(yearsSet).sort((a, b) => b - a); // Newest first
    } catch (error) {
      console.error('Error fetching model years:', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const vehicleApi = new VehicleApiClient();
export default vehicleApi;

// Also export the class for potential custom instances
export { VehicleApiClient };
