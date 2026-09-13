"""
Error Handling and Validation Utilities
"""

import logging
import asyncio
from typing import Any, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def handle_errors(
    default_return: Any = None,
    log_error: bool = True,
    reraise: bool = False
):
    """
    Decorator for error handling.
    
    Args:
        default_return: Value to return on error
        log_error: Whether to log errors
        reraise: Whether to re-raise exceptions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                if reraise:
                    raise
                return default_return
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                if reraise:
                    raise
                return default_return
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def validate_agent_output(output: Any) -> bool:
    """
    Validate agent output.
    
    Args:
        output: Agent output to validate
    
    Returns:
        True if valid, False otherwise
    """
    if output is None:
        return False
    
    if isinstance(output, str):
        return len(output.strip()) > 0
    
    if isinstance(output, dict):
        return len(output) > 0
    
    return True


def safe_agent_run(agent, query: str, session=None, max_retries: int = 3):
    """
    Safely run an agent with retry logic.
    
    Args:
        agent: Agent to run
        query: Query string
        session: Optional session
        max_retries: Maximum retry attempts
    
    Returns:
        Agent result or None on failure
    """
    from agents import Runner
    
    for attempt in range(max_retries):
        try:
            result = Runner.run_sync(agent, query, session=session)
            if validate_agent_output(result.final_output if hasattr(result, 'final_output') else result):
                return result
        except Exception as e:
            logger.warning(f"Agent run attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"All {max_retries} attempts failed")
                return None
    
    return None

