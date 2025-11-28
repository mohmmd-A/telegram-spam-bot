import logging
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler as TgMessageHandler, filters
)
from dotenv import load_dotenv

from app.handlers.message_handler import MessageHandler, CommandHandler as BasicCommandHandler
from app.handlers.admin_handler import AdminHandler, AdvancedFeatures
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
            CommandHandler("start", BasicCommandHandler.start_command)
        )
        self.application.add_handler(
            CommandHandler("help", BasicCommandHandler.help_command)
        )
        self.application.add_handler(
            CommandHandler("stats", BasicCommandHandler.stats_command)
        )
        self.application.add_handler(
            CommandHandler("settings", BasicCommandHandler.settings_command)
        )
        
        # ========== أوامر المسؤولين ==========
        self.application.add_handler(
            CommandHandler("whitelist", AdminHandler.whitelist_command)
        )
        self.application.add_handler(
            CommandHandler("blacklist", AdminHandler.blacklist_command)
        )
        self.application.add_handler(
            CommandHandler("sensitivity", AdminHandler.sensitivity_command)
        )
        self.application.add_handler(
            CommandHandler("enable", AdminHandler.enable_command)
        )
        self.application.add_handler(
            CommandHandler("disable", AdminHandler.disable_command)
        )
        self.application.add_handler(
            CommandHandler("report", AdminHandler.report_command)
        )
        self.application.add_handler(
            CommandHandler("logs", AdminHandler.logs_command)
        )
        
        # ========== المزايا المتقدمة ==========
        self.application.add_handler(
            CommandHandler("addkeyword", AdvancedFeatures.add_keyword_command)
        )
        self.application.add_handler(
            CommandHandler("removekeyword", AdvancedFeatures.removekeyword_command)
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
