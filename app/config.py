"""
إعدادات البوت المركزية
Bot Configuration Settings
"""

# ==================== Detection Settings ====================
DETECTION_CONFIG = {
    'default_sensitivity': 0.7,  # Default detection threshold
    'fuzzy_match_threshold': 0.75,  # Fuzzy matching threshold
    'min_confidence': 0.5,  # Minimum confidence for spam detection
    'max_keywords_per_message': 10,  # Maximum keywords to extract
}

# ==================== Cache Settings ====================
CACHE_CONFIG = {
    'ttl': 3600,  # Time to live in seconds (1 hour)
    'max_size': 1000,  # Maximum cache entries
    'cleanup_interval': 300,  # Cleanup interval in seconds (5 minutes)
}

# ==================== Rate Limiting Settings ====================
RATE_LIMIT_CONFIG = {
    'message_max_requests': 30,  # Max messages per minute
    'message_time_window': 60,  # Time window in seconds
    'command_max_requests': 10,  # Max commands per minute
    'command_time_window': 60,  # Time window in seconds
}

# ==================== Database Settings ====================
DATABASE_CONFIG = {
    'cleanup_days': 30,  # Delete messages older than 30 days
    'batch_size': 100,  # Batch size for database operations
    'connection_timeout': 30,  # Connection timeout in seconds
    'max_retries': 3,  # Maximum retry attempts
}

# ==================== Logging Settings ====================
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'max_log_size': 10485760,  # 10MB
    'backup_count': 5,  # Number of backup files to keep
}

# ==================== Spam Detection Keywords ====================
SPAM_KEYWORDS = {
    # Medical/Health related
    'سكليف': 0.95,
    'اجازة': 0.90,
    'مرضي': 0.85,
    'مستشفي': 0.80,
    'موثق': 0.85,
    'معتمد': 0.80,
    'اعتذار': 0.75,
    'اعذار': 0.75,
    'غياب': 0.70,
    'غيبة': 0.70,
    
    # Service related
    'خدمة': 0.60,
    'عرض': 0.60,
    'فوري': 0.70,
    'سريع': 0.70,
    'إنجاز': 0.75,
    'معالجة': 0.65,
    
    # Action related
    'تصدر': 0.75,
    'تضبط': 0.75,
    'نستقبل': 0.70,
    'نطلع': 0.70,
    'تطلع': 0.70,
    'نسحب': 0.70,
}

# ==================== Username Suspicious Keywords ====================
SUSPICIOUS_USERNAMES = {
    'سكليف': 0.9,
    'اجازة': 0.9,
    'موثق': 0.8,
    'معتمد': 0.8,
    'فوري': 0.7,
    'سريع': 0.7,
    'خدمة': 0.6,
    'عرض': 0.6,
}

# ==================== Obfuscation Detection Settings ====================
OBFUSCATION_CONFIG = {
    'dots_score': 0.2,
    'spaces_score': 0.2,
    'dashes_score': 0.15,
    'special_chars_score': 0.15,
    'mixed_language_score': 0.1,
    'heavy_obfuscation_threshold': 0.5,
}

# ==================== Phone Number Patterns ====================
PHONE_PATTERNS = {
    'saudi': r'\+?966[0-9]{8,9}',  # Saudi Arabia
    'general': r'\+?[0-9]{10,15}',  # General international format
}

# ==================== Message Settings ====================
MESSAGE_CONFIG = {
    'max_message_length': 4096,  # Telegram max message length
    'min_message_length': 1,  # Minimum message length to process
    'spam_delete_delay': 5,  # Delay before deleting spam (seconds)
}

# ==================== Admin Settings ====================
ADMIN_CONFIG = {
    'require_admin_confirmation': True,  # Require admin confirmation for actions
    'log_all_actions': True,  # Log all admin actions
    'max_whitelist_size': 1000,  # Maximum whitelist entries
    'max_blacklist_size': 1000,  # Maximum blacklist entries
}

# ==================== Feature Flags ====================
FEATURES = {
    'enable_caching': True,
    'enable_analytics': True,
    'enable_rate_limiting': True,
    'enable_obfuscation_detection': True,
    'enable_username_filtering': True,
    'enable_auto_cleanup': True,
    'enable_learning': False,  # Self-learning disabled for now
}

# ==================== Error Messages ====================
ERROR_MESSAGES = {
    'no_token': 'TELEGRAM_BOT_TOKEN is not set in environment variables',
    'db_error': 'Database connection error',
    'permission_denied': 'You do not have permission to use this command',
    'invalid_parameter': 'Invalid parameter provided',
    'rate_limit_exceeded': 'Rate limit exceeded. Please try again later.',
    'unknown_error': 'An unknown error occurred',
}

# ==================== Success Messages ====================
SUCCESS_MESSAGES = {
    'bot_started': 'Bot started successfully',
    'bot_stopped': 'Bot stopped',
    'settings_updated': 'Settings updated successfully',
    'message_deleted': 'Message deleted',
    'user_added': 'User added successfully',
    'user_removed': 'User removed successfully',
}
