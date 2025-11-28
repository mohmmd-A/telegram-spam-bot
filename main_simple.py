"""
ملف البدء الرئيسي - النسخة المبسطة والمصححة
Main Entry Point - Simplified and Fixed Version
"""

import os
import logging
from dotenv import load_dotenv
from telegram.ext import (
    Application, CommandHandler, MessageHandler as TgMessageHandler, filters
)
from app.handlers.message_handler import MessageHandler
from app.handlers.admin_handler import AdminHandler, AdvancedFeatures
from app.handlers.cleanup_handler import CleanupCommandHandler
from app.utils.commands import CommandRegistry

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
    logger.info("🚀 جاري تهيئة البوت...")
    
    try:
        # تسجيل الأوامر في تلقرام
        commands = CommandRegistry.get_all_bot_commands()
        await application.bot.set_my_commands(commands)
        
        logger.info(f"✅ تم تسجيل {len(commands)} أمر بنجاح")
        
        # طباعة الأوامر المسجلة
        print("\n" + "="*70)
        print("📋 الأوامر المسجلة والمتاحة:")
        print("="*70)
        
        print("\n🟢 الأوامر العامة:")
        for cmd in CommandRegistry.get_general_commands():
            print(f"  /{cmd.command:<20} - {cmd.description}")
        
        print("\n🔵 أوامر المسؤولين:")
        for cmd in CommandRegistry.get_admin_commands():
            print(f"  /{cmd.command:<20} - {cmd.description}")
        
        print("\n🟡 أوامر التنظيف:")
        for cmd in CommandRegistry.get_cleanup_commands():
            print(f"  /{cmd.command:<20} - {cmd.description}")
        
        print("\n🟣 أوامر الكلمات المفتاحية:")
        for cmd in CommandRegistry.get_keyword_commands():
            print(f"  /{cmd.command:<20} - {cmd.description}")
        
        print("\n🟠 الأوامر المتقدمة:")
        for cmd in CommandRegistry.get_advanced_commands():
            print(f"  /{cmd.command:<20} - {cmd.description}")
        
        print("\n" + "="*70)
        print("✅ البوت جاهز للاستخدام!")
        print("="*70)
        print("\n💡 اكتب / في القروب لرؤية جميع الأوامر المتاحة\n")
        
    except Exception as e:
        logger.error(f"❌ خطأ في تهيئة البوت: {e}")


def main():
    """الدالة الرئيسية"""
    
    # الحصول على رمز البوت
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN غير موجود في متغيرات البيئة")
        print("\n⚠️  تأكد من إضافة TELEGRAM_BOT_TOKEN في ملف .env")
        print("📝 اكتب: TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    print("\n" + "="*70)
    print("🚀 جاري بدء بوت حذف الإعلانات المزعجة...")
    print("="*70 + "\n")
    
    # إنشاء التطبيق
    application = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )
    
    # إنشاء معالجات الأوامر
    message_handler = MessageHandler()
    admin_handler = AdminHandler()
    advanced_features = AdvancedFeatures()
    
    # ===== تسجيل معالجات الأوامر العامة =====
    application.add_handler(CommandHandler("start", message_handler.start))
    application.add_handler(CommandHandler("help", message_handler.help_command))
    application.add_handler(CommandHandler("stats", message_handler.stats))
    application.add_handler(CommandHandler("settings", message_handler.settings))
    
    # ===== تسجيل معالجات أوامر المسؤولين =====
    application.add_handler(CommandHandler("enable", admin_handler.enable_bot))
    application.add_handler(CommandHandler("disable", admin_handler.disable_bot))
    application.add_handler(CommandHandler("sensitivity", admin_handler.set_sensitivity))
    application.add_handler(CommandHandler("whitelist", admin_handler.manage_whitelist))
    application.add_handler(CommandHandler("blacklist", admin_handler.manage_blacklist))
    application.add_handler(CommandHandler("report", admin_handler.generate_report))
    application.add_handler(CommandHandler("logs", admin_handler.show_logs))
    
    # ===== تسجيل معالجات أوامر الكلمات المفتاحية =====
    application.add_handler(CommandHandler("addkeyword", advanced_features.add_keyword))
    application.add_handler(CommandHandler("removekeyword", advanced_features.remove_keyword))
    application.add_handler(CommandHandler("keywords", advanced_features.list_keywords))
    
    # ===== تسجيل معالجات أوامر التنظيف =====
    cleanup_handlers = CleanupCommandHandler.get_handlers()
    for handler in cleanup_handlers:
        application.add_handler(handler)
    
    # ===== تسجيل معالج الرسائل العام =====
    application.add_handler(
        TgMessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler.handle_message
        )
    )
    
    # تشغيل البوت
    try:
        print("✅ البوت يعمل الآن... اضغط Ctrl+C للإيقاف\n")
        application.run_polling()
    except KeyboardInterrupt:
        print("\n" + "="*70)
        print("⛔ تم إيقاف البوت")
        print("="*70)
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        print(f"\n❌ خطأ: {e}")
        raise


if __name__ == '__main__':
    main()
