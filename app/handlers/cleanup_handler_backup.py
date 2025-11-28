"""
معالج أوامر التنظيف والحذف
Cleanup and Deletion Commands Handler
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from app.services.cleanup_service import CleanupService, MessageArchiver
from app.models.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


class CleanupCommandHandler:
    """معالج أوامر التنظيف والحذف"""
    
    @staticmethod
    async def cleanup_old_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /cleanup_old - حذف الرسائل الإعلانية القديمة
        """
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        member = await context.bot.get_chat_member(
            update.effective_chat.id, update.effective_user.id
        )
        
        if not member.can_delete_messages:
            await update.message.reply_text(
                "❌ عذراً، ليس لديك صلاحية حذف الرسائل في هذا القروب."
            )
            return
        
        # الحصول على عدد الأيام من الأمر
        days = 30
        if context.args and context.args[0].isdigit():
            days = int(context.args[0])
        
        # إرسال رسالة الانتظار
        status_msg = await update.message.reply_text(
            f"⏳ جاري تنظيف الرسائل الإعلانية القديمة (أكثر من {days} يوم)..."
        )
        
        try:
            db = SessionLocal()
            result = await CleanupService.cleanup_old_messages(
                context, db, update.effective_chat.id, days=days
            )
            db.close()
            
            # إرسال النتيجة
            response = (
                f"✅ تم التنظيف بنجاح!\n\n"
                f"📊 الإحصائيات:\n"
                f"• تم حذف: {result['deleted_count']} رسالة\n"
                f"• فشل: {result['failed_count']} رسالة\n"
                f"• إجمالي المعالج: {result['total_processed']} رسالة\n"
                f"• الفترة: أكثر من {result['days']} يوم"
            )
            
            await status_msg.edit_text(response)
        
        except Exception as e:
            logger.error(f"خطأ في التنظيف: {e}")
            await status_msg.edit_text(
                f"❌ حدث خطأ أثناء التنظيف: {str(e)}"
            )
    
    @staticmethod
    async def cleanup_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /cleanup_user <user_id> - حذف جميع رسائل مستخدم معين
        """
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        member = await context.bot.get_chat_member(
            update.effective_chat.id, update.effective_user.id
        )
        
        if not member.can_delete_messages:
            await update.message.reply_text(
                "❌ عذراً، ليس لديك صلاحية حذف الرسائل."
            )
            return
        
        # الحصول على معرف المستخدم
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text(
                "❌ الاستخدام: /cleanup_user <user_id>"
            )
            return
        
        user_id = int(context.args[0])
        
        status_msg = await update.message.reply_text(
            f"⏳ جاري حذف رسائل المستخدم {user_id}..."
        )
        
        try:
            db = SessionLocal()
            result = await CleanupService.cleanup_by_user(
                context, db, update.effective_chat.id, user_id
            )
            db.close()
            
            response = (
                f"✅ تم الحذف بنجاح!\n\n"
                f"📊 الإحصائيات:\n"
                f"• تم حذف: {result['deleted_count']} رسالة\n"
                f"• المستخدم: {user_id}"
            )
            
            await status_msg.edit_text(response)
        
        except Exception as e:
            logger.error(f"خطأ في حذف رسائل المستخدم: {e}")
            await status_msg.edit_text(
                f"❌ حدث خطأ: {str(e)}"
            )
    
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
        
        try:
            db = SessionLocal()
            summary = MessageArchiver.get_archive_summary(
                db, update.effective_chat.id, days=days
            )
            db.close()
            
            # تنسيق الرسالة
            response = f"📊 ملخص الرسائل المحذوفة (آخر {days} يوم):\n\n"
            response += f"📈 إجمالي الرسائل: {summary['total_messages']}\n\n"
            
            if summary['by_user']:
                response += "👥 أكثر المستخدمين إرسالاً:\n"
                for user, count in sorted(
                    summary['by_user'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]:
                    response += f"  • {user}: {count} رسالة\n"
                response += "\n"
            
            if summary['by_keyword']:
                response += "🔑 أكثر الكلمات المفتاحية:\n"
                for keyword, count in sorted(
                    summary['by_keyword'].items(),
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
    
    @staticmethod
    async def export_archive(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /export_archive <format> - تصدير أرشيف الرسائل
        Format: json أو csv
        """
        if not update.message or not update.effective_chat:
            return
        
        # الحصول على الصيغة
        format_type = "json"
        if context.args:
            format_type = context.args[0].lower()
        
        if format_type not in ["json", "csv"]:
            await update.message.reply_text(
                "❌ الصيغ المدعومة: json أو csv"
            )
            return
        
        try:
            db = SessionLocal()
            archive_data = MessageArchiver.export_archive(
                db, update.effective_chat.id, format=format_type
            )
            db.close()
            
            # إرسال الملف
            filename = f"archive.{format_type}"
            await update.message.reply_document(
                document=archive_data.encode('utf-8'),
                filename=filename,
                caption=f"📄 أرشيف الرسائل ({format_type.upper()})"
            )
        
        except Exception as e:
            logger.error(f"خطأ في تصدير الأرشيف: {e}")
            await update.message.reply_text(
                f"❌ حدث خطأ: {str(e)}"
            )
    
    @staticmethod
    def get_handlers():
        """الحصول على معالجات الأوامر"""
        return [
            CommandHandler("cleanup_old", CleanupCommandHandler.cleanup_old_messages),
            CommandHandler("cleanup_user", CleanupCommandHandler.cleanup_user_messages),
            CommandHandler("archive_summary", CleanupCommandHandler.archive_summary),
            CommandHandler("export_archive", CleanupCommandHandler.export_archive),
        ]
