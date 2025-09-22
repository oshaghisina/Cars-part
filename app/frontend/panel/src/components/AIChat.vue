<template>
  <div class="ai-chat-container">
    <!-- Chat Header -->
    <div class="chat-header">
      <div class="chat-title">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        AI Assistant
      </div>
      <div class="chat-status">
        <div class="status-indicator" :class="{ 'online': isOnline, 'offline': !isOnline }"></div>
        <span class="status-text">{{ isOnline ? 'Online' : 'Offline' }}</span>
      </div>
    </div>

    <!-- Chat Messages -->
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="message in messages" :key="message.id" class="message" :class="message.type">
        <div class="message-avatar">
          <div v-if="message.type === 'user'" class="user-avatar">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div v-else class="ai-avatar">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(message.content)"></div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <!-- Typing Indicator -->
      <div v-if="isTyping" class="message ai">
        <div class="message-avatar">
          <div class="ai-avatar">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Input -->
    <div class="chat-input-container">
      <div class="chat-input-wrapper">
        <textarea
          v-model="inputMessage"
          @keydown.enter.prevent="handleEnterKey"
          @keydown.shift.enter="addNewLine"
          placeholder="Ask me anything about the system..."
          class="chat-input"
          :disabled="isLoading"
          rows="1"
          ref="messageInput"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!inputMessage.trim() || isLoading"
          class="send-button"
        >
          <svg v-if="!isLoading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          <div v-else class="loading-spinner"></div>
        </button>
      </div>
      
      <!-- Quick Actions -->
      <div class="quick-actions">
        <button
          v-for="action in quickActions"
          :key="action.id"
          @click="sendQuickAction(action)"
          class="quick-action-button"
          :disabled="isLoading"
        >
          {{ action.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'AIChat',
  setup() {
    const authStore = useAuthStore()
    const messagesContainer = ref(null)
    const messageInput = ref(null)
    
    // Reactive state
    const inputMessage = ref('')
    const isLoading = ref(false)
    const isTyping = ref(false)
    const isOnline = ref(true)
    const messages = ref([])
    
    // Quick actions for common queries
    const quickActions = ref([
      { id: 'system-status', label: 'System Status', query: 'What is the current system status?' },
      { id: 'performance', label: 'Performance', query: 'Show me performance metrics' },
      { id: 'errors', label: 'Recent Errors', query: 'What are the recent errors in the system?' },
      { id: 'users', label: 'User Activity', query: 'Show me user activity summary' },
      { id: 'ai-status', label: 'AI Status', query: 'What is the AI Gateway status?' }
    ])
    
    // Initialize chat with welcome message
    onMounted(() => {
      addMessage('ai', 'Hello! I\'m your AI assistant. I can help you with system monitoring, performance analysis, troubleshooting, and answering questions about the China Car Parts system. How can I assist you today?')
    })
    
    // Auto-scroll to bottom when new messages arrive
    watch(messages, () => {
      nextTick(() => {
        scrollToBottom()
      })
    }, { deep: true })
    
    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }
    
    const addMessage = (type, content, timestamp = null) => {
      const message = {
        id: Date.now() + Math.random(),
        type,
        content,
        timestamp: timestamp || new Date()
      }
      messages.value.push(message)
    }
    
    const formatMessage = (content) => {
      // Convert markdown-like formatting to HTML
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>')
    }
    
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    }
    
    const handleEnterKey = () => {
      if (!isLoading.value && inputMessage.value.trim()) {
        sendMessage()
      }
    }
    
    const addNewLine = () => {
      inputMessage.value += '\n'
    }
    
    const sendMessage = async () => {
      if (!inputMessage.value.trim() || isLoading.value) return
      
      const userMessage = inputMessage.value.trim()
      inputMessage.value = ''
      
      // Add user message
      addMessage('user', userMessage)
      
      // Show typing indicator
      isTyping.value = true
      isLoading.value = true
      
      try {
        // Send message to AI service
        const response = await fetch('/api/v1/ai/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify({
            message: userMessage,
            context: {
              user_id: authStore.user?.id,
              timestamp: new Date().toISOString(),
              session_id: getSessionId()
            }
          })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        
        // Add AI response
        addMessage('ai', data.response || 'I apologize, but I couldn\'t process your request at the moment.')
        
      } catch (error) {
        console.error('Chat error:', error)
        addMessage('ai', 'I apologize, but I\'m experiencing technical difficulties. Please try again later or contact support if the issue persists.')
      } finally {
        isTyping.value = false
        isLoading.value = false
        // Focus back on input
        nextTick(() => {
          if (messageInput.value) {
            messageInput.value.focus()
          }
        })
      }
    }
    
    const sendQuickAction = (action) => {
      inputMessage.value = action.query
      sendMessage()
    }
    
    const getSessionId = () => {
      let sessionId = localStorage.getItem('ai_chat_session_id')
      if (!sessionId) {
        sessionId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
        localStorage.setItem('ai_chat_session_id', sessionId)
      }
      return sessionId
    }
    
    // Check AI service status
    const checkAIServiceStatus = async () => {
      try {
        const response = await fetch('/api/v1/ai/status', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        isOnline.value = response.ok
      } catch (error) {
        isOnline.value = false
      }
    }
    
    // Check status periodically
    onMounted(() => {
      checkAIServiceStatus()
      setInterval(checkAIServiceStatus, 30000) // Check every 30 seconds
    })
    
    return {
      messagesContainer,
      messageInput,
      inputMessage,
      isLoading,
      isTyping,
      isOnline,
      messages,
      quickActions,
      addMessage,
      formatMessage,
      formatTime,
      handleEnterKey,
      addNewLine,
      sendMessage,
      sendQuickAction
    }
  }
}
</script>

<style scoped>
.ai-chat-container {
  @apply flex flex-col h-full bg-white border border-gray-200 rounded-lg shadow-sm;
  max-height: 600px;
}

.chat-header {
  @apply flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg;
}

.chat-title {
  @apply flex items-center text-lg font-semibold text-gray-900;
}

.chat-status {
  @apply flex items-center space-x-2;
}

.status-indicator {
  @apply w-2 h-2 rounded-full;
}

.status-indicator.online {
  @apply bg-green-500;
}

.status-indicator.offline {
  @apply bg-red-500;
}

.status-text {
  @apply text-sm text-gray-600;
}

.chat-messages {
  @apply flex-1 overflow-y-auto p-4 space-y-4;
  max-height: 400px;
}

.message {
  @apply flex space-x-3;
}

.message.user {
  @apply flex-row-reverse space-x-reverse;
}

.message-avatar {
  @apply flex-shrink-0;
}

.user-avatar {
  @apply w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white;
}

.ai-avatar {
  @apply w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white;
}

.message-content {
  @apply flex-1;
}

.message.user .message-content {
  @apply text-right;
}

.message-text {
  @apply text-sm text-gray-900 bg-gray-100 rounded-lg px-3 py-2 inline-block max-w-xs;
}

.message.user .message-text {
  @apply bg-blue-500 text-white;
}

.message.ai .message-text {
  @apply bg-gray-100 text-gray-900;
}

.message-time {
  @apply text-xs text-gray-500 mt-1;
}

.typing-indicator {
  @apply flex space-x-1;
}

.typing-indicator span {
  @apply w-2 h-2 bg-gray-400 rounded-full animate-pulse;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

.chat-input-container {
  @apply border-t border-gray-200 p-4 bg-gray-50 rounded-b-lg;
}

.chat-input-wrapper {
  @apply flex items-end space-x-2;
}

.chat-input {
  @apply flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
  min-height: 40px;
  max-height: 120px;
}

.chat-input:disabled {
  @apply bg-gray-100 cursor-not-allowed;
}

.send-button {
  @apply w-10 h-10 bg-blue-500 text-white rounded-lg flex items-center justify-center hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors;
}

.loading-spinner {
  @apply w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin;
}

.quick-actions {
  @apply flex flex-wrap gap-2 mt-3;
}

.quick-action-button {
  @apply px-3 py-1 text-xs bg-white border border-gray-300 rounded-full hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors;
}

/* Custom scrollbar */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded;
}

.chat-messages::-webkit-scrollbar-thumb {
  @apply bg-gray-300 rounded;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400;
}

/* Code formatting */
.message-text code {
  @apply bg-gray-200 px-1 py-0.5 rounded text-xs font-mono;
}

.message.user .message-text code {
  @apply bg-blue-600 text-blue-100;
}
</style>
