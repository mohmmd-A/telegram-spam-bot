"""
فئة البوت الرئيسية المحدثة
Updated Main Bot Class
"""

import logging
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler as TgMessageHandler, filters
)
from dotenv import load_dotenv

from app.handlers.message_handler import MessageHandler, CommandHandler as BasicCommandHandler
from app.handlers.admin_handler import AdminHandler, AdvancedFeatures
from app.handlers.cleanup_handler import CleanupCommandHandler
from app.utils.commands import CommandRegistry
from app.utils.setup import setup_bot_defaults

load_dotenv()

logger = logging.getLogger(__name__)


class SpamBotManager:
    """مدير البوت الرئيسي"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("❌ TELEGRAM_BOT_TOKEN غير موجود في متغيرات البيئة")
        
        self.application = None
        self.message_handler = MessageHandler()
        self.admin_handler = AdminHandler()
        self.advanced_features = AdvancedFeatures()
    
    async def post_init(self, application: Application) -> None:
        """تهيئة البوت بعد الإنشاء"""
        logger.info("🚀 جاري تهيئة البوت...")
        
        # إعداد أوامر البوت
        await setup_bot_defaults(application)
        
        logger.info("✅ تم تهيئة البوت بنجاح")
    
    def create_application(self) -> Application:
        """إنشاء تطبيق البوت"""
        
        # إنشاء التطبيق
        self.application = (
            Application.builder()
            .token(self.token)
            .post_init(self.post_init)
            .build()
        )
        
        # تسجيل معالجات الأوامر العامة
        self._register_general_commands()
        
        # تسجيل معالجات أوامر المسؤولين
        self._register_admin_commands()
        
        # تسجيل معالجات أوامر التنظيف
        self._register_cleanup_commands()
        
        # تسجيل معالج الرسائل العام
        self._register_message_handlers()
        
        return self.application
    
    def _register_general_commands(self):
        """تسجيل الأوامر العامة"""
        
        # أوامر أساسية
        self.application.add_handler(
            CommandHandler("start", self.message_handler.start)
        )
        self.application.add_handler(
            CommandHandler("help", self.message_handler.help_command)
        )
        self.application.add_handler(
            CommandHandler("stats", self.message_handler.stats)
        )
        self.application.add_handler(
            CommandHandler("settings", self.message_handler.settings)
        )
    
    def _register_admin_commands(self):
        """تسجيل أوامر المسؤولين"""
        
        # أوامر الإدارة الأساسية
        self.application.add_handler(
            CommandHandler("enable", self.admin_handler.enable_bot)
        )
        self.application.add_handler(
            CommandHandler("disable", self.admin_handler.disable_bot)
        )
        self.application.add_handler(
            CommandHandler("sensitivity", self.admin_handler.set_sensitivity)
        )
        self.application.add_handler(
            CommandHandler("whitelist", self.admin_handler.manage_whitelist)
        )
        self.application.add_handler(
            CommandHandler("blacklist", self.admin_handler.manage_blacklist)
        )
        self.application.add_handler(
            CommandHandler("report", self.admin_handler.generate_report)
        )
        self.application.add_handler(
            CommandHandler("logs", self.admin_handler.show_logs)
        )
        
        # أوامر الكلمات المفتاحية
        self.application.add_handler(
            CommandHandler("addkeyword", self.advanced_features.add_keyword)
        )
        self.application.add_handler(
            CommandHandler("removekeyword", self.advanced_features.remove_keyword)
        )
        self.application.add_handler(
            CommandHandler("keywords", self.advanced_features.list_keywords)
        )
    
    def _register_cleanup_commands(self):
        """تسجيل أوامر التنظيف"""
        
        # الحصول على معالجات التنظيف
        cleanup_handlers = CleanupCommandHandler.get_handlers()
        
        for handler in cleanup_handlers:
            self.application.add_handler(handler)
    
    def _register_message_handlers(self):
        """تسجيل معالجات الرسائل"""
        
        # معالج الرسائل العام
        self.application.add_handler(
            TgMessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.message_handler.handle_message
            )
        )
    
    def run(self):
        """تشغيل البوت"""
        print("\n" + "="*60)
        print("🚀 جاري بدء بوت حذف الإعلانات المزعجة...")
        print("="*60)
        
        try:
            self.application.run_polling()
        except KeyboardInterrupt:
            print("\n" + "="*60)
            print("⛔ تم إيقاف البوت")
            print("="*60)
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل البوت: {e}")
            raise


def create_bot() -> SpamBotManager:
    """إنشاء مثيل من مدير البوت"""
    return SpamBotManager()
