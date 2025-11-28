"""
معالج التنظيف المحسّن
Improved Cleanup Handler
"""

from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from app.models.init_db import SessionLocal, DeletedMessage, ChatSettings
from app.services.database_service import DatabaseService
from app.handlers.message_deletion_handler import message_deletion_handler
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ImprovedCleanupHandler:
    """معالج تنظيف محسّن مع دعم أفضل للأخطاء"""
    
    @staticmethod
    async def cleanup_old_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /cleanup_old - حذف الرسائل الإعلانية القديمة
        الاستخدام: /cleanup_old 14
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
        days = 30  # القيمة الافتراضية
        if context.args and context.args[0].isdigit():
            days = int(context.args[0])
        
        if days < 1:
            await update.message.reply_text("❌ يجب أن يكون عدد الأيام أكبر من 0")
            return
        
        # إرسال رسالة الانتظار
        status_msg = await update.message.reply_text(
            f"⏳ **جاري تنظيف الرسائل الإعلانية القديمة...**\n\n"
            f"📅 الفترة: أكثر من {days} يوم\n"
            f"⚠️ هذا قد يستغرق بعض الوقت..."
        )
        
        db = SessionLocal()
        
        try:
            # حساب التاريخ الحد
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # الحصول على الرسائل القديمة من قاعدة البيانات
            old_messages = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id,
                DeletedMessage.deleted_at < cutoff_date
            ).all()
            
            if not old_messages:
                await status_msg.edit_text(
                    f"ℹ️ **لا توجد رسائل قديمة للحذف**\n\n"
                    f"لم يتم العثور على رسائل أقدم من {days} يوم في السجلات."
                )
                db.close()
                return
            
            total_messages = len(old_messages)
            message_ids = [msg.message_id for msg in old_messages]
            
            # حذف الرسائل باستخدام معالج الحذف المحسّن
            stats = await message_deletion_handler.delete_messages_in_range(
                context, chat_id, message_ids, f"cleanup_{days}_days"
            )
            
            # حذف من قاعدة البيانات
            for msg in old_messages:
                try:
                    db.delete(msg)
                except:
                    pass
            
            db.commit()
            
            # النتيجة النهائية
            response = (
                f"✅ **تم التنظيف بنجاح!**\n\n"
                f"📊 **الإحصائيات:**\n"
                f"• تم حذف: {stats['deleted']} رسالة\n"
                f"• فشل الحذف: {stats['failed']} رسالة\n"
                f"• غير موجودة: {stats['not_found']} رسالة\n"
                f"• إجمالي المعالج: {stats['total']} رسالة\n"
                f"• الفترة: أكثر من {days} يوم"
            )
            
            if stats['errors']:
                response += f"\n\n⚠️ **الأخطاء:**\n"
                for error in stats['errors'][:3]:
                    response += f"• {error}\n"
            
            await status_msg.edit_text(response)
            
            logger.info(f"تم تنظيف {stats['deleted']} رسالة من القروب {chat_id}")
        
        except Exception as e:
            logger.error(f"خطأ في التنظيف: {e}")
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
            await update.message.reply_text("❌ يجب أن تكون مسؤول في القروب")
            return
        
        # الحصول على معرف المستخدم المراد حذف رسائله
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text(
                "❌ **الاستخدام:** `/cleanup_user <user_id>`\n\n"
                "**مثال:** `/cleanup_user 123456789`",
                parse_mode="Markdown"
            )
            return
        
        target_user_id = int(context.args[0])
        
        # إرسال رسالة الانتظار
        status_msg = await update.message.reply_text(
            f"⏳ جاري حذف رسائل المستخدم {target_user_id}..."
        )
        
        db = SessionLocal()
        
        try:
            # الحصول على رسائل المستخدم
            user_messages = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id,
                DeletedMessage.user_id == target_user_id
            ).all()
            
            if not user_messages:
                await status_msg.edit_text(
                    f"ℹ️ لم يتم العثور على رسائل للمستخدم {target_user_id}"
                )
                db.close()
                return
            
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
            
            # النتيجة
            response = (
                f"✅ **تم الحذف بنجاح!**\n\n"
                f"📊 **الإحصائيات:**\n"
                f"• تم حذف: {stats['deleted']} رسالة\n"
                f"• فشل: {stats['failed']} رسالة\n"
                f"• إجمالي: {stats['total']} رسالة"
            )
            
            await status_msg.edit_text(response)
        
        except Exception as e:
            logger.error(f"خطأ في حذف رسائل المستخدم: {e}")
            await status_msg.edit_text(f"❌ حدث خطأ: {str(e)}")
        
        finally:
            db.close()
    
    @staticmethod
    async def archive_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /archive_summary - عرض ملخص الرسائل المحذوفة
        """
        if not update.message or not update.effective_chat:
            return
        
        chat_id = update.effective_chat.id
        
        # الحصول على عدد الأيام من الأمر
        days = 7  # القيمة الافتراضية
        if context.args and context.args[0].isdigit():
            days = int(context.args[0])
        
        db = SessionLocal()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # الحصول على الإحصائيات
            deleted_messages = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == chat_id,
                DeletedMessage.deleted_at >= cutoff_date
            ).all()
            
            if not deleted_messages:
                await update.message.reply_text(
                    f"ℹ️ لا توجد رسائل محذوفة في آخر {days} يوم"
                )
                db.close()
                return
            
            # حساب الإحصائيات
            total_deleted = len(deleted_messages)
            unique_users = len(set(msg.user_id for msg in deleted_messages))
            
            # الكلمات الأكثر شيوعاً
            all_keywords = []
            for msg in deleted_messages:
                if msg.keywords:
                    all_keywords.extend(msg.keywords.split(","))
            
            keyword_counts = {}
            for keyword in all_keywords:
                keyword = keyword.strip()
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # بناء الرد
            summary = (
                f"📊 **ملخص الرسائل المحذوفة (آخر {days} يوم)**\n\n"
                f"📈 **الإحصائيات:**\n"
                f"• إجمالي المحذوفة: {total_deleted}\n"
                f"• عدد المستخدمين: {unique_users}\n\n"
            )
            
            if top_keywords:
                summary += f"🔑 **أكثر الكلمات المزعجة:**\n"
                for keyword, count in top_keywords:
                    summary += f"• {keyword}: {count}\n"
            
            await update.message.reply_text(summary)
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على الملخص: {e}")
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        finally:
            db.close()


# إنشاء نسخة واحدة من المعالج
improved_cleanup_handler = ImprovedCleanupHandler()
