"""
سجل الأوامر مع الأوصاف
Commands Registry with Descriptions
"""

from telegram import BotCommand, BotCommandScope, BotCommandScopeDefault
from typing import List, Dict


class CommandRegistry:
    """سجل جميع أوامر البوت مع الأوصاف"""
    
    # أوامر عامة للجميع
    GENERAL_COMMANDS = {
        "start": "🚀 بدء البوت والحصول على المساعدة",
        "help": "📖 عرض قائمة المساعدة الكاملة",
        "stats": "📊 عرض إحصائيات القروب",
        "settings": "⚙️ عرض إعدادات البوت",
    }
    
    # أوامر المسؤولين
    ADMIN_COMMANDS = {
        "enable": "✅ تفعيل البوت",
        "disable": "❌ تعطيل البوت",
        "sensitivity": "📈 تعديل حساسية الكشف (0.1-1.0)",
        "whitelist": "⚪ إدارة القائمة البيضاء",
        "blacklist": "⚫ إدارة القائمة السوداء",
        "report": "📋 عرض التقرير الشامل",
        "logs": "📝 عرض السجلات",
    }
    
    # أوامر التنظيف والأرشيف
    CLEANUP_COMMANDS = {
        "cleanup_old": "🧹 حذف الرسائل الإعلانية القديمة",
        "cleanup_user": "👤 حذف رسائل مستخدم معين",
        "archive_summary": "📦 عرض ملخص الأرشيف",
        "export_archive": "💾 تصدير الأرشيف (json/csv)",
    }
    
    # أوامر إدارة الكلمات المفتاحية
    KEYWORD_COMMANDS = {
        "addkeyword": "➕ إضافة كلمة مفتاحية جديدة",
        "removekeyword": "➖ إزالة كلمة مفتاحية",
        "keywords": "📚 عرض قائمة الكلمات المفتاحية",
    }
    
    # أوامر متقدمة
    ADVANCED_COMMANDS = {
        "obfuscation_check": "🔍 فحص رسالة للتمويه",
        "normalize_text": "📝 تطبيع نص",
    }
    
    @staticmethod
    def get_all_commands() -> Dict[str, str]:
        """الحصول على جميع الأوامر"""
        return {
            **CommandRegistry.GENERAL_COMMANDS,
            **CommandRegistry.ADMIN_COMMANDS,
            **CommandRegistry.CLEANUP_COMMANDS,
            **CommandRegistry.KEYWORD_COMMANDS,
            **CommandRegistry.ADVANCED_COMMANDS,
        }
    
    @staticmethod
    def get_general_commands() -> List[BotCommand]:
        """الحصول على أوامر عامة للجميع"""
        return [
            BotCommand(command, description)
            for command, description in CommandRegistry.GENERAL_COMMANDS.items()
        ]
    
    @staticmethod
    def get_admin_commands() -> List[BotCommand]:
        """الحصول على أوامر المسؤولين"""
        return [
            BotCommand(command, description)
            for command, description in CommandRegistry.ADMIN_COMMANDS.items()
        ]
    
    @staticmethod
    def get_cleanup_commands() -> List[BotCommand]:
        """الحصول على أوامر التنظيف"""
        return [
            BotCommand(command, description)
            for command, description in CommandRegistry.CLEANUP_COMMANDS.items()
        ]
    
    @staticmethod
    def get_keyword_commands() -> List[BotCommand]:
        """الحصول على أوامر الكلمات المفتاحية"""
        return [
            BotCommand(command, description)
            for command, description in CommandRegistry.KEYWORD_COMMANDS.items()
        ]
    
    @staticmethod
    def get_advanced_commands() -> List[BotCommand]:
        """الحصول على الأوامر المتقدمة"""
        return [
            BotCommand(command, description)
            for command, description in CommandRegistry.ADVANCED_COMMANDS.items()
        ]
    
    @staticmethod
    def get_all_bot_commands() -> List[BotCommand]:
        """الحصول على جميع أوامر البوت"""
        all_commands = []
        all_commands.extend(CommandRegistry.get_general_commands())
        all_commands.extend(CommandRegistry.get_admin_commands())
        all_commands.extend(CommandRegistry.get_cleanup_commands())
        all_commands.extend(CommandRegistry.get_keyword_commands())
        all_commands.extend(CommandRegistry.get_advanced_commands())
        return all_commands
    
    @staticmethod
    def get_help_text() -> str:
        """الحصول على نص المساعدة الكامل"""
        help_text = """
🤖 **بوت حذف الإعلانات المزعجة**

📌 **الأوامر العامة:**
"""
        
        for command, description in CommandRegistry.GENERAL_COMMANDS.items():
            help_text += f"\n/{command} - {description}"
        
        help_text += "\n\n📌 **أوامر المسؤولين:**"
        for command, description in CommandRegistry.ADMIN_COMMANDS.items():
            help_text += f"\n/{command} - {description}"
        
        help_text += "\n\n📌 **أوامر التنظيف والأرشيف:**"
        for command, description in CommandRegistry.CLEANUP_COMMANDS.items():
            help_text += f"\n/{command} - {description}"
        
        help_text += "\n\n📌 **أوامر الكلمات المفتاحية:**"
        for command, description in CommandRegistry.KEYWORD_COMMANDS.items():
            help_text += f"\n/{command} - {description}"
        
        help_text += "\n\n📌 **الأوامر المتقدمة:**"
        for command, description in CommandRegistry.ADVANCED_COMMANDS.items():
            help_text += f"\n/{command} - {description}"
        
        help_text += """

💡 **نصائح:**
• اكتب / لرؤية جميع الأوامر المتاحة
• استخدم /help للمزيد من المعلومات
• فقط المسؤولون يمكنهم استخدام أوامر الإدارة
"""
        
        return help_text
    
    @staticmethod
    def get_command_description(command: str) -> str:
        """الحصول على وصف أمر معين"""
        all_commands = CommandRegistry.get_all_commands()
        return all_commands.get(command, "أمر غير معروف")


# إنشاء مثيل عام
command_registry = CommandRegistry()
