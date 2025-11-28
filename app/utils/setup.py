"""
إعداد البوت وتسجيل الأوامر
Bot Setup and Command Registration
"""

from telegram.ext import Application
from app.utils.commands import CommandRegistry
import logging

logger = logging.getLogger(__name__)


async def setup_bot_commands(application: Application):
    """
    إعداد أوامر البوت وتسجيلها في تلقرام
    
    هذا يسمح للمستخدمين برؤية الأوامر المتاحة عند كتابة /
    """
    
    try:
        # الحصول على جميع الأوامر
        commands = CommandRegistry.get_all_bot_commands()
        
        # تسجيل الأوامر
        await application.bot.set_my_commands(commands)
        
        logger.info(f"✅ تم تسجيل {len(commands)} أمر بنجاح")
        
        # طباعة الأوامر المسجلة
        print("\n" + "="*60)
        print("📋 الأوامر المسجلة:")
        print("="*60)
        
        print("\n🟢 الأوامر العامة:")
        for cmd in CommandRegistry.get_general_commands():
            print(f"  /{cmd.command} - {cmd.description}")
        
        print("\n🔵 أوامر المسؤولين:")
        for cmd in CommandRegistry.get_admin_commands():
            print(f"  /{cmd.command} - {cmd.description}")
        
        print("\n🟡 أوامر التنظيف:")
        for cmd in CommandRegistry.get_cleanup_commands():
            print(f"  /{cmd.command} - {cmd.description}")
        
        print("\n🟣 أوامر الكلمات المفتاحية:")
        for cmd in CommandRegistry.get_keyword_commands():
            print(f"  /{cmd.command} - {cmd.description}")
        
        print("\n🟠 الأوامر المتقدمة:")
        for cmd in CommandRegistry.get_advanced_commands():
            print(f"  /{cmd.command} - {cmd.description}")
        
        print("\n" + "="*60)
        print("✅ البوت جاهز للاستخدام!")
        print("="*60 + "\n")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ خطأ في تسجيل الأوامر: {e}")
        return False


async def setup_bot_description(application: Application):
    """
    إعداد وصف البوت
    """
    
    try:
        description = (
            "🤖 بوت ذكي لحذف الإعلانات المزعجة عن الإجازات المرضية\n\n"
            "✨ المزايا:\n"
            "• كشف ذكي للإعلانات المموهة\n"
            "• حذف تلقائي للرسائل المزعجة\n"
            "• حذف الرسائل القديمة\n"
            "• إدارة متقدمة للقروب\n"
            "• تقارير شاملة وإحصائيات"
        )
        
        short_description = "بوت ذكي لحذف الإعلانات المزعجة 🤖"
        
        await application.bot.set_my_description(description)
        await application.bot.set_my_short_description(short_description)
        
        logger.info("✅ تم تعيين وصف البوت بنجاح")
        return True
    
    except Exception as e:
        logger.error(f"❌ خطأ في تعيين وصف البوت: {e}")
        return False


async def setup_bot_defaults(application: Application):
    """
    إعداد الإعدادات الافتراضية للبوت
    """
    
    try:
        # تسجيل الأوامر
        await setup_bot_commands(application)
        
        # تعيين الوصف
        await setup_bot_description(application)
        
        logger.info("✅ تم إعداد البوت بنجاح")
        return True
    
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد البوت: {e}")
        return False
