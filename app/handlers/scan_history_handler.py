"""
معالج مسح السجل التاريخي
Scan History Handler - Scan and delete old spam messages
"""

from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.error import TelegramError, BadRequest
from app.models.init_db import SessionLocal, DeletedMessage, ChatSettings
from app.services.database_service import DatabaseService
from app.services.detection import detection_engine
from app.handlers.message_deletion_handler import message_deletion_handler
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)


class ScanHistoryHandler:
    """معالج مسح السجل التاريخي للرسائل المزعجة"""
    
    @staticmethod
    async def scan_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /scan_history - مسح الرسائل القديمة والبحث عن الرسائل المزعجة
        
        ملاحظة مهمة:
        Telegram API لا يسمح بالوصول المباشر لسجل الرسائل القديمة.
        هذا الأمر يعمل بطريقة بديلة:
        1. يمسح الرسائل الجديدة التي يتلقاها البوت
        2. يحفظ الرسائل المزعجة المكتشفة
        3. يمكنك استخدام /cleanup_old لحذف الرسائل المسجلة
        
        الاستخدام الأفضل:
        - استخدم /cleanup_old 7 لحذف الرسائل المزعجة من آخر 7 أيام
        - استخدم /cleanup_old 30 لحذف الرسائل المزعجة من آخر 30 يوم
        """
        if not update.message or not update.effective_chat:
            return
        
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # التحقق من صلاحيات المستخدم
        user_perms = await message_deletion_handler.check_user_permissions(context, chat_id, user_id)
        if not user_perms["is_administrator"]:
            await update.message.reply_text(
                "❌ عذراً، يجب أن تكون مسؤول في القروب لاستخدام هذا الأمر."
            )
            return
        
        db = SessionLocal()
        
        try:
            # الحصول على إحصائيات الرسائل المسجلة
            week_ago = datetime.utcnow() - timedelta(days=7)
            month_ago = datetime.utcnow() - timedelta(days=30)
            
            total_deleted = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id
            ).count()
            
            deleted_week = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id,
                DeletedMessage.deleted_at >= week_ago
            ).count()
            
            deleted_month = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id,
                DeletedMessage.deleted_at >= month_ago
            ).count()
            
            response = (
                f"📊 **إحصائيات الرسائل المزعجة المكتشفة:**\n\n"
                f"• إجمالي المحذوفة: {total_deleted} رسالة\n"
                f"• آخر 7 أيام: {deleted_week} رسالة\n"
                f"• آخر 30 يوم: {deleted_month} رسالة\n\n"
                f"💡 **الأوامر المتاحة:**\n"
                f"• `/cleanup_old 7` - حذف الرسائل المزعجة من آخر 7 أيام\n"
                f"• `/cleanup_old 30` - حذف الرسائل المزعجة من آخر 30 يوم\n"
                f"• `/cleanup_user <id>` - حذف رسائل مستخدم معين\n\n"
                f"ℹ️ **ملاحظة:**\n"
                f"البوت يكتشف ويحذف الرسائل المزعجة تلقائياً عند وصولها.\n"
                f"استخدم الأوامر أعلاه لحذف الرسائل المسجلة."
            )
            
            await update.message.reply_text(response)
        
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الإحصائيات: {e}")
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        finally:
            db.close()
    
    @staticmethod
    async def manual_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /manual_scan - مسح يدوي للرسائل المزعجة المرسلة في الدردشة الحالية
        
        هذا الأمر يفحص الرسائل التي يتم إرسالها بعد تشغيل الأمر
        ويحفظ الرسائل المزعجة للحذف لاحقاً
        """
        if not update.message or not update.effective_chat:
            return
        
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # التحقق من صلاحيات المستخدم
        user_perms = await message_deletion_handler.check_user_permissions(context, chat_id, user_id)
        if not user_perms["is_administrator"]:
            await update.message.reply_text(
                "❌ عذراً، يجب أن تكون مسؤول في القروب لاستخدام هذا الأمر."
            )
            return
        
        # حفظ حالة المسح اليدوي
        if not hasattr(context, 'user_data'):
            context.user_data = {}
        
        context.user_data['manual_scan_enabled'] = True
        context.user_data['manual_scan_count'] = 0
        context.user_data['manual_scan_spam'] = 0
        
        response = (
            f"🔍 **تم تفعيل المسح اليدوي**\n\n"
            f"سيتم فحص جميع الرسائل المرسلة من الآن\n"
            f"والبحث عن الرسائل المزعجة.\n\n"
            f"استخدم `/stop_scan` لإيقاف المسح"
        )
        
        await update.message.reply_text(response)
        logger.info(f"🔍 تم تفعيل المسح اليدوي للقروب {chat_id}")
    
    @staticmethod
    async def stop_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /stop_scan - إيقاف المسح اليدوي
        """
        if not update.message or not update.effective_chat:
            return
        
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # التحقق من صلاحيات المستخدم
        user_perms = await message_deletion_handler.check_user_permissions(context, chat_id, user_id)
        if not user_perms["is_administrator"]:
            await update.message.reply_text(
                "❌ عذراً، يجب أن تكون مسؤول في القروب لاستخدام هذا الأمر."
            )
            return
        
        if not hasattr(context, 'user_data') or not context.user_data.get('manual_scan_enabled'):
            await update.message.reply_text("❌ لا يوجد مسح نشط حالياً")
            return
        
        # إيقاف المسح
        count = context.user_data.get('manual_scan_count', 0)
        spam = context.user_data.get('manual_scan_spam', 0)
        
        context.user_data['manual_scan_enabled'] = False
        
        response = (
            f"✅ **تم إيقاف المسح**\n\n"
            f"📊 **النتائج:**\n"
            f"• تم فحص: {count} رسالة\n"
            f"• رسائل مزعجة: {spam}\n\n"
            f"استخدم `/cleanup_old` لحذف الرسائل المزعجة المكتشفة"
        )
        
        await update.message.reply_text(response)
        logger.info(f"✅ تم إيقاف المسح للقروب {chat_id} - فحص={count}, مزعج={spam}")
