"""
معالج حذف الرسائل المتقدم
Advanced Message Deletion Handler
"""

from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.error import TelegramError, BadRequest
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MessageDeletionHandler:
    """معالج متقدم لحذف الرسائل مع التحقق من الصلاحيات"""
    
    @staticmethod
    async def delete_message(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        message_id: int,
        reason: str = "spam"
    ) -> bool:
        """
        حذف رسالة مع معالجة الأخطاء
        
        العودة:
            True إذا تم الحذف بنجاح
            False إذا فشل الحذف
        """
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.info(f"✅ تم حذف الرسالة {message_id} من القروب {chat_id} - السبب: {reason}")
            return True
        
        except BadRequest as e:
            if "message to delete not found" in str(e):
                logger.warning(f"⚠️ الرسالة {message_id} غير موجودة أو تم حذفها مسبقاً")
            elif "message can't be deleted" in str(e):
                logger.warning(f"⚠️ لا يمكن حذف الرسالة {message_id} - قد تكون قديمة جداً")
            else:
                logger.warning(f"⚠️ خطأ في حذف الرسالة {message_id}: {e}")
            return False
        
        except TelegramError as e:
            logger.error(f"❌ خطأ في حذف الرسالة {message_id}: {e}")
            return False
        
        except Exception as e:
            logger.error(f"❌ خطأ غير متوقع في حذف الرسالة {message_id}: {e}")
            return False
    
    @staticmethod
    async def check_bot_permissions(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int
    ) -> dict:
        """
        التحقق من صلاحيات البوت في القروب
        
        العودة:
            قاموس بالصلاحيات
        """
        try:
            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            
            permissions = {
                "can_delete_messages": bot_member.can_delete_messages,
                "can_restrict_members": bot_member.can_restrict_members,
                "can_pin_messages": bot_member.can_pin_messages,
                "is_administrator": bot_member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR],
                "status": bot_member.status
            }
            
            logger.info(f"صلاحيات البوت في القروب {chat_id}: {permissions}")
            return permissions
        
        except Exception as e:
            logger.error(f"خطأ في التحقق من صلاحيات البوت: {e}")
            return {
                "can_delete_messages": False,
                "can_restrict_members": False,
                "can_pin_messages": False,
                "is_administrator": False,
                "status": "unknown"
            }
    
    @staticmethod
    async def check_user_permissions(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        user_id: int
    ) -> dict:
        """
        التحقق من صلاحيات المستخدم في القروب
        """
        try:
            user_member = await context.bot.get_chat_member(chat_id, user_id)
            
            permissions = {
                "is_administrator": user_member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR],
                "is_creator": user_member.status == ChatMember.CREATOR,
                "can_delete_messages": user_member.can_delete_messages,
                "status": user_member.status
            }
            
            return permissions
        
        except Exception as e:
            logger.error(f"خطأ في التحقق من صلاحيات المستخدم: {e}")
            return {
                "is_administrator": False,
                "is_creator": False,
                "can_delete_messages": False,
                "status": "unknown"
            }
    
    @staticmethod
    async def delete_messages_in_range(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        message_ids: list,
        reason: str = "cleanup"
    ) -> dict:
        """
        حذف مجموعة من الرسائل
        
        العودة:
            قاموس بإحصائيات الحذف
        """
        stats = {
            "total": len(message_ids),
            "deleted": 0,
            "failed": 0,
            "not_found": 0,
            "errors": []
        }
        
        for message_id in message_ids:
            try:
                success = await MessageDeletionHandler.delete_message(
                    context, chat_id, message_id, reason
                )
                
                if success:
                    stats["deleted"] += 1
                else:
                    stats["failed"] += 1
            
            except BadRequest as e:
                if "message to delete not found" in str(e):
                    stats["not_found"] += 1
                else:
                    stats["failed"] += 1
                    stats["errors"].append(str(e))
            
            except Exception as e:
                stats["failed"] += 1
                stats["errors"].append(str(e))
        
        logger.info(f"إحصائيات الحذف: {stats}")
        return stats
    
    @staticmethod
    async def delete_messages_by_date(
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        days_old: int,
        message_data: list
    ) -> dict:
        """
        حذف الرسائل الأقدم من عدد معين من الأيام
        
        message_data: قائمة بـ (message_id, timestamp)
        """
        now = datetime.utcnow()
        cutoff_date = now - timedelta(days=days_old)
        
        messages_to_delete = []
        
        for message_id, timestamp in message_data:
            if timestamp < cutoff_date:
                messages_to_delete.append(message_id)
        
        logger.info(f"سيتم حذف {len(messages_to_delete)} رسالة أقدم من {days_old} أيام")
        
        return await MessageDeletionHandler.delete_messages_in_range(
            context, chat_id, messages_to_delete, f"cleanup_{days_old}_days"
        )
    
    @staticmethod
    async def notify_deletion_failure(
        context: ContextTypes.DEFAULT_TYPE,
        update: Update,
        reason: str
    ):
        """إرسال إشعار بفشل الحذف"""
        try:
            if update.message:
                await update.message.reply_text(
                    f"⚠️ **تنبيه:**\n\n"
                    f"لم يتمكن البوت من حذف الرسائل.\n\n"
                    f"**السبب:** {reason}\n\n"
                    f"**الحل:**\n"
                    f"1. تأكد أن البوت لديه صلاحية 'حذف الرسائل'\n"
                    f"2. تأكد أن البوت مسؤول في القروب\n"
                    f"3. قد تكون الرسائل قديمة جداً ولا يمكن حذفها\n"
                    f"4. جرّب `/cleanup_old 7` لحذف الرسائل من آخر 7 أيام",
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشعار: {e}")


# إنشاء نسخة واحدة من المعالج
message_deletion_handler = MessageDeletionHandler()
