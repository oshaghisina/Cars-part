"""
AI Chat API Router

This module provides API endpoints for AI chat functionality in the admin panel.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.services.ai_orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/chat", tags=["AI Chat"])

# Global AI orchestrator instance
ai_orchestrator = AIOrchestrator()
ai_orchestrator.initialize()


class ChatMessage(BaseModel):
    """Chat message request model."""

    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str
    session_id: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class ChatHistory(BaseModel):
    """Chat history model."""

    session_id: str
    messages: List[Dict[str, Any]]
    created_at: str
    updated_at: str


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(message_data: ChatMessage, current_user: dict = Depends(get_current_user)):
    """
    Chat with the AI assistant.

    Args:
        message_data: Chat message and context
        current_user: Current authenticated user

    Returns:
        AI response
    """
    try:
        # Extract message and context
        user_message = message_data.message.strip()
        context = message_data.context or {}

        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty"
            )

        # Add user context
        context.update(
            {
                "user_id": current_user.get("id"),
                "username": current_user.get("username"),
                "role": current_user.get("role", "user"),
            }
        )

        # Process the message with AI
        ai_response = await process_chat_message(user_message, context)

        # Generate session ID if not provided
        session_id = context.get(
            "session_id", f"chat_{current_user.get('id')}_{hash(user_message) % 10000}"
        )

        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            timestamp=context.get("timestamp", ""),
            metadata={
                "user_id": current_user.get("id"),
                "message_length": len(user_message),
                "response_length": len(ai_response),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message",
        )


async def process_chat_message(message: str, context: Dict[str, Any]) -> str:
    """
    Process a chat message using AI capabilities.

    Args:
        message: User message
        context: Additional context

    Returns:
        AI response
    """
    try:
        # Analyze the message to determine intent
        query_analysis = await ai_orchestrator.analyze_query(message)

        # Determine response based on intent and content
        intent = query_analysis.get("intent", "general")

        if intent == "system_status":
            return await handle_system_status_query(message, context)
        elif intent == "performance":
            return await handle_performance_query(message, context)
        elif intent == "errors":
            return await handle_errors_query(message, context)
        elif intent == "users":
            return await handle_users_query(message, context)
        elif intent == "ai_status":
            return await handle_ai_status_query(message, context)
        elif intent == "help":
            return await handle_help_query(message, context)
        else:
            return await handle_general_query(message, context)

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return (
            "I apologize, but I encountered an error while processing your request. "
            "Please try again or contact support if the issue persists."
        )


async def handle_system_status_query(message: str, context: Dict[str, Any]) -> str:
    """Handle system status related queries."""
    try:
        # Get system status
        ai_status = ai_orchestrator.get_ai_status()

        response = "## System Status\n\n"

        # AI Gateway status
        if ai_status.get("enabled"):
            response += "✅ **AI Gateway**: Enabled\n"
        else:
            response += "❌ **AI Gateway**: Disabled\n"

        # Provider status
        providers = ai_status.get("providers", {})
        if providers:
            response += f"\n**AI Providers**: {len(providers)} available\n"
        for name, provider_status in providers.items():
            status_icon = "✅" if provider_status.get("available") else "❌"
            response += (
                f"- {status_icon} {name.title()}: " f"{provider_status.get('status', 'unknown')}\n"
            )

        # Performance metrics
        performance = ai_status.get("performance", {})
        if performance:
            global_metrics = performance.get("global_metrics", {})
            response += "\n**Performance**:\n"
            response += f"- Success Rate: " f"{global_metrics.get('success_rate', 0):.1f}%\n"
            response += (
                f"- Average Response Time: "
                f"{global_metrics.get('average_response_time', 0):.3f}s\n"
            )
            response += f"- Total Requests: {global_metrics.get('total_requests', 0)}\n"

        # Cache status
        caching = ai_status.get("caching", {})
        if caching:
            response += "\n**Caching**:\n"
            response += f"- Hit Rate: {caching.get('hit_rate', 0):.1f}%\n"
            response += f"- Total Requests: {caching.get('total_requests', 0)}\n"

        return response

    except Exception as e:
        logger.error(f"Error handling system status query: {e}")
        return "I'm having trouble retrieving the system status. Please try again later."


async def handle_performance_query(message: str, context: Dict[str, Any]) -> str:
    """Handle performance related queries."""
    try:
        # Get performance health
        performance_health = await ai_orchestrator.get_performance_health()

        response = "## Performance Metrics\n\n"

        # Global metrics
        performance_stats = performance_health.get("performance_stats", {})
        global_metrics = performance_stats.get("global_metrics", {})

        if global_metrics:
            response += "**Overall Performance**:\n"
            response += f"- Success Rate: {global_metrics.get('success_rate', 0):.1f}%\n"
            response += f"- Error Rate: {global_metrics.get('error_rate', 0):.1f}%\n"
            avg_time = global_metrics.get("average_response_time", 0)
            response += f"- Average Response Time: {avg_time:.3f}s\n"
            throughput = global_metrics.get("throughput_rpm", 0)
            response += f"- Throughput: {throughput:.1f} requests/min\n"
            response += f"- Average Cost: ${global_metrics.get('average_cost', 0):.4f}\n"
            response += f"- Average Tokens: {global_metrics.get('average_tokens', 0):.0f}\n"

        # Provider performance
        provider_stats = performance_stats.get("provider_stats", {})
        if provider_stats:
            response += "\n**Provider Performance**:\n"
            for provider, stats in provider_stats.items():
                metrics = stats.get("metrics", {})
                response += f"- **{provider.title()}**:\n"
                response += f"  - Success Rate: {metrics.get('success_rate', 0):.1f}%\n"
                response += f"  - Response Time: {metrics.get('average_response_time', 0):.3f}s\n"
                response += f"  - Weight: {stats.get('weight', 0):.2f}\n"

        # Resource usage
        resource_usage = performance_health.get("resource_usage", {})
        if resource_usage:
            response += "\n**Resource Usage**:\n"
            limits = resource_usage.get("limits", {})
            current_usage = resource_usage.get("current_usage", {})
            resource_usage.get("utilization", {})

            response += (
                f"- Concurrent Requests: "
                f"{current_usage.get('concurrent_requests', 0)}/"
                f"{limits.get('max_concurrent_requests', 0)}\n"
            )
            response += (
                f"- Requests/min: "
                f"{current_usage.get('requests_this_minute', 0)}/"
                f"{limits.get('max_requests_per_minute', 0)}\n"
            )
            response += (
                f"- Tokens/min: "
                f"{current_usage.get('tokens_this_minute', 0)}/"
                f"{limits.get('max_tokens_per_minute', 0)}\n"
            )
            response += (
                f"- Cost/hour: "
                f"${current_usage.get('cost_this_hour', 0):.2f}/"
                f"${limits.get('max_cost_per_hour', 0):.2f}\n"
            )

        return response

    except Exception as e:
        logger.error(f"Error handling performance query: {e}")
        return "I'm having trouble retrieving performance metrics. Please try again later."


async def handle_errors_query(message: str, context: Dict[str, Any]) -> str:
    """Handle error related queries."""
    try:
        # Get AI status for error information
        ai_status = ai_orchestrator.get_ai_status()

        response = "## Recent System Status\n\n"

        # Check for any unhealthy providers
        providers = ai_status.get("providers", {})
        unhealthy_providers = []
        for name, provider_status in providers.items():
            if not provider_status.get("available") or provider_status.get("status") != "healthy":
                unhealthy_providers.append(name)

        if unhealthy_providers:
            response += "❌ **Unhealthy Providers**:\n"
            for provider in unhealthy_providers:
                response += f"- {provider.title()}\n"
        else:
            response += "✅ **All providers are healthy**\n"

        # Performance metrics for error rates
        performance = ai_status.get("performance", {})
        if performance:
            global_metrics = performance.get("global_metrics", {})
            error_rate = global_metrics.get("error_rate", 0)

            if error_rate > 0:
                response += f"\n⚠️ **Error Rate**: {error_rate:.1f}%\n"
                error_breakdown = global_metrics.get("error_breakdown", {})
                if error_breakdown:
                    response += "\n**Error Breakdown**:\n"
                    for error_type, count in error_breakdown.items():
                        response += f"- {error_type}: {count}\n"
            else:
                response += "\n✅ **No errors detected**\n"

        # Circuit breaker status
        if providers:
            response += "\n**Circuit Breaker Status**:\n"
            for name, provider_status in providers.items():
                cb_status = provider_status.get("circuit_breaker", {})
                state = cb_status.get("state", "unknown")
                state_icon = "🟢" if state == "closed" else "🔴" if state == "open" else "🟡"
                response += f"- {state_icon} {name.title()}: {state}\n"

        return response

    except Exception as e:
        logger.error(f"Error handling errors query: {e}")
        return "I'm having trouble retrieving error information. " "Please try again later."


async def handle_users_query(message: str, context: Dict[str, Any]) -> str:
    """Handle user activity related queries."""
    try:
        # This would typically query the database for user activity
        # For now, we'll provide a general response

        response = "## User Activity Summary\n\n"
        response += (
            "I can help you with user-related information, but I need to "
            "connect to the database to get real-time data.\n\n"
        )
        response += "**Available user queries**:\n"
        response += "- Show active users\n"
        response += "- User login statistics\n"
        response += "- User role distribution\n"
        response += "- Recent user registrations\n"
        response += "- User activity patterns\n\n"
        response += "Please be more specific about what user information you'd like to see."

        return response

    except Exception as e:
        logger.error(f"Error handling users query: {e}")
        return "I'm having trouble retrieving user information. Please try again later."


async def handle_ai_status_query(message: str, context: Dict[str, Any]) -> str:
    """Handle AI status related queries."""
    try:
        # Get comprehensive AI status
        ai_status = ai_orchestrator.get_ai_status()

        response = "## AI Gateway Status\n\n"

        # Basic status
        if ai_status.get("enabled"):
            response += "✅ **AI Gateway**: Enabled\n"
        else:
            response += "❌ **AI Gateway**: Disabled\n"

        # Provider details
        providers = ai_status.get("providers", {})
        if providers:
            response += f"\n**Providers** ({len(providers)}):\n"
            for name, provider_status in providers.items():
                available = "✅" if provider_status.get("available") else "❌"
                healthy = "🟢" if provider_status.get("healthy") else "🔴"
                response += (
                    f"- {available} {name.title()}: "
                    f"{provider_status.get('status', 'unknown')} {healthy}\n"
                )

                capabilities = provider_status.get("capabilities", [])
                if capabilities:
                    response += f"  - Capabilities: {', '.join(capabilities)}\n"

        # Performance summary
        performance = ai_status.get("performance", {})
        if performance:
            global_metrics = performance.get("global_metrics", {})
            response += "\n**Performance Summary**:\n"
            response += f"- Success Rate: {global_metrics.get('success_rate', 0):.1f}%\n"
            response += f"- Response Time: {global_metrics.get('average_response_time', 0):.3f}s\n"
            response += f"- Total Requests: {global_metrics.get('total_requests', 0)}\n"

        # Cache status
        caching = ai_status.get("caching", {})
        if caching:
            response += "\n**Cache Status**:\n"
            response += f"- Hit Rate: {caching.get('hit_rate', 0):.1f}%\n"
            response += f"- Memory Entries: {caching.get('memory_entries', 0)}\n"
            response += f"- Redis Enabled: {'Yes' if caching.get('redis_enabled') else 'No'}\n"

        return response

    except Exception as e:
        logger.error(f"Error handling AI status query: {e}")
        return "I'm having trouble retrieving AI status information. Please try again later."


async def handle_help_query(message: str, context: Dict[str, Any]) -> str:
    """Handle help related queries."""
    response = """## AI Assistant Help

I'm your AI assistant for the China Car Parts system. I can help you with:

### System Monitoring
- **System Status**: Check overall system health and status
- **Performance**: View performance metrics and statistics
- **Errors**: Check for recent errors and issues
- **AI Status**: Get detailed AI Gateway information

### Quick Commands
- "Show me the system status"
- "What's the performance like?"
- "Are there any errors?"
- "How is the AI system doing?"

### Features
- Real-time system monitoring
- Performance analysis
- Error detection and reporting
- AI Gateway status
- Resource usage tracking

### Tips
- Be specific about what you want to know
- Use natural language - I understand context
- Ask follow-up questions for more details
- I can help troubleshoot issues

How can I assist you today?"""

    return response


async def handle_general_query(message: str, context: Dict[str, Any]) -> str:
    """Handle general queries."""
    try:
        # Use intelligent search for general queries
        search_result = await ai_orchestrator.intelligent_search(message)

        if search_result and search_result.get("success"):
            # Extract suggestions and analysis
            suggestions = search_result.get("suggestions", [])
            analysis = search_result.get("query_analysis", {})

            response = "I understand you're asking about: "
            response += f"**{message}**\n\n"

            if analysis:
                intent = analysis.get("intent", "general")
                response += f"Intent: {intent}\n\n"

            if suggestions:
                response += "Here are some related topics you might find helpful:\n"
                for i, suggestion in enumerate(suggestions[:3], 1):
                    response += f"{i}. {suggestion}\n"

            response += "\nFor more specific help, try asking about:\n"
            response += "- System status\n"
            response += "- Performance metrics\n"
            response += "- Error reports\n"
            response += "- AI Gateway status\n"

        else:
            response = "I understand you're asking about: "
            response += f"**{message}**\n\n"
            response += "I'm here to help with system monitoring and analysis. "
            response += "Could you be more specific about what you'd like to know? "
            response += "For example, you could ask about system status, performance, or errors."

        return response

    except Exception as e:
        logger.error(f"Error handling general query: {e}")
        return (
            "I'm here to help with system monitoring and analysis. "
            "Could you please rephrase your question or ask about something "
            "specific like system status, performance, or errors?"
        )


@router.get("/status")
async def get_chat_status(current_user: dict = Depends(get_current_user)):
    """Get AI chat service status."""
    try:
        ai_status = ai_orchestrator.get_ai_status()

        return {
            "available": ai_status.get("enabled", False),
            "providers": len(ai_status.get("providers", {})),
            "performance": ai_status.get("performance", {}),
            "caching": ai_status.get("caching", {}),
        }

    except Exception as e:
        logger.error(f"Error getting chat status: {e}")
        return {"available": False, "error": str(e)}
