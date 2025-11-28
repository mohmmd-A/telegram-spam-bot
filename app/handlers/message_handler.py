"""
معالج الرسائل والأوامر الأساسية - النسخة المصححة
Message and Basic Commands Handler - Fixed Version
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from sqlalchemy.orm import Session
import logging

from app.services.detection import detection_engine
from app.services.database_service import DatabaseService
from app.services.username_filter import username_filter
from app.services.obfuscation_detector import obfuscation_detector
from app.models.init_db import SessionLocal
from app.utils.commands import CommandRegistry

logger = logging.getLogger(__name__)


class MessageHandler:
    """معالج رسائل البوت"""
    
    @staticmethod
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل الواردة"""
        if not update.message or not update.message.text:
            return
        
        message = update.message
        chat_id = message.chat_id
        user_id = message.from_user.id
        user_name = message.from_user.username or message.from_user.first_name or "Unknown"
        message_text = message.text
        
        db = SessionLocal()
        try:
            # الحصول على إعدادات القروب
            settings = DatabaseService.get_or_create_chat_settings(db, chat_id)
            
            # التحقق من أن البوت مفعل
            if not settings.is_enabled:
                return
            
            # التحقق من أن المستخدم في القائمة البيضاء
            if DatabaseService.is_user_whitelisted(db, chat_id, user_id):
                return
            
            # التحقق من أن المستخدم في القائمة السوداء
            if DatabaseService.is_user_blacklisted(db, chat_id, user_id):
                await MessageHandler._delete_message(context, chat_id, message.message_id)
                DatabaseService.log_activity(
                    db, chat_id, "auto_delete_blacklist",
                    user_id, user_name,
                    f"تم حذف رسالة من مستخدم في القائمة السوداء"
                )
                return
            
            # فحص اسم المستخدم للكلمات المزعجة
            if message.from_user.username:
                is_suspicious, keywords, confidence = username_filter.check_username_for_spam(
                    message.from_user.username
                )
                
                if is_suspicious and confidence > 0.5:
                    # حفظ اسم المستخدم المشبوه
                    risk_score, risk_level = username_filter.get_username_risk_score(
                        message.from_user.username
                    )
                    
                    username_filter.save_suspicious_username(
                        db, chat_id, user_id, message.from_user.username,
                        risk_score, f"كلمات مزعجة: {', '.join(keywords)}"
                    )
                    
                    # تحديد المستخدم - حذف الرسالة
                    await MessageHandler._delete_message(context, chat_id, message.message_id)
                    DatabaseService.log_activity(
                        db, chat_id, "auto_delete_suspicious_username",
                        user_id, message.from_user.username,
                        f"تم حذف الرسالة - اسم المستخدم مشبوه: {risk_level}"
                    )
                    
                    logger.info(f"تم تحديد مستخدم مشبوه: {message.from_user.username}")
                    return
            
            # كشف الإعلانات
            is_spam, confidence, keywords = detection_engine.detect_spam(
                message_text, user_id, chat_id, settings.detection_sensitivity
            )
            
            if is_spam:
                # حذف الرسالة
                await MessageHandler._delete_message(context, chat_id, message.message_id)
                
                # تسجيل النشاط
                try:
                    DatabaseService.log_deleted_message(
                        db, chat_id, message.message_id, user_id, user_name,
                        message_text, keywords, confidence
                    )
                    logger.info(f"✅ تم تسجيل رسالة مزعجة: chat_id={chat_id}, msg_id={message.message_id}")
                except Exception as db_error:
                    logger.error(f"❌ خطأ في تسجيل الرسالة: {db_error}")
                    import traceback
                    traceback.print_exc()
                
                # إرسال إشعار للمسؤولين
                await MessageHandler._notify_admins(
                    context, chat_id, user_name, message_text, confidence, keywords
                )
                
                logger.info(f"تم حذف رسالة إعلانية من {user_name} في القروب {chat_id}")
        
        except Exception as e:
            logger.error(f"خطأ في معالجة الرسالة: {e}")
        
        finally:
            db.close()
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        if not update.message:
            return
        
        welcome_text = """
🤖 **مرحباً بك في بوت حذف الإعلانات المزعجة!**

✨ **المزايا:**
• 🔍 كشف ذكي للإعلانات المزعجة
• ⚡ حذف فوري للرسائل المكتشفة
• 🧹 تنظيف الرسائل القديمة
• 📊 إحصائيات مفصلة
• ⚙️ إدارة متقدمة

📋 **للمزيد من المعلومات:**
اكتب `/help` لرؤية جميع الأوامر

💡 **نصيحة:**
اكتب `/` لرؤية قائمة الأوامر المتاحة
"""
        
        await update.message.reply_text(welcome_text, parse_mode="Markdown")
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        if not update.message:
            return
        
        help_text = CommandRegistry.get_help_text()
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    @staticmethod
    async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /stats"""
        if not update.message or not update.effective_chat:
            return
        
        db = SessionLocal()
        try:
            chat_id = update.effective_chat.id
            
            # الحصول على إحصائيات القروب
            stats = DatabaseService.get_chat_statistics(db, chat_id)
            
            stats_text = f"""
📊 **إحصائيات القروب:**

📈 **الرسائل:**
• المكتشفة: {stats.get('detected_count', 0)}
• المحذوفة: {stats.get('deleted_count', 0)}
• نسبة الحذف: {stats.get('deletion_rate', 0):.1f}%

👥 **المستخدمون:**
• إجمالي المرسلين: {stats.get('user_count', 0)}
• في القائمة البيضاء: {stats.get('whitelist_count', 0)}
• في القائمة السوداء: {stats.get('blacklist_count', 0)}

🔑 **الكلمات المفتاحية:**
• الأكثر تكراراً: {stats.get('top_keyword', 'لا توجد')}
• عدد الكلمات: {stats.get('keyword_count', 0)}

⏰ **آخر تحديث:** الآن
"""
            
            await update.message.reply_text(stats_text, parse_mode="Markdown")
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات: {e}")
            await update.message.reply_text(
                f"❌ حدث خطأ في الحصول على الإحصائيات: {str(e)}"
            )
        
        finally:
            db.close()
    
    @staticmethod
    async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /settings"""
        if not update.message or not update.effective_chat:
            return
        
        db = SessionLocal()
        try:
            chat_id = update.effective_chat.id
            
            # الحصول على إعدادات القروب
            settings = DatabaseService.get_or_create_chat_settings(db, chat_id)
            
            settings_text = f"""
⚙️ **إعدادات البوت:**

🔧 **الحالة:**
• البوت: {'✅ مفعل' if settings.is_enabled else '❌ معطل'}
• حساسية الكشف: {settings.detection_sensitivity * 100:.0f}%

📋 **الإعدادات:**
• حذف تلقائي: {'✅ مفعل' if settings.auto_delete else '❌ معطل'}
• إشعارات: {'✅ مفعلة' if settings.notify_admins else '❌ معطلة'}
• تسجيل النشاط: ✅ مفعل

💡 **لتعديل الإعدادات:**
استخدم الأوامر التالية:
• `/enable` - تفعيل البوت
• `/disable` - تعطيل البوت
• `/sensitivity <رقم>` - تعديل الحساسية
"""
            
            await update.message.reply_text(settings_text, parse_mode="Markdown")
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإعدادات: {e}")
            await update.message.reply_text(
                f"❌ حدث خطأ: {str(e)}"
            )
        
        finally:
            db.close()
    
    @staticmethod
    async def _delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
        """حذف رسالة من القروب"""
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except TelegramError as e:
            logger.warning(f"فشل حذف الرسالة {message_id}: {e}")
    
    @staticmethod
    async def _notify_admins(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        user_name: str,
        message_text: str,
        confidence: float,
        keywords: list
    ):
        """إرسال إشعار للمسؤولين"""
        try:
            notification = f"""
🚨 **تنبيه: رسالة إعلانية مكتشفة**

👤 **المستخدم:** {user_name}
📝 **النص:** {message_text[:100]}...
🎯 **الثقة:** {confidence * 100:.1f}%
🔑 **الكلمات:** {', '.join(keywords[:3])}

⏰ **الوقت:** الآن
"""
            
            # إرسال الإشعار إلى القروب (اختياري)
            # await context.bot.send_message(chat_id=chat_id, text=notification)
        
        except Exception as e:
            logger.warning(f"فشل إرسال الإشعار: {e}")


class CommandHandler:
    """معالج الأوامر الأساسية"""
    pass
