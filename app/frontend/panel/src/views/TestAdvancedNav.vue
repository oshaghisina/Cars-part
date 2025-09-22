<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Advanced Navigation Bar -->
    <AdvancedNavBar />

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">
          Advanced Navigation Bar Test
        </h1>
        <p class="mt-2 text-gray-600">
          This page demonstrates the advanced navigation bar with dropdown
          menus, search functionality, and user management.
        </p>
      </div>

      <!-- Feature Overview -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <!-- Dropdown Menus -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center mb-4">
            <div
              class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>
            <h3 class="ml-3 text-lg font-medium text-gray-900">
              Dropdown Menus
            </h3>
          </div>
          <p class="text-gray-600">
            Organized navigation with dropdown menus for Inventory, Sales, and
            Administration sections.
          </p>
          <ul class="mt-3 text-sm text-gray-500">
            <li>• Inventory: Vehicles, Categories, Parts</li>
            <li>• Sales: Orders, Leads</li>
            <li>• Admin: Users, Analytics</li>
          </ul>
        </div>

        <!-- Search Functionality -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center mb-4">
            <div
              class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <h3 class="ml-3 text-lg font-medium text-gray-900">
              Global Search
            </h3>
          </div>
          <p class="text-gray-600">
            Integrated search bar with real-time suggestions and quick access to
            all modules.
          </p>
          <div class="mt-3 text-sm text-gray-500">
            <p>• Search across parts, orders, leads</p>
            <p>• Keyboard shortcuts support</p>
            <p>• Search history and suggestions</p>
          </div>
        </div>

        <!-- User Management -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center mb-4">
            <div
              class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <h3 class="ml-3 text-lg font-medium text-gray-900">User Profile</h3>
          </div>
          <p class="text-gray-600">
            User avatar with dropdown menu for profile management and settings.
          </p>
          <div class="mt-3 text-sm text-gray-500">
            <p>• Profile management</p>
            <p>• Settings access</p>
            <p>• Secure logout</p>
          </div>
        </div>
      </div>

      <!-- Interactive Demo -->
      <div class="bg-white rounded-lg shadow p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">
          Interactive Demo
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-3">
              Try the Features:
            </h3>
            <ul class="space-y-2 text-gray-600">
              <li class="flex items-center">
                <svg
                  class="w-4 h-4 text-blue-500 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Hover over "Inventory" to see dropdown menu
              </li>
              <li class="flex items-center">
                <svg
                  class="w-4 h-4 text-blue-500 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Hover over "Sales" to see orders and leads
              </li>
              <li class="flex items-center">
                <svg
                  class="w-4 h-4 text-blue-500 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Hover over "Admin" to see users and analytics
              </li>
              <li class="flex items-center">
                <svg
                  class="w-4 h-4 text-blue-500 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Use the search bar to search across modules
              </li>
              <li class="flex items-center">
                <svg
                  class="w-4 h-4 text-blue-500 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Click on user avatar for profile menu
              </li>
            </ul>
          </div>
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-3">
              Responsive Design:
            </h3>
            <ul class="space-y-2 text-gray-600">
              <li class="flex items-center">
                <svg
                  class="w-4 h-4 text-green-500 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Mobile-friendly hamburger menu
              </li>
              <li class="flex items-center">
                <svg
                  class="w-4 h-4 text-green-500 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Adaptive layout for all screen sizes
              </li>
              <li class="flex items-center">
                <svg
                  class="w-4 h-4 text-green-500 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Smooth hover animations
              </li>
              <li class="flex items-center">
                <svg
                  class="w-4 h-4 text-green-500 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Dark theme with modern styling
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Comparison with Current NavBar -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">
          Advanced vs Current Navigation
        </h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Feature
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Current NavBar
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Advanced NavBar
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr>
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
                >
                  Navigation Style
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Flat horizontal links
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Organized dropdown menus
                </td>
              </tr>
              <tr>
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
                >
                  Search Functionality
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  ❌ Not available
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  ✅ Global search bar
                </td>
              </tr>
              <tr>
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
                >
                  User Management
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Simple welcome + logout
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Avatar + profile dropdown
                </td>
              </tr>
              <tr>
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
                >
                  Visual Design
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Light theme
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Dark theme with modern styling
                </td>
              </tr>
              <tr>
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
                >
                  Mobile Support
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Basic responsive
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Enhanced mobile menu
                </td>
              </tr>
              <tr>
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
                >
                  Organization
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  All links visible
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Grouped by functionality
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 class="text-lg font-medium text-blue-900 mb-2">Recommendation</h3>
          <p class="text-blue-800">
            The AdvancedNavBar provides a more professional and organized user
            experience with better navigation structure, search functionality,
            and modern design. It's particularly beneficial for larger
            applications with many modules.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import AdvancedNavBar from "@/components/AdvancedNavBar.vue";
</script>

<style scoped>
/* Additional styling for the test page */
</style>
