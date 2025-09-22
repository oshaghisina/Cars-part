<template>
  <div class="ai-chat-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <h1 class="text-2xl font-bold text-gray-900">AI Assistant</h1>
          <p class="text-gray-600">
            Get help with system monitoring, troubleshooting, and analysis
          </p>
        </div>
        <div class="header-actions">
          <button
            class="action-button"
            :title="isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'"
            @click="toggleFullscreen"
          >
            <svg
              v-if="!isFullscreen"
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
              />
            </svg>
            <svg
              v-else
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 9V4.5M9 9H4.5M9 9L3.5 3.5M15 9v-4.5M15 9h4.5M15 9l5.5-5.5M9 15v4.5M9 15H4.5M9 15l-5.5 5.5M15 15v4.5M15 15h4.5m0 0l5.5 5.5"
              />
            </svg>
          </button>
          <button class="action-button" title="Clear Chat" @click="clearChat">
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
          <button class="action-button" title="Export Chat" @click="exportChat">
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Chat Container -->
    <div class="chat-container" :class="{ fullscreen: isFullscreen }">
      <AIChat ref="aiChat" />
    </div>

    <!-- AI Status Panel -->
    <div v-if="showStatusPanel" class="status-panel">
      <div class="status-header">
        <h3 class="text-lg font-semibold text-gray-900">AI System Status</h3>
        <button class="close-button" @click="showStatusPanel = false">
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
      <div class="status-content">
        <div v-if="aiStatus" class="status-grid">
          <div class="status-item">
            <div class="status-label">AI Gateway</div>
            <div
              class="status-value"
              :class="aiStatus.enabled ? 'text-green-600' : 'text-red-600'"
            >
              {{ aiStatus.enabled ? "Enabled" : "Disabled" }}
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">Providers</div>
            <div class="status-value">
              {{ Object.keys(aiStatus.providers || {}).length }}
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">Cache Hit Rate</div>
            <div class="status-value">
              {{ aiStatus.caching?.hit_rate || 0 }}%
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">Performance</div>
            <div class="status-value">
              {{ aiStatus.performance?.global_metrics?.success_rate || 0 }}%
              Success
            </div>
          </div>
        </div>
        <div v-else class="status-loading">
          <div class="loading-spinner"></div>
          <span>Loading status...</span>
        </div>
      </div>
    </div>

    <!-- Floating Action Button -->
    <div class="floating-actions">
      <button
        class="floating-button"
        title="AI Status"
        @click="showStatusPanel = !showStatusPanel"
      >
        <svg
          class="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import AIChat from "../components/AIChat.vue";
import { useAuthStore } from "../stores/auth";

export default {
  name: "AIChatPage",
  components: {
    AIChat,
  },
  setup() {
    const authStore = useAuthStore();
    const aiChat = ref(null);
    const isFullscreen = ref(false);
    const showStatusPanel = ref(false);
    const aiStatus = ref(null);

    const toggleFullscreen = () => {
      isFullscreen.value = !isFullscreen.value;
      if (isFullscreen.value) {
        document.documentElement.requestFullscreen?.();
      } else {
        document.exitFullscreen?.();
      }
    };

    const clearChat = () => {
      if (aiChat.value) {
        // Reset the chat component
        aiChat.value.messages = [];
        aiChat.value.addMessage(
          "ai",
          "Hello! I'm your AI assistant. How can I help you today?",
        );
      }
    };

    const exportChat = () => {
      if (!aiChat.value?.messages) return;

      const chatData = {
        timestamp: new Date().toISOString(),
        messages: aiChat.value.messages.map((msg) => ({
          type: msg.type,
          content: msg.content,
          timestamp: msg.timestamp,
        })),
      };

      const blob = new Blob([JSON.stringify(chatData, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ai-chat-export-${new Date().toISOString().split("T")[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    };

    const loadAIStatus = async () => {
      try {
        const response = await fetch("/api/v1/ai/status", {
          headers: {
            Authorization: `Bearer ${authStore.token}`,
          },
        });

        if (response.ok) {
          aiStatus.value = await response.json();
        }
      } catch (error) {
        console.error("Failed to load AI status:", error);
      }
    };

    const handleFullscreenChange = () => {
      isFullscreen.value = !!document.fullscreenElement;
    };

    onMounted(() => {
      loadAIStatus();
      document.addEventListener("fullscreenchange", handleFullscreenChange);

      // Load AI status periodically
      const statusInterval = setInterval(loadAIStatus, 60000); // Every minute

      onUnmounted(() => {
        clearInterval(statusInterval);
        document.removeEventListener(
          "fullscreenchange",
          handleFullscreenChange,
        );
      });
    });

    return {
      aiChat,
      isFullscreen,
      showStatusPanel,
      aiStatus,
      toggleFullscreen,
      clearChat,
      exportChat,
    };
  },
};
</script>

<style scoped>
.ai-chat-page {
  @apply h-full flex flex-col bg-gray-50;
}

.page-header {
  @apply bg-white border-b border-gray-200 px-6 py-4;
}

.header-content {
  @apply flex items-center justify-between;
}

.header-title h1 {
  @apply text-2xl font-bold text-gray-900;
}

.header-title p {
  @apply text-gray-600 mt-1;
}

.header-actions {
  @apply flex items-center space-x-2;
}

.action-button {
  @apply p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors;
}

.chat-container {
  @apply flex-1 p-6;
  transition: all 0.3s ease;
}

.chat-container.fullscreen {
  @apply fixed inset-0 z-50 bg-white p-0;
}

.status-panel {
  @apply fixed right-4 top-4 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-40;
  max-height: 400px;
}

.status-header {
  @apply flex items-center justify-between p-4 border-b border-gray-200;
}

.close-button {
  @apply p-1 text-gray-400 hover:text-gray-600 rounded;
}

.status-content {
  @apply p-4;
}

.status-grid {
  @apply grid grid-cols-2 gap-4;
}

.status-item {
  @apply space-y-1;
}

.status-label {
  @apply text-sm font-medium text-gray-500;
}

.status-value {
  @apply text-lg font-semibold;
}

.status-loading {
  @apply flex items-center justify-center space-x-2 py-8;
}

.loading-spinner {
  @apply w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin;
}

.floating-actions {
  @apply fixed bottom-6 right-6 z-30;
}

.floating-button {
  @apply w-12 h-12 bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors;
}

/* Responsive design */
@media (max-width: 768px) {
  .page-header {
    @apply px-4 py-3;
  }

  .header-content {
    @apply flex-col items-start space-y-2;
  }

  .header-actions {
    @apply w-full justify-end;
  }

  .chat-container {
    @apply p-4;
  }

  .status-panel {
    @apply right-2 top-2 left-2 w-auto;
  }

  .floating-actions {
    @apply bottom-4 right-4;
  }
}

/* Fullscreen styles */
.chat-container.fullscreen .page-header {
  @apply hidden;
}

.chat-container.fullscreen .floating-actions {
  @apply hidden;
}
</style>
