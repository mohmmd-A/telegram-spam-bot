import logging
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler as TgMessageHandler, filters
)
from dotenv import load_dotenv

from app.handlers.message_handler import MessageHandler
from app.handlers.admin_handler import AdminHandler, AdvancedFeatures
from app.handlers.cleanup_handler import ImprovedCleanupHandler as CleanupHandler
from app.models.database import init_db

# تحميل متغيرات البيئة
load_dotenv()

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class SpamBot:
    """فئة البوت الرئيسية"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN غير محدد في متغيرات البيئة")
        
        self.admin_id = os.getenv("TELEGRAM_ADMIN_ID")
        self.application = None
    
    def setup(self):
        """إعداد البوت"""
        # إنشاء قاعدة البيانات
        init_db()
        logger.info("تم إنشاء قاعدة البيانات")
        
        # إنشاء التطبيق
        self.application = Application.builder().token(self.token).build()
        
        # ========== أوامر أساسية ==========
        self.application.add_handler(
            CommandHandler("start", MessageHandler.start)
        )
        self.application.add_handler(
            CommandHandler("help", MessageHandler.help_command)
        )
        self.application.add_handler(
            CommandHandler("stats", MessageHandler.stats)
        )
        self.application.add_handler(
            CommandHandler("settings", MessageHandler.settings)
        )
        
        # ========== أوامر المسؤولين ==========
        self.application.add_handler(
            CommandHandler("whitelist", AdminHandler.manage_whitelist)
        )
        self.application.add_handler(
            CommandHandler("blacklist", AdminHandler.manage_blacklist)
        )
        self.application.add_handler(
            CommandHandler("sensitivity", AdminHandler.set_sensitivity)
        )
        self.application.add_handler(
            CommandHandler("enable", AdminHandler.enable_bot)
        )
        self.application.add_handler(
            CommandHandler("disable", AdminHandler.disable_bot)
        )
        self.application.add_handler(
            CommandHandler("report", AdminHandler.generate_report)
        )
        self.application.add_handler(
            CommandHandler("logs", AdminHandler.show_logs)
        )
        
        # ========== المزايا المتقدمة ==========
        self.application.add_handler(
            CommandHandler("addkeyword", AdvancedFeatures.add_keyword)
        )
        self.application.add_handler(
            CommandHandler("removekeyword", AdvancedFeatures.remove_keyword)
        )
        
        # ========== أوامر التنظيف ==========
        self.application.add_handler(
            CommandHandler("cleanup_old", CleanupHandler.cleanup_old_messages)
        )
        self.application.add_handler(
            CommandHandler("cleanup_user", CleanupHandler.cleanup_user_messages)
        )
        self.application.add_handler(
            CommandHandler("archive", CleanupHandler.archive_summary)
        )
        
        # ========== معالج الرسائل ==========
        self.application.add_handler(
            TgMessageHandler(filters.TEXT & ~filters.COMMAND, MessageHandler.handle_message)
        )
        
        logger.info("تم إعداد معالجات البوت")
    
    async def start(self):
        """بدء البوت"""
        if not self.application:
            self.setup()
        
        logger.info("🚀 بدء البوت...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("✅ البوت يعمل بنجاح!")
    
    async def stop(self):
        """إيقاف البوت"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
            logger.info("🛑 تم إيقاف البوت")


def create_bot() -> SpamBot:
    """إنشاء مثيل من البوت"""
    return SpamBot()
