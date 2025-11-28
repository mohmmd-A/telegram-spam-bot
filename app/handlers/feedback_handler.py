"""
معالج التغذية الراجعة والتعلم الذاتي
Feedback Handler for Self-Learning
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
import logging

from app.services.detection import detection_engine
from app.models.init_db import SessionLocal
from app.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class FeedbackHandler:
    """معالج التغذية الراجعة والتحسن الذاتي"""
    
    @staticmethod
    async def report_false_positive(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /report_fp - الإبلاغ عن إيجابي خاطئ (رسالة تم حذفها بالخطأ)
        الاستخدام: /report_fp <رقم الرسالة>
        """
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id, update.effective_user.id
            )
            if member.status not in ['creator', 'administrator']:
                await update.message.reply_text(
                    "❌ هذا الأمر متاح فقط للمسؤولين."
                )
                return
        except Exception as e:
            logger.error(f"خطأ في التحقق من الصلاحيات: {e}")
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ الاستخدام: /report_fp <الكلمات المفتاحية>\n\n"
                "مثال: /report_fp إجازة مرضية\n\n"
                "هذا يخبر البوت أن هذه الكلمات ليست مزعجة وتقلل درجتها."
            )
            return
        
        keywords = ' '.join(context.args)
        
        try:
            # تسجيل الإيجابي الخاطئ
            detection_engine.add_false_positive("", keywords.split())
            
            await update.message.reply_text(
                f"✅ تم تسجيل الإيجابي الخاطئ!\n\n"
                f"📝 الكلمات: {keywords}\n"
                f"📊 تم تقليل درجة هذه الكلمات بنسبة 5%\n\n"
                f"شكراً على مساعدتك في تحسين البوت!"
            )
            
            logger.info(f"تم تسجيل إيجابي خاطئ: {keywords}")
        
        except Exception as e:
            logger.error(f"خطأ في تسجيل الإيجابي الخاطئ: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
    
    @staticmethod
    async def report_false_negative(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /report_fn - الإبلاغ عن سلبي خاطئ (رسالة مزعجة لم يتم اكتشافها)
        الاستخدام: /report_fn <الكلمات المفتاحية>
        """
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id, update.effective_user.id
            )
            if member.status not in ['creator', 'administrator']:
                await update.message.reply_text(
                    "❌ هذا الأمر متاح فقط للمسؤولين."
                )
                return
        except Exception as e:
            logger.error(f"خطأ في التحقق من الصلاحيات: {e}")
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ الاستخدام: /report_fn <الكلمات المفتاحية>\n\n"
                "مثال: /report_fn إجازة مرضية\n\n"
                "هذا يخبر البوت أن هذه الكلمات مزعجة وتزيد درجتها."
            )
            return
        
        keywords = ' '.join(context.args)
        
        try:
            # تسجيل السلبي الخاطئ
            detection_engine.add_false_negative("", keywords.split())
            
            await update.message.reply_text(
                f"✅ تم تسجيل السلبي الخاطئ!\n\n"
                f"📝 الكلمات: {keywords}\n"
                f"📊 تم زيادة درجة هذه الكلمات بنسبة 5%\n\n"
                f"شكراً على مساعدتك في تحسين البوت!"
            )
            
            logger.info(f"تم تسجيل سلبي خاطئ: {keywords}")
        
        except Exception as e:
            logger.error(f"خطأ في تسجيل السلبي الخاطئ: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
    
    @staticmethod
    async def show_learning_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /learning_stats - عرض إحصائيات التعلم الذاتي
        """
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id, update.effective_user.id
            )
            if member.status not in ['creator', 'administrator']:
                await update.message.reply_text(
                    "❌ هذا الأمر متاح فقط للمسؤولين."
                )
                return
        except Exception as e:
            logger.error(f"خطأ في التحقق من الصلاحيات: {e}")
            return
        
        try:
            stats = detection_engine.get_learning_stats()
            
            # تنسيق أفضل الكلمات
            top_keywords_text = ""
            if stats['top_keywords']:
                top_keywords_text = "🔑 أفضل الكلمات المكتشفة:\n"
                for keyword, count in stats['top_keywords']:
                    top_keywords_text += f"  • {keyword}: {count} مرة\n"
            
            response = f"""
📊 **إحصائيات التعلم الذاتي:**

📈 **الإحصائيات العامة:**
• إجمالي الكشوفات: {stats['total_detections']}
• إيجابيات خاطئة: {stats['false_positives']}
• سلبيات خاطئة: {stats['false_negatives']}
• دقة الكشف: {stats['accuracy']:.1f}%

{top_keywords_text}

💡 **كيفية التحسن:**
• استخدم /report_fp لتصحيح الأخطاء
• استخدم /report_fn لإضافة كلمات جديدة
• كل تصحيح يحسّن دقة البوت
"""
            
            await update.message.reply_text(response, parse_mode="Markdown")
        
        except Exception as e:
            logger.error(f"خطأ في عرض إحصائيات التعلم: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
    
    @staticmethod
    def get_handlers():
        """الحصول على معالجات الأوامر"""
        return [
            CommandHandler("report_fp", FeedbackHandler.report_false_positive),
            CommandHandler("report_fn", FeedbackHandler.report_false_negative),
            CommandHandler("learning_stats", FeedbackHandler.show_learning_stats),
        ]
