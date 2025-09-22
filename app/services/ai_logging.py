"""
AI Logging Utilities with PII Masking

This module provides structured logging capabilities for AI operations,
including PII detection and masking, request/response correlation,
and audit trail functionality.
"""

import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PIIMasker:
    """Utility class for detecting and masking PII in text."""
    
    # Patterns for detecting PII
    PATTERNS = {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'),
        'ssn': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
        'credit_card': re.compile(r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b'),
        'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
        'persian_phone': re.compile(r'(\+98|0)?9\d{9}'),
        'persian_id': re.compile(r'\b\d{10}\b'),
    }
    
    @classmethod
    def mask_pii(cls, text: str, mask_char: str = '*') -> str:
        """
        Mask PII in text using predefined patterns.
        
        Args:
            text: Text to mask
            mask_char: Character to use for masking
            
        Returns:
            Text with PII masked
        """
        if not isinstance(text, str):
            return text
            
        masked_text = text
        
        # Mask emails
        for match in cls.PATTERNS['email'].finditer(masked_text):
            email = match.group()
            local, domain = email.split('@')
            masked_local = local[0] + mask_char * (len(local) - 2) + local[-1] if len(local) > 2 else mask_char * len(local)
            masked_email = f"{masked_local}@{domain}"
            masked_text = masked_text.replace(email, f"[EMAIL:{masked_email}]")
        
        # Mask phone numbers
        for match in cls.PATTERNS['phone'].finditer(masked_text):
            phone = match.group()
            masked_phone = f"[PHONE:{mask_char * 10}]"
            masked_text = masked_text.replace(phone, masked_phone)
            
        # Mask Persian phone numbers
        for match in cls.PATTERNS['persian_phone'].finditer(masked_text):
            phone = match.group()
            masked_phone = f"[PHONE_IR:{mask_char * 10}]"
            masked_text = masked_text.replace(phone, masked_phone)
        
        # Mask SSN
        for match in cls.PATTERNS['ssn'].finditer(masked_text):
            ssn = match.group()
            masked_ssn = f"[SSN:{mask_char * 9}]"
            masked_text = masked_text.replace(ssn, masked_ssn)
        
        # Mask credit card numbers
        for match in cls.PATTERNS['credit_card'].finditer(masked_text):
            card = match.group()
            masked_card = f"[CARD:{mask_char * 16}]"
            masked_text = masked_text.replace(card, masked_card)
        
        # Mask IP addresses
        for match in cls.PATTERNS['ip_address'].finditer(masked_text):
            ip = match.group()
            masked_ip = f"[IP:{mask_char * 15}]"
            masked_text = masked_text.replace(ip, masked_ip)
        
        # Mask Persian national ID
        for match in cls.PATTERNS['persian_id'].finditer(masked_text):
            pid = match.group()
            masked_pid = f"[ID_IR:{mask_char * 10}]"
            masked_text = masked_text.replace(pid, masked_pid)
        
        return masked_text
    
    @classmethod
    def has_pii(cls, text: str) -> bool:
        """
        Check if text contains PII.
        
        Args:
            text: Text to check
            
        Returns:
            True if PII is detected, False otherwise
        """
        if not isinstance(text, str):
            return False
            
        for pattern in cls.PATTERNS.values():
            if pattern.search(text):
                return True
        return False


class AILogger:
    """Structured logger for AI operations with correlation and masking."""
    
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)
        self.masker = PIIMasker()
    
    def _create_correlation_id(self) -> str:
        """Create a unique correlation ID for request tracking."""
        return str(uuid.uuid4())[:8]
    
    def _mask_sensitive_data(self, data: Any) -> Any:
        """
        Recursively mask PII in data structures.
        
        Args:
            data: Data to mask (dict, list, string, or other)
            
        Returns:
            Data with PII masked
        """
        if isinstance(data, dict):
            return {key: self._mask_sensitive_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            return self.masker.mask_pii(data)
        else:
            return data
    
    def _format_log_data(self, 
                        level: str,
                        correlation_id: str,
                        operation: str,
                        provider: str,
                        data: Dict[str, Any],
                        duration_ms: Optional[float] = None) -> Dict[str, Any]:
        """
        Format log data in a structured way.
        
        Args:
            level: Log level
            correlation_id: Request correlation ID
            operation: AI operation name
            provider: AI provider name
            data: Log data
            duration_ms: Operation duration in milliseconds
            
        Returns:
            Formatted log data
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "correlation_id": correlation_id,
            "operation": operation,
            "provider": provider,
            "data": self._mask_sensitive_data(data),
        }
        
        if duration_ms is not None:
            log_entry["duration_ms"] = duration_ms
            
        return log_entry
    
    def log_request(self, 
                   correlation_id: str,
                   operation: str,
                   provider: str,
                   request_data: Dict[str, Any]) -> None:
        """
        Log an AI request.
        
        Args:
            correlation_id: Request correlation ID
            operation: AI operation name
            provider: AI provider name
            request_data: Request data
        """
        log_data = self._format_log_data(
            "INFO", correlation_id, operation, provider, {
                "type": "request",
                "request": request_data
            }
        )
        
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_response(self, 
                    correlation_id: str,
                    operation: str,
                    provider: str,
                    response_data: Dict[str, Any],
                    duration_ms: Optional[float] = None) -> None:
        """
        Log an AI response.
        
        Args:
            correlation_id: Request correlation ID
            operation: AI operation name
            provider: AI provider name
            response_data: Response data
            duration_ms: Operation duration in milliseconds
        """
        log_data = self._format_log_data(
            "INFO", correlation_id, operation, provider, {
                "type": "response",
                "response": response_data
            },
            duration_ms
        )
        
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_error(self, 
                  correlation_id: str,
                  operation: str,
                  provider: str,
                  error: Exception,
                  request_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an AI operation error.
        
        Args:
            correlation_id: Request correlation ID
            operation: AI operation name
            provider: AI provider name
            error: Exception that occurred
            request_data: Original request data (optional)
        """
        error_data = {
            "type": "error",
            "error": {
                "type": type(error).__name__,
                "message": str(error),
            }
        }
        
        if request_data:
            error_data["request"] = request_data
        
        log_data = self._format_log_data(
            "ERROR", correlation_id, operation, provider, error_data
        )
        
        self.logger.error(json.dumps(log_data, ensure_ascii=False))
    
    def log_provider_status(self, 
                           provider: str,
                           status: str,
                           details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log provider status changes.
        
        Args:
            provider: Provider name
            status: Provider status
            details: Additional status details
        """
        log_data = self._format_log_data(
            "INFO", "system", "provider_status", provider, {
                "type": "status_change",
                "status": status,
                "details": details or {}
            }
        )
        
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_cost_tracking(self, 
                         correlation_id: str,
                         provider: str,
                         operation: str,
                         cost_data: Dict[str, Any]) -> None:
        """
        Log AI operation cost tracking.
        
        Args:
            correlation_id: Request correlation ID
            provider: Provider name
            operation: Operation name
            cost_data: Cost tracking data
        """
        log_data = self._format_log_data(
            "INFO", correlation_id, operation, provider, {
                "type": "cost_tracking",
                "cost": cost_data
            }
        )
        
        self.logger.info(json.dumps(log_data, ensure_ascii=False))


class AILoggingMixin:
    """Mixin class to add AI logging capabilities to other classes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ai_logger = AILogger(self.__class__.__name__)
        self._correlation_id = None
    
    def _get_correlation_id(self) -> str:
        """Get or create correlation ID for current operation."""
        if not self._correlation_id:
            self._correlation_id = self.ai_logger._create_correlation_id()
        return self._correlation_id
    
    def _reset_correlation_id(self) -> None:
        """Reset correlation ID for new operation."""
        self._correlation_id = None
    
    def _log_ai_operation(self, 
                         operation: str,
                         provider: str,
                         request_data: Dict[str, Any],
                         response_data: Optional[Dict[str, Any]] = None,
                         error: Optional[Exception] = None,
                         duration_ms: Optional[float] = None) -> None:
        """
        Log AI operation with automatic correlation tracking.
        
        Args:
            operation: Operation name
            provider: Provider name
            request_data: Request data
            response_data: Response data (optional)
            error: Exception (optional)
            duration_ms: Operation duration (optional)
        """
        correlation_id = self._get_correlation_id()
        
        # Log request
        self.ai_logger.log_request(correlation_id, operation, provider, request_data)
        
        # Log response or error
        if error:
            self.ai_logger.log_error(correlation_id, operation, provider, error, request_data)
        elif response_data is not None:
            self.ai_logger.log_response(correlation_id, operation, provider, response_data, duration_ms)
        
        # Reset correlation ID after operation
        self._reset_correlation_id()


# Global AI logger instance
ai_logger = AILogger("ai_gateway")


def log_ai_operation(operation: str, 
                    provider: str,
                    request_data: Dict[str, Any],
                    response_data: Optional[Dict[str, Any]] = None,
                    error: Optional[Exception] = None,
                    duration_ms: Optional[float] = None) -> str:
    """
    Log AI operation using global logger.
    
    Args:
        operation: Operation name
        provider: Provider name
        request_data: Request data
        response_data: Response data (optional)
        error: Exception (optional)
        duration_ms: Operation duration (optional)
        
    Returns:
        Correlation ID for the operation
    """
    correlation_id = ai_logger._create_correlation_id()
    
    # Log request
    ai_logger.log_request(correlation_id, operation, provider, request_data)
    
    # Log response or error
    if error:
        ai_logger.log_error(correlation_id, operation, provider, error, request_data)
    elif response_data is not None:
        ai_logger.log_response(correlation_id, operation, provider, response_data, duration_ms)
    
    return correlation_id