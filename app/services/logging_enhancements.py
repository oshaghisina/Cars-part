"""
Enhanced Logging for Parts & Inventory Integration
================================================

This module provides structured logging for the parts and inventory system,
including performance metrics, error tracking, and audit trails.
"""

import json
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

# Configure structured logging
logger = logging.getLogger(__name__)


class PartsAuditLogger:
    """Audit logger for parts operations."""

    @staticmethod
    def log_part_creation(part_id: int, part_data: Dict, user_id: Optional[int] = None):
        """Log part creation with audit trail."""
        audit_data = {
            "event": "part_created",
            "timestamp": datetime.utcnow().isoformat(),
            "part_id": part_id,
            "part_data": part_data,
            "user_id": user_id,
            "operation": "CREATE",
        }
        logger.info(f"Parts Audit: {json.dumps(audit_data)}")

    @staticmethod
    def log_part_update(
        part_id: int, old_data: Dict, new_data: Dict, user_id: Optional[int] = None
    ):
        """Log part updates with before/after data."""
        audit_data = {
            "event": "part_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "part_id": part_id,
            "old_data": old_data,
            "new_data": new_data,
            "user_id": user_id,
            "operation": "UPDATE",
        }
        logger.info(f"Parts Audit: {json.dumps(audit_data)}")

    @staticmethod
    def log_price_update(part_id: int, price_data: Dict, user_id: Optional[int] = None):
        """Log price updates."""
        audit_data = {
            "event": "price_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "part_id": part_id,
            "price_data": price_data,
            "user_id": user_id,
            "operation": "PRICE_UPDATE",
        }
        logger.info(f"Parts Audit: {json.dumps(audit_data)}")

    @staticmethod
    def log_stock_update(part_id: int, stock_data: Dict, user_id: Optional[int] = None):
        """Log stock updates."""
        audit_data = {
            "event": "stock_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "part_id": part_id,
            "stock_data": stock_data,
            "user_id": user_id,
            "operation": "STOCK_UPDATE",
        }
        logger.info(f"Parts Audit: {json.dumps(audit_data)}")


class PartsPerformanceLogger:
    """Performance logger for parts operations."""

    @staticmethod
    def log_api_request(
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        user_id: Optional[int] = None,
        error: Optional[str] = None,
    ):
        """Log API request performance."""
        perf_data = {
            "event": "api_request",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "response_time_ms": round(response_time * 1000, 2),
            "status_code": status_code,
            "user_id": user_id,
            "error": error,
        }

        if error:
            logger.warning(f"Parts Performance: {json.dumps(perf_data)}")
        else:
            logger.info(f"Parts Performance: {json.dumps(perf_data)}")

    @staticmethod
    def log_database_query(
        query_type: str,
        table: str,
        duration: float,
        rows_affected: Optional[int] = None,
        error: Optional[str] = None,
    ):
        """Log database query performance."""
        query_data = {
            "event": "database_query",
            "timestamp": datetime.utcnow().isoformat(),
            "query_type": query_type,
            "table": table,
            "duration_ms": round(duration * 1000, 2),
            "rows_affected": rows_affected,
            "error": error,
        }

        if error:
            logger.error(f"Parts Performance: {json.dumps(query_data)}")
        else:
            logger.info(f"Parts Performance: {json.dumps(query_data)}")


class PartsErrorLogger:
    """Error logger for parts operations."""

    @staticmethod
    def log_api_error(
        endpoint: str,
        method: str,
        error: Exception,
        request_data: Optional[Dict] = None,
        user_id: Optional[int] = None,
    ):
        """Log API errors with context."""
        error_data = {
            "event": "api_error",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "request_data": request_data,
            "user_id": user_id,
        }
        logger.error(f"Parts Error: {json.dumps(error_data)}", exc_info=True)

    @staticmethod
    def log_database_error(
        operation: str, table: str, error: Exception, query_data: Optional[Dict] = None
    ):
        """Log database errors with context."""
        error_data = {
            "event": "database_error",
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "table": table,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "query_data": query_data,
        }
        logger.error(f"Parts Error: {json.dumps(error_data)}", exc_info=True)

    @staticmethod
    def log_business_logic_error(
        operation: str, part_id: Optional[int], error: Exception, context: Optional[Dict] = None
    ):
        """Log business logic errors."""
        error_data = {
            "event": "business_logic_error",
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "part_id": part_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
        }
        logger.error(f"Parts Error: {json.dumps(error_data)}", exc_info=True)


def log_performance(operation_name: str):
    """Decorator to log performance of operations."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                duration = time.time() - start_time
                PartsPerformanceLogger.log_api_request(
                    endpoint=operation_name,
                    method="INTERNAL",
                    response_time=duration,
                    status_code=500 if error else 200,
                    error=error,
                )

        return wrapper

    return decorator


def log_database_operation(table: str, operation: str):
    """Decorator to log database operations."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            rows_affected = None

            try:
                result = func(*args, **kwargs)
                # Try to determine rows affected (rough estimate)
                if isinstance(result, list):
                    rows_affected = len(result)
                elif result is not None:
                    rows_affected = 1
                return result
            except Exception as e:
                error = str(e)
                PartsErrorLogger.log_database_error(operation, table, e)
                raise
            finally:
                duration = time.time() - start_time
                PartsPerformanceLogger.log_database_query(
                    query_type=operation,
                    table=table,
                    duration=duration,
                    rows_affected=rows_affected,
                    error=error,
                )

        return wrapper

    return decorator


class PartsHealthChecker:
    """Health checker for parts system."""

    @staticmethod
    def check_database_health(db: Session) -> Dict[str, Any]:
        """Check database health for parts system."""
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "component": "parts_database",
            "status": "healthy",
            "checks": {},
        }

        try:
            # Check if required tables exist
            from sqlalchemy import inspect

            inspector = inspect(db.bind)
            tables = inspector.get_table_names()

            required_tables = ["parts", "stock_levels", "prices_new"]
            missing_tables = [table for table in required_tables if table not in tables]

            health_data["checks"]["required_tables"] = {
                "status": "healthy" if not missing_tables else "unhealthy",
                "missing_tables": missing_tables,
            }

            # Check parts count
            from app.db.models import Part

            parts_count = db.query(Part).count()
            health_data["checks"]["parts_count"] = {
                "status": "healthy" if parts_count > 0 else "warning",
                "count": parts_count,
            }

            # Check if any parts have price/stock data
            from app.models.stock_models import PartPrice, StockLevel

            parts_with_price = db.query(PartPrice).count()
            parts_with_stock = db.query(StockLevel).count()

            health_data["checks"]["price_coverage"] = {
                "status": "healthy" if parts_with_price > 0 else "warning",
                "parts_with_price": parts_with_price,
                "total_parts": parts_count,
                "coverage_percent": (
                    round((parts_with_price / parts_count * 100), 2) if parts_count > 0 else 0
                ),
            }

            health_data["checks"]["stock_coverage"] = {
                "status": "healthy" if parts_with_stock > 0 else "warning",
                "parts_with_stock": parts_with_stock,
                "total_parts": parts_count,
                "coverage_percent": (
                    round((parts_with_stock / parts_count * 100), 2) if parts_count > 0 else 0
                ),
            }

            # Overall status
            all_healthy = all(
                check["status"] == "healthy" for check in health_data["checks"].values()
            )
            health_data["status"] = "healthy" if all_healthy else "degraded"

        except Exception as e:
            health_data["status"] = "unhealthy"
            health_data["error"] = str(e)
            PartsErrorLogger.log_database_error("health_check", "parts_system", e)

        logger.info(f"Parts Health Check: {json.dumps(health_data)}")
        return health_data


def setup_parts_logging():
    """Set up structured logging for parts system."""
    # Create a dedicated handler for parts logs
    parts_handler = logging.FileHandler("logs/parts.log")
    parts_handler.setLevel(logging.INFO)

    # Create formatter for structured logs
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parts_handler.setFormatter(formatter)

    # Add handler to parts logger
    parts_logger = logging.getLogger("app.services.parts_enhanced_service")
    parts_logger.addHandler(parts_handler)
    parts_logger.setLevel(logging.INFO)

    # Ensure logs directory exists
    import os

    os.makedirs("logs", exist_ok=True)
