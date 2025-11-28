#!/usr/bin/env python3
"""
🤖 بوت حذف الإعلانات المزعجة - ملف البدء الرئيسي
Telegram Spam Killer Bot - Main Entry Point
"""

import os
import sys
import logging
from dotenv import load_dotenv
from telegram.ext import (
    Application, CommandHandler, MessageHandler as TgMessageHandler, filters
)

# استيراد المعالجات والخدمات
from app.handlers.message_handler import MessageHandler
from app.handlers.admin_handler import AdminHandler, AdvancedFeatures
from app.handlers.cleanup_handler import CleanupCommandHandler
# from app.handlers.feedback_handler import FeedbackHandler  # تم إزالتها
from app.utils.commands import CommandRegistry
from app.models.init_db import init_db, SessionLocal

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة
load_dotenv()


async def post_init(application: Application) -> None:
    """تهيئة البوت بعد الإنشاء"""
    try:
        # تسجيل الأوامر في تلقرام
        commands = CommandRegistry.get_all_bot_commands()
        await application.bot.set_my_commands(commands)
        logger.info(f"✅ تم تسجيل {len(commands)} أمر بنجاح")
        
        # طباعة رسالة البدء
        print("\n" + "="*70)
        print("✅ البوت جاهز للاستخدام!")
        print("="*70)
        print("\n💡 اكتب / في القروب لرؤية جميع الأوامر المتاحة\n")
        
    except Exception as e:
        logger.error(f"❌ خطأ في تهيئة البوت: {e}")
        print(f"❌ خطأ في التهيئة: {e}")


def setup_handlers(application: Application):
    """إعداد جميع معالجات الأوامر"""
    
    # إنشاء معالجات الأوامر
    message_handler = MessageHandler()
    admin_handler = AdminHandler()
    advanced_features = AdvancedFeatures()
    
    # ===== الأوامر العامة =====
    application.add_handler(CommandHandler("start", message_handler.start))
    application.add_handler(CommandHandler("help", message_handler.help_command))
    application.add_handler(CommandHandler("stats", message_handler.stats))
    application.add_handler(CommandHandler("settings", message_handler.settings))
    
    # ===== أوامر المسؤولين =====
    application.add_handler(CommandHandler("enable", admin_handler.enable_bot))
    application.add_handler(CommandHandler("disable", admin_handler.disable_bot))
    application.add_handler(CommandHandler("sensitivity", admin_handler.set_sensitivity))
    application.add_handler(CommandHandler("whitelist", admin_handler.manage_whitelist))
    application.add_handler(CommandHandler("blacklist", admin_handler.manage_blacklist))
    application.add_handler(CommandHandler("report", admin_handler.generate_report))
    application.add_handler(CommandHandler("logs", admin_handler.show_logs))
    
    # ===== أوامر الكلمات المفتاحية =====
    application.add_handler(CommandHandler("addkeyword", advanced_features.add_keyword))
    application.add_handler(CommandHandler("removekeyword", advanced_features.remove_keyword))
    application.add_handler(CommandHandler("keywords", advanced_features.list_keywords))
    
    # ===== أوامر التنظيف =====
    cleanup_handlers = CleanupCommandHandler.get_handlers()
    for handler in cleanup_handlers:
        application.add_handler(handler)
    
        # ===== أوامر التغذية الراجعة والتعلم الذاتي =====
    feedback_handlers = FeedbackHandler.get_handlers()
    for handler in feedback_handlers:
        application.add_handler(handler)
    
    # ===== معالج الرسائل العام =====
    application.add_handler(
        TgMessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler.handle_message
        )
    )


def main():
    """الدالة الرئيسية"""
    
    # الحصول على رمز البوت
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("\n" + "="*70)
        print("❌ خطأ: TELEGRAM_BOT_TOKEN غير موجود")
        print("="*70)
        print("\n📝 الحل:")
        print("1. افتح ملف .env")
        print("2. أضف السطر التالي:")
        print("   TELEGRAM_BOT_TOKEN=your_token_here")
        print("3. استبدل your_token_here برمز البوت الخاص بك")
        print("\n💡 للحصول على رمز البوت:")
        print("   - افتح تلقرام وابحث عن @BotFather")
        print("   - أرسل /newbot واتبع التعليمات")
        print("\n" + "="*70 + "\n")
        return
    
    print("\n" + "="*70)
    print("🚀 جاري بدء بوت حذف الإعلانات المزعجة...")
    print("="*70 + "\n")
    
    try:
        # تهيئة قاعدة البيانات
        print("📦 جاري إعداد قاعدة البيانات...")
        if init_db():
            print("✅ تم إعداد قاعدة البيانات بنجاح\n")
        else:
            print("⚠️ تحذير: قد يكون هناك مشكلة في قاعدة البيانات\n")
        
        # إنشاء التطبيق
        application = (
            Application.builder()
            .token(token)
            .post_init(post_init)
            .build()
        )
        
        # إعداد المعالجات
        setup_handlers(application)
        
        # تشغيل البوت
        print("✅ البوت يعمل الآن... اضغط Ctrl+C للإيقاف\n")
        application.run_polling()
    
    except KeyboardInterrupt:
        print("\n" + "="*70)
        print("⛔ تم إيقاف البوت")
        print("="*70 + "\n")
    
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ خطأ في تشغيل البوت: {e}")
        print("="*70 + "\n")
        logger.error(f"خطأ في تشغيل البوت: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
