from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from sqlalchemy.orm import Session
import logging

from app.services.detection import detection_engine
from app.services.database_service import DatabaseService
from app.models.database import SessionLocal

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
            settings = DatabaseService.get_chat_settings(db, chat_id)
            
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
                    f"تم حذف رسالة من مستخدم في القائمة السوداء",
                    user_id, user_name
                )
                return
            
            # الكشف عن الإعلانات
            is_spam, confidence_score, detected_keywords = detection_engine.detect_spam(
                message_text, user_id, chat_id, settings.detection_sensitivity
            )
            
            if is_spam:
                # تسجيل الرسالة المحذوفة
                DatabaseService.log_deleted_message(
                    db, chat_id, message.message_id, user_id, user_name,
                    message_text, detected_keywords, confidence_score
                )
                
                # تحديث إحصائيات المستخدم
                user_stats = DatabaseService.update_user_statistics(
                    db, chat_id, user_id, user_name, increment_spam=True
                )
                
                # حذف الرسالة إذا كان الحذف التلقائي مفعل
                if settings.auto_delete:
                    await MessageHandler._delete_message(context, chat_id, message.message_id)
                    
                    # تسجيل النشاط
                    DatabaseService.log_activity(
                        db, chat_id, "spam_deleted",
                        f"تم حذف إعلان: {', '.join(detected_keywords[:3])}",
                        user_id, user_name
                    )
                
                # إرسال إشعار للمسؤولين
                if settings.notify_admins:
                    await MessageHandler._notify_admins(
                        context, chat_id, user_name, message_text,
                        detected_keywords, confidence_score
                    )
                
                # تحذير المستخدم إذا تجاوز عدد التحذيرات
                if user_stats.spam_count >= settings.max_warnings:
                    await MessageHandler._warn_user(
                        context, chat_id, user_id, user_name, user_stats.spam_count
                    )
        
        except Exception as e:
            logger.error(f"خطأ في معالجة الرسالة: {e}")
        
        finally:
            db.close()
    
    @staticmethod
    async def _delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
        """حذف رسالة"""
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.info(f"تم حذف الرسالة {message_id} من القروب {chat_id}")
        except TelegramError as e:
            logger.error(f"خطأ في حذف الرسالة: {e}")
    
    @staticmethod
    async def _notify_admins(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        user_name: str,
        message_text: str,
        detected_keywords: list,
        confidence_score: float
    ):
        """إرسال إشعار للمسؤولين"""
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            admin_ids = [admin.user.id for admin in admins]
            
            notification = (
                f"🚨 **تنبيه إعلان مزعج**\n\n"
                f"👤 المستخدم: @{user_name}\n"
                f"📝 الرسالة: `{message_text[:100]}...`\n"
                f"🔑 الكلمات المفتاحية: {', '.join(detected_keywords[:3])}\n"
                f"📊 درجة الثقة: {confidence_score:.1%}"
            )
            
            for admin_id in admin_ids:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=notification,
                        parse_mode="Markdown"
                    )
                except TelegramError:
                    pass
        
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشعار: {e}")
    
    @staticmethod
    async def _warn_user(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        user_id: int,
        user_name: str,
        spam_count: int
    ):
        """تحذير المستخدم"""
        try:
            warning_message = (
                f"⚠️ تحذير: تم اكتشاف {spam_count} رسائل إعلانية من حسابك.\n"
                f"يرجى الامتناع عن نشر الإعلانات في هذا القروب."
            )
            
            await context.bot.send_message(
                chat_id=user_id,
                text=warning_message
            )
        
        except TelegramError as e:
            logger.error(f"خطأ في إرسال التحذير: {e}")


class CommandHandler:
    """معالج الأوامر"""
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /start"""
        message = (
            "👋 مرحباً بك في بوت حذف الإعلانات المزعجة!\n\n"
            "🤖 أنا بوت ذكي يساعد في تنظيف القروب من الإعلانات المزعجة.\n\n"
            "📋 الأوامر المتاحة:\n"
            "/help - عرض المساعدة\n"
            "/stats - الإحصائيات\n"
            "/settings - الإعدادات\n"
            "/whitelist - القائمة البيضاء\n"
            "/blacklist - القائمة السوداء\n"
        )
        await update.message.reply_text(message)
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /help"""
        help_text = (
            "📚 **دليل الاستخدام**\n\n"
            "🔍 **كيفية عمل البوت:**\n"
            "يقوم البوت بفحص جميع الرسائل في القروب وكشف الإعلانات المزعجة تلقائياً.\n\n"
            "🛡️ **معايير الكشف:**\n"
            "• الكلمات المفتاحية الطبية\n"
            "• أرقام الهواتف والروابط المريبة\n"
            "• الرسائل المكررة\n"
            "• مؤشرات الإعلانات\n\n"
            "⚙️ **الإعدادات:**\n"
            "يمكن للمسؤولين تخصيص حساسية الكشف والإعدادات الأخرى.\n"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    @staticmethod
    async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /stats"""
        chat_id = update.message.chat_id
        db = SessionLocal()
        
        try:
            stats = DatabaseService.get_chat_statistics(db, chat_id, days=7)
            
            stats_text = (
                f"📊 **إحصائيات القروب (آخر 7 أيام)**\n\n"
                f"🗑️ الرسائل المحذوفة: {stats['total_deleted_messages']}\n\n"
            )
            
            if stats['top_spammers']:
                stats_text += "👤 **أكثر المستخدمين إرسالاً للإعلانات:**\n"
                for i, spammer in enumerate(stats['top_spammers'], 1):
                    stats_text += f"{i}. {spammer['user_name']}: {spammer['spam_count']} رسائل\n"
            
            await update.message.reply_text(stats_text, parse_mode="Markdown")
        
        finally:
            db.close()
    
    @staticmethod
    async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /settings"""
        chat_id = update.message.chat_id
        db = SessionLocal()
        
        try:
            settings = DatabaseService.get_chat_settings(db, chat_id)
            
            settings_text = (
                f"⚙️ **إعدادات القروب**\n\n"
                f"🔴 الحالة: {'مفعل ✅' if settings.is_enabled else 'معطل ❌'}\n"
                f"📊 حساسية الكشف: {settings.detection_sensitivity:.1%}\n"
                f"🗑️ الحذف التلقائي: {'مفعل ✅' if settings.auto_delete else 'معطل ❌'}\n"
                f"🔔 إشعارات المسؤولين: {'مفعل ✅' if settings.notify_admins else 'معطل ❌'}\n"
                f"⚠️ الحد الأقصى للتحذيرات: {settings.max_warnings}\n"
            )
            
            await update.message.reply_text(settings_text, parse_mode="Markdown")
        
        finally:
            db.close()
