"""
دوال مساعدة عامة
Common Helper Functions
"""

import logging
from typing import Any, Callable, Optional, Dict, List
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


def safe_async_handler(func: Callable) -> Callable:
    """
    Decorator for safe async handler execution with error handling
    
    Args:
        func: Async function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
    
    return wrapper


def validate_input(required_fields: List[str]) -> Callable:
    """
    Decorator for input validation
    
    Args:
        required_fields: List of required field names
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for field in required_fields:
                if field not in kwargs or kwargs[field] is None:
                    logger.warning(f"Missing required field: {field}")
                    raise ValueError(f"Missing required field: {field}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0) -> Callable:
    """
    Decorator for retrying failed operations
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
        
        return wrapper
    
    return decorator


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format error message for user display
    
    Args:
        error: Exception object
        context: Additional context information
        
    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        return f"❌ خطأ في {context}: {error_msg}"
    else:
        return f"❌ خطأ: {error_msg}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_number(num: int, lang: str = "ar") -> str:
    """
    Format number with thousands separator
    
    Args:
        num: Number to format
        lang: Language ('ar' for Arabic, 'en' for English)
        
    Returns:
        Formatted number
    """
    if lang == "ar":
        # Convert to Arabic numerals
        arabic_numerals = "٠١٢٣٤٥٦٧٨٩"
        formatted = f"{num:,}"
        return "".join(arabic_numerals[int(d)] if d.isdigit() else d for d in formatted)
    else:
        return f"{num:,}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format percentage value
    
    Args:
        value: Value between 0 and 1
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    percentage = value * 100
    return f"{percentage:.{decimals}f}%"


def format_duration(seconds: int) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds} ثانية"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} دقيقة"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} ساعة"
    else:
        days = seconds // 86400
        return f"{days} يوم"


def is_valid_user_id(user_id: Any) -> bool:
    """
    Validate user ID
    
    Args:
        user_id: User ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        uid = int(user_id)
        return uid > 0
    except (ValueError, TypeError):
        return False


def is_valid_chat_id(chat_id: Any) -> bool:
    """
    Validate chat ID
    
    Args:
        chat_id: Chat ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        cid = int(chat_id)
        return cid != 0
    except (ValueError, TypeError):
        return False


def sanitize_text(text: str) -> str:
    """
    Sanitize text for safe display
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove control characters
    text = "".join(char for char in text if ord(char) >= 32 or char in '\n\t')
    # Limit length
    return text[:1000]


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    
    return result


def get_nested_value(data: Dict, path: str, default: Any = None) -> Any:
    """
    Get nested dictionary value using dot notation
    
    Args:
        data: Dictionary to search
        path: Path using dot notation (e.g., 'user.profile.name')
        default: Default value if not found
        
    Returns:
        Value or default
    """
    keys = path.split('.')
    value = data
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value
