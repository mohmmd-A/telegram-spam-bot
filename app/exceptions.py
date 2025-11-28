"""
استثناءات مخصصة للبوت
Custom Bot Exceptions
"""


class BotException(Exception):
    """Base exception for bot errors"""
    pass


class DatabaseError(BotException):
    """Database operation error"""
    pass


class DetectionError(BotException):
    """Spam detection error"""
    pass


class ConfigurationError(BotException):
    """Configuration error"""
    pass


class PermissionError(BotException):
    """Permission denied error"""
    pass


class ValidationError(BotException):
    """Input validation error"""
    pass


class RateLimitError(BotException):
    """Rate limit exceeded error"""
    pass


class MessageDeletionError(BotException):
    """Message deletion error"""
    pass


class UserNotFoundError(BotException):
    """User not found error"""
    pass


class ChatNotFoundError(BotException):
    """Chat not found error"""
    pass


class InvalidParameterError(BotException):
    """Invalid parameter error"""
    pass


class TimeoutError(BotException):
    """Operation timeout error"""
    pass
