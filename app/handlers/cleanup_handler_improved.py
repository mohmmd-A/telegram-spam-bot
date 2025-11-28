"""
معالج التنظيف المحسّن - نسخة محسّنة
Improved Cleanup Handler - Enhanced Version
"""

from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from app.models.init_db import SessionLocal, DeletedMessage, ChatSettings
from app.services.database_service import DatabaseService
from app.services.detection import detection_engine
from app.handlers.message_deletion_handler import message_deletion_handler
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ImprovedCleanupHandlerV2:
    """معالج تنظيف محسّن مع حذف فعلي للرسائل المزعجة"""
    
    @staticmethod
    async def cleanup_old_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /cleanup_old - حذف الرسائل المزعجة من آخر N يوم
        الاستخدام: /cleanup_old 7  (آخر 7 أيام)
        الاستخدام: /cleanup_old 30 (آخر 30 يوم)
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
        
        # التحقق من صلاحيات البوت
        bot_perms = await message_deletion_handler.check_bot_permissions(context, chat_id)
        if not bot_perms["can_delete_messages"]:
            await update.message.reply_text(
                "❌ **خطأ في الصلاحيات:**\n\n"
                "البوت لا يملك صلاحية حذف الرسائل.\n\n"
                "**الحل:**\n"
                "1. تأكد أن البوت مسؤول في القروب\n"
                "2. تأكد من تفعيل صلاحية 'حذف الرسائل' للبوت\n"
                "3. أضف البوت مرة أخرى إذا لزم الأمر"
            )
            return
        
        # الحصول على عدد الأيام من الأمر
        days = 7  # القيمة الافتراضية (آخر 7 أيام بدلاً من 30)
        if context.args and context.args[0].isdigit():
            days = int(context.args[0])
        
        if days < 1:
            await update.message.reply_text("❌ يجب أن يكون عدد الأيام أكبر من 0")
            return
        
        # إرسال رسالة الانتظار
        status_msg = await update.message.reply_text(
            f"⏳ **جاري تنظيف الرسائل المزعجة...**\n\n"
            f"📅 الفترة: آخر {days} يوم\n"
            f"🔍 جاري البحث عن الرسائل المزعجة...\n"
            f"⚠️ هذا قد يستغرق بعض الوقت..."
        )
        
        db = SessionLocal()
        
        try:
            # حساب التاريخ الحد
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # الحصول على الرسائل المحذوفة من قاعدة البيانات
            deleted_messages = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id,
                DeletedMessage.deleted_at >= cutoff_date
            ).all()
            
            if not deleted_messages:
                await status_msg.edit_text(
                    f"ℹ️ **لا توجد رسائل مزعجة مسجلة للحذف**\n\n"
                    f"لم يتم العثور على رسائل مزعجة مسجلة في آخر {days} يوم.\n\n"
                    f"**ملاحظة:** البوت يحذف الرسائل المزعجة تلقائياً عند اكتشافها."
                )
                db.close()
                return
            
            total_messages = len(deleted_messages)
            message_ids = [msg.message_id for msg in deleted_messages]
            
            await status_msg.edit_text(
                f"⏳ **جاري حذف {total_messages} رسالة مزعجة...**\n\n"
                f"📅 الفترة: آخر {days} يوم\n"
                f"⚠️ هذا قد يستغرق بعض الوقت..."
            )
            
            # حذف الرسائل باستخدام معالج الحذف المحسّن
            stats = await message_deletion_handler.delete_messages_in_range(
                context, chat_id, message_ids, f"cleanup_{days}_days"
            )
            
            # حذف من قاعدة البيانات
            for msg in deleted_messages:
                try:
                    db.delete(msg)
                except Exception as e:
                    logger.warning(f"خطأ في حذف السجل: {e}")
            
            db.commit()
            
            # النتيجة النهائية
            response = (
                f"✅ **تم التنظيف بنجاح!**\n\n"
                f"📊 **الإحصائيات:**\n"
                f"• تم حذف: {stats['deleted']} رسالة\n"
                f"• فشل الحذف: {stats['failed']} رسالة\n"
                f"• غير موجودة: {stats['not_found']} رسالة\n"
                f"• إجمالي المعالج: {stats['total']} رسالة\n"
                f"• الفترة: آخر {days} يوم"
            )
            
            if stats['errors']:
                response += f"\n\n⚠️ **الأخطاء:**\n"
                for error in stats['errors'][:3]:
                    response += f"• {error}\n"
            
            await status_msg.edit_text(response)
            
            logger.info(f"✅ تم تنظيف {stats['deleted']} رسالة من القروب {chat_id}")
        
        except Exception as e:
            logger.error(f"❌ خطأ في التنظيف: {e}")
            await status_msg.edit_text(
                f"❌ **حدث خطأ أثناء التنظيف:**\n\n"
                f"`{str(e)}`\n\n"
                f"**نصائح:**\n"
                f"• تأكد من صلاحيات البوت\n"
                f"• جرّب عدد أيام أقل\n"
                f"• تأكد من اتصال الإنترنت"
            )
        
        finally:
            db.close()
    
    @staticmethod
    async def cleanup_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /cleanup_user <user_id> - حذف جميع رسائل مستخدم معين
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
        
        # التحقق من صلاحيات البوت
        bot_perms = await message_deletion_handler.check_bot_permissions(context, chat_id)
        if not bot_perms["can_delete_messages"]:
            await update.message.reply_text("❌ البوت لا يملك صلاحية حذف الرسائل")
            return
        
        # الحصول على معرف المستخدم المراد حذف رسائله
        if not context.args:
            await update.message.reply_text(
                "❌ الرجاء تحديد معرف المستخدم\n"
                "الاستخدام: /cleanup_user <user_id>"
            )
            return
        
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ معرف المستخدم غير صحيح")
            return
        
        status_msg = await update.message.reply_text(
            f"⏳ **جاري حذف رسائل المستخدم {target_user_id}...**"
        )
        
        db = SessionLocal()
        
        try:
            # الحصول على رسائل المستخدم المزعجة
            user_messages = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id,
                DeletedMessage.user_id == target_user_id
            ).all()
            
            if not user_messages:
                await status_msg.edit_text(
                    f"ℹ️ **لا توجد رسائل مزعجة لهذا المستخدم**\n\n"
                    f"معرف المستخدم: {target_user_id}"
                )
                db.close()
                return
            
            total_messages = len(user_messages)
            message_ids = [msg.message_id for msg in user_messages]
            
            # حذف الرسائل
            stats = await message_deletion_handler.delete_messages_in_range(
                context, chat_id, message_ids, f"cleanup_user_{target_user_id}"
            )
            
            # حذف من قاعدة البيانات
            for msg in user_messages:
                try:
                    db.delete(msg)
                except:
                    pass
            
            db.commit()
            
            response = (
                f"✅ **تم حذف رسائل المستخدم بنجاح!**\n\n"
                f"📊 **الإحصائيات:**\n"
                f"• تم حذف: {stats['deleted']} رسالة\n"
                f"• فشل الحذف: {stats['failed']} رسالة\n"
                f"• معرف المستخدم: {target_user_id}"
            )
            
            await status_msg.edit_text(response)
            logger.info(f"✅ تم حذف {stats['deleted']} رسالة للمستخدم {target_user_id}")
        
        except Exception as e:
            logger.error(f"❌ خطأ في حذف رسائل المستخدم: {e}")
            await status_msg.edit_text(f"❌ حدث خطأ: {str(e)}")
        
        finally:
            db.close()
    
    @staticmethod
    async def archive_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /archive - عرض ملخص الرسائل المحذوفة
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
            # إحصائيات الحذف
            total_deleted = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id
            ).count()
            
            # آخر 7 أيام
            week_ago = datetime.utcnow() - timedelta(days=7)
            deleted_week = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id,
                DeletedMessage.deleted_at >= week_ago
            ).count()
            
            # آخر 30 يوم
            month_ago = datetime.utcnow() - timedelta(days=30)
            deleted_month = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id,
                DeletedMessage.deleted_at >= month_ago
            ).count()
            
            response = (
                f"📊 **ملخص الرسائل المحذوفة**\n\n"
                f"• إجمالي المحذوفة: {total_deleted} رسالة\n"
                f"• آخر 7 أيام: {deleted_week} رسالة\n"
                f"• آخر 30 يوم: {deleted_month} رسالة\n\n"
                f"💡 **الأوامر المتاحة:**\n"
                f"• `/cleanup_old 7` - حذف الرسائل المزعجة من آخر 7 أيام\n"
                f"• `/cleanup_old 30` - حذف الرسائل المزعجة من آخر 30 يوم\n"
                f"• `/cleanup_user <id>` - حذف رسائل مستخدم معين"
            )
            
            await update.message.reply_text(response)
        
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الملخص: {e}")
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        finally:
            db.close()
