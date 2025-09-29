"""Decorators for transaction management, cache invalidation, and event emission."""

import asyncio
import functools
import time
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.cache import cache_service
from app.core.events import event_bus


def transactional(func: Callable) -> Callable:
    """Ensure database operations are wrapped in transactions with automatic rollback."""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Find database session in arguments or as instance attribute
        db: Optional[Session] = None
        
        # Check args for Session
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        
        # Check kwargs
        if not db:
            db = kwargs.get('db')
        
        # Check if first arg is a service instance with .db attribute
        if not db and args and hasattr(args[0], 'db'):
            db = args[0].db
        
        if not db:
            raise ValueError("No database session found in function arguments or instance")
        
        try:
            result = await func(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            raise e
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Find database session in arguments or as instance attribute
        db: Optional[Session] = None
        
        # Check args for Session
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        
        # Check kwargs
        if not db:
            db = kwargs.get('db')
        
        # Check if first arg is a service instance with .db attribute
        if not db and args and hasattr(args[0], 'db'):
            db = args[0].db
        
        if not db:
            raise ValueError("No database session found in function arguments or instance")
        
        try:
            result = func(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            raise e
    
    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def cache_invalidate(cache_keys: List[str]):
    """Invalidate specified cache keys after function execution."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Invalidate cache keys
            for key_pattern in cache_keys:
                if '*' in key_pattern:
                    cache_service._invalidate_pattern(key_pattern)
                else:
                    cache_service.redis_client.delete(key_pattern)
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache keys
            for key_pattern in cache_keys:
                if '*' in key_pattern:
                    cache_service._invalidate_pattern(key_pattern)
                else:
                    cache_service.redis_client.delete(key_pattern)
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def event_emit(event_type: str, data_extractor: Optional[Callable] = None):
    """Emit events after function execution."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Extract event data
            if data_extractor:
                event_data = data_extractor(result, *args, **kwargs)
            else:
                event_data = {'result': result}
            
            # Emit event
            await event_bus.emit(event_type, event_data)
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Extract event data
            if data_extractor:
                event_data = data_extractor(result, *args, **kwargs)
            else:
                event_data = {'result': result}
            
            # Emit event (sync version) - safe for both sync and async contexts
            try:
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(event_bus.emit(event_type, event_data))
                except RuntimeError:
                    # No event loop running, create one
                    asyncio.run(event_bus.emit(event_type, event_data))
            except Exception as e:
                print(f"Event emission failed in decorator: {e}")
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def performance_monitor(operation_name: str):
    """Monitor function performance and log metrics."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                print(f"Performance: {operation_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                print(f"Performance: {operation_name} failed after {duration:.3f}s - {e}")
                raise e
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                print(f"Performance: {operation_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                print(f"Performance: {operation_name} failed after {duration:.3f}s - {e}")
                raise e
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Retry function on failure with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)
                        print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"All {max_retries} retries failed: {e}")
            
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)
                        print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        print(f"All {max_retries} retries failed: {e}")
            
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Predefined data extractors for common events
def extract_part_update_data(result, *args, **kwargs) -> Dict[str, Any]:
    """Extract part update data for events."""
    part_id = None
    
    # Try to find part_id in arguments
    for arg in args:
        if isinstance(arg, int):
            part_id = arg
            break
    
    # Try to find in kwargs
    if not part_id:
        part_id = kwargs.get('part_id')
    
    # Try to extract from result
    if not part_id and hasattr(result, 'id'):
        part_id = result.id
    
    return {
        'part_id': part_id,
        'changes': kwargs.get('update_data', {}),
        'updated_by': kwargs.get('updated_by', 'system')
    }


def extract_stock_update_data(result, *args, **kwargs) -> Dict[str, Any]:
    """Extract stock update data for events."""
    part_id = None
    
    # Try to find part_id in arguments
    for arg in args:
        if isinstance(arg, int):
            part_id = arg
            break
    
    # Try to find in kwargs
    if not part_id:
        part_id = kwargs.get('part_id')
    
    # Try to extract from result
    if not part_id and hasattr(result, 'part_id'):
        part_id = result.part_id
    
    return {
        'part_id': part_id,
        'stock_changes': kwargs.get('stock_data', {}),
        'updated_by': kwargs.get('updated_by', 'system')
    }
