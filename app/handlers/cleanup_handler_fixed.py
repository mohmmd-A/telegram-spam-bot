"""
معالج أوامر التنظيف والحذف - النسخة المصححة
Cleanup and Deletion Commands Handler - Fixed Version
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from app.models.database import SessionLocal, DeletedMessage
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CleanupCommandHandler:
    """معالج أوامر التنظيف والحذف"""
    
    @staticmethod
    async def cleanup_old_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /cleanup_old - حذف الرسائل الإعلانية القديمة
        الاستخدام: /cleanup_old 14
        """
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id, update.effective_user.id
            )
            
            if not member.can_delete_messages:
                await update.message.reply_text(
                    "❌ عذراً، ليس لديك صلاحية حذف الرسائل في هذا القروب."
                )
                return
        except Exception as e:
            logger.error(f"خطأ في التحقق من الصلاحيات: {e}")
            await update.message.reply_text(
                "❌ خطأ في التحقق من الصلاحيات. تأكد من أنك مسؤول."
            )
            return
        
        # الحصول على عدد الأيام من الأمر
        days = 30  # القيمة الافتراضية
        if context.args and context.args[0].isdigit():
            days = int(context.args[0])
        
        # إرسال رسالة الانتظار
        status_msg = await update.message.reply_text(
            f"⏳ جاري تنظيف الرسائل الإعلانية القديمة (أكثر من {days} يوم)...\n\n"
            f"⚠️ هذا قد يستغرق بعض الوقت حسب عدد الرسائل..."
        )
        
        db = SessionLocal()
        deleted_count = 0
        failed_count = 0
        
        try:
            # حساب التاريخ الحد
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # الحصول على الرسائل القديمة من قاعدة البيانات
            old_messages = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == update.effective_chat.id,
                DeletedMessage.timestamp < cutoff_date
            ).all()
            
            if not old_messages:
                await status_msg.edit_text(
                    f"ℹ️ لا توجد رسائل قديمة للحذف (أكثر من {days} يوم)"
                )
                db.close()
                return
            
            total_messages = len(old_messages)
            
            # حذف الرسائل
            for msg in old_messages:
                try:
                    # محاولة حذف الرسالة من تلقرام
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=msg.message_id
                    )
                    deleted_count += 1
                    
                    # حذف من قاعدة البيانات
                    db.delete(msg)
                    db.commit()
                
                except Exception as e:
                    failed_count += 1
                    logger.warning(f"فشل حذف الرسالة {msg.message_id}: {e}")
                    continue
            
            # النتيجة النهائية
            response = (
                f"✅ تم التنظيف بنجاح!\n\n"
                f"📊 الإحصائيات:\n"
                f"• تم حذف: {deleted_count} رسالة\n"
                f"• فشل: {failed_count} رسالة\n"
                f"• إجمالي المعالج: {total_messages} رسالة\n"
                f"• الفترة: أكثر من {days} يوم"
            )
            
            await status_msg.edit_text(response)
        
        except Exception as e:
            logger.error(f"خطأ في التنظيف: {e}")
            await status_msg.edit_text(
                f"❌ حدث خطأ أثناء التنظيف:\n{str(e)}"
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
        
        # التحقق من الصلاحيات
        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id, update.effective_user.id
            )
            
            if not member.can_delete_messages:
                await update.message.reply_text(
                    "❌ عذراً، ليس لديك صلاحية حذف الرسائل."
                )
                return
        except Exception as e:
            logger.error(f"خطأ في التحقق من الصلاحيات: {e}")
            return
        
        # الحصول على معرف المستخدم
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text(
                "❌ الاستخدام: /cleanup_user <user_id>\n"
                "مثال: /cleanup_user 123456789"
            )
            return
        
        user_id = int(context.args[0])
        
        status_msg = await update.message.reply_text(
            f"⏳ جاري حذف رسائل المستخدم {user_id}..."
        )
        
        db = SessionLocal()
        deleted_count = 0
        
        try:
            # الحصول على رسائل المستخدم
            user_messages = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == update.effective_chat.id,
                DeletedMessage.user_id == user_id
            ).all()
            
            if not user_messages:
                await status_msg.edit_text(
                    f"ℹ️ لا توجد رسائل لهذا المستخدم"
                )
                db.close()
                return
            
            # حذف الرسائل
            for msg in user_messages:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=msg.message_id
                    )
                    deleted_count += 1
                    db.delete(msg)
                    db.commit()
                except Exception as e:
                    logger.warning(f"فشل حذف الرسالة: {e}")
                    continue
            
            response = (
                f"✅ تم الحذف بنجاح!\n\n"
                f"📊 الإحصائيات:\n"
                f"• تم حذف: {deleted_count} رسالة\n"
                f"• المستخدم: {user_id}"
            )
            
            await status_msg.edit_text(response)
        
        except Exception as e:
            logger.error(f"خطأ في حذف رسائل المستخدم: {e}")
            await status_msg.edit_text(
                f"❌ حدث خطأ: {str(e)}"
            )
        
        finally:
            db.close()
    
    @staticmethod
    async def archive_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /archive_summary - عرض ملخص الرسائل المحذوفة
        """
        if not update.message or not update.effective_chat:
            return
        
        # الحصول على عدد الأيام من الأمر
        days = 7
        if context.args and context.args[0].isdigit():
            days = int(context.args[0])
        
        db = SessionLocal()
        
        try:
            # حساب التاريخ الحد
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # الحصول على الرسائل من قاعدة البيانات
            messages = db.query(DeletedMessage).filter(
                DeletedMessage.chat_id == update.effective_chat.id,
                DeletedMessage.timestamp >= cutoff_date
            ).all()
            
            if not messages:
                await update.message.reply_text(
                    f"ℹ️ لا توجد رسائل محذوفة في آخر {days} يوم"
                )
                db.close()
                return
            
            # حساب الإحصائيات
            by_user = {}
            by_keyword = {}
            
            for msg in messages:
                # إحصائيات المستخدمين
                user_id = msg.user_id
                by_user[user_id] = by_user.get(user_id, 0) + 1
                
                # إحصائيات الكلمات المفتاحية
                if msg.detected_keywords:
                    for keyword in msg.detected_keywords.split(','):
                        keyword = keyword.strip()
                        if keyword:
                            by_keyword[keyword] = by_keyword.get(keyword, 0) + 1
            
            # تنسيق الرسالة
            response = f"📊 ملخص الرسائل المحذوفة (آخر {days} يوم):\n\n"
            response += f"📈 إجمالي الرسائل: {len(messages)}\n\n"
            
            if by_user:
                response += "👥 أكثر المستخدمين إرسالاً:\n"
                for user, count in sorted(
                    by_user.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]:
                    response += f"  • المستخدم {user}: {count} رسالة\n"
                response += "\n"
            
            if by_keyword:
                response += "🔑 أكثر الكلمات المفتاحية:\n"
                for keyword, count in sorted(
                    by_keyword.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]:
                    response += f"  • {keyword}: {count} مرة\n"
            
            await update.message.reply_text(response)
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على الملخص: {e}")
            await update.message.reply_text(
                f"❌ حدث خطأ: {str(e)}"
            )
        
        finally:
            db.close()
    
    @staticmethod
    def get_handlers():
        """الحصول على معالجات الأوامر"""
        return [
            CommandHandler("cleanup_old", CleanupCommandHandler.cleanup_old_messages),
            CommandHandler("cleanup_user", CleanupCommandHandler.cleanup_user_messages),
            CommandHandler("archive_summary", CleanupCommandHandler.archive_summary),
        ]
