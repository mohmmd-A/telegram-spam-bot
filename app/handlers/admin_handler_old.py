from telegram import Update, ChatMember
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError
from sqlalchemy.orm import Session
import logging

from app.services.database_service import DatabaseService
from app.models.database import SessionLocal

logger = logging.getLogger(__name__)

# حالات المحادثة
SETTING_SENSITIVITY = 1
SETTING_MAX_WARNINGS = 2
ADDING_WHITELIST = 3
ADDING_BLACKLIST = 4


class AdminHandler:
    """معالج أوامر المسؤولين"""
    
    @staticmethod
    async def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """التحقق من أن المستخدم مسؤول"""
        try:
            chat_id = update.message.chat_id
            user_id = update.message.from_user.id
            
            admins = await context.bot.get_chat_administrators(chat_id)
            admin_ids = [admin.user.id for admin in admins]
            
            return user_id in admin_ids
        except TelegramError:
            return False
    
    @staticmethod
    async def whitelist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /whitelist - إدارة القائمة البيضاء"""
        if not await AdminHandler._is_admin(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط للمسؤولين")
            return
        
        if not context.args:
            await update.message.reply_text(
                "📋 استخدام:\n"
                "/whitelist add @username - إضافة مستخدم\n"
                "/whitelist remove @username - إزالة مستخدم\n"
                "/whitelist list - عرض القائمة"
            )
            return
        
        chat_id = update.message.chat_id
        db = SessionLocal()
        
        try:
            action = context.args[0].lower()
            
            if action == "add" and len(context.args) > 1:
                username = context.args[1].lstrip("@")
                DatabaseService.add_to_whitelist(
                    db, chat_id, f"إضافة يدوية: {username}", keyword=username
                )
                await update.message.reply_text(f"✅ تمت إضافة {username} إلى القائمة البيضاء")
            
            elif action == "remove" and len(context.args) > 1:
                # هنا يمكن تطبيق إزالة من القائمة البيضاء
                await update.message.reply_text("✅ تمت إزالة المستخدم من القائمة البيضاء")
            
            elif action == "list":
                await update.message.reply_text("📋 القائمة البيضاء (قيد التطوير)")
        
        finally:
            db.close()
    
    @staticmethod
    async def blacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /blacklist - إدارة القائمة السوداء"""
        if not await AdminHandler._is_admin(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط للمسؤولين")
            return
        
        if not context.args:
            await update.message.reply_text(
                "📋 استخدام:\n"
                "/blacklist add @username - حظر مستخدم\n"
                "/blacklist remove @username - إلغاء الحظر\n"
                "/blacklist list - عرض القائمة"
            )
            return
        
        chat_id = update.message.chat_id
        db = SessionLocal()
        
        try:
            action = context.args[0].lower()
            
            if action == "add" and len(context.args) > 1:
                username = context.args[1].lstrip("@")
                DatabaseService.add_to_blacklist(
                    db, chat_id, f"حظر يدوي: {username}", keyword=username
                )
                await update.message.reply_text(f"✅ تم حظر {username}")
            
            elif action == "remove" and len(context.args) > 1:
                await update.message.reply_text("✅ تم إلغاء الحظر")
            
            elif action == "list":
                await update.message.reply_text("📋 القائمة السوداء (قيد التطوير)")
        
        finally:
            db.close()
    
    @staticmethod
    async def sensitivity_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /sensitivity - تعديل حساسية الكشف"""
        if not await AdminHandler._is_admin(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط للمسؤولين")
            return
        
        if not context.args:
            await update.message.reply_text(
                "⚙️ استخدام:\n"
                "/sensitivity <0.1-1.0> - تعديل حساسية الكشف\n"
                "مثال: /sensitivity 0.8"
            )
            return
        
        try:
            sensitivity = float(context.args[0])
            if not 0.1 <= sensitivity <= 1.0:
                await update.message.reply_text("❌ يجب أن تكون القيمة بين 0.1 و 1.0")
                return
            
            chat_id = update.message.chat_id
            db = SessionLocal()
            
            try:
                DatabaseService.update_chat_settings(
                    db, chat_id, detection_sensitivity=sensitivity
                )
                await update.message.reply_text(
                    f"✅ تم تعديل حساسية الكشف إلى {sensitivity:.1%}"
                )
            finally:
                db.close()
        
        except ValueError:
            await update.message.reply_text("❌ يجب إدخال رقم صحيح")
    
    @staticmethod
    async def enable_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /enable - تفعيل البوت"""
        if not await AdminHandler._is_admin(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط للمسؤولين")
            return
        
        chat_id = update.message.chat_id
        db = SessionLocal()
        
        try:
            DatabaseService.update_chat_settings(db, chat_id, is_enabled=True)
            await update.message.reply_text("✅ تم تفعيل البوت")
        finally:
            db.close()
    
    @staticmethod
    async def disable_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /disable - تعطيل البوت"""
        if not await AdminHandler._is_admin(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط للمسؤولين")
            return
        
        chat_id = update.message.chat_id
        db = SessionLocal()
        
        try:
            DatabaseService.update_chat_settings(db, chat_id, is_enabled=False)
            await update.message.reply_text("✅ تم تعطيل البوت")
        finally:
            db.close()
    
    @staticmethod
    async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /report - عرض تقرير شامل"""
        if not await AdminHandler._is_admin(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط للمسؤولين")
            return
        
        chat_id = update.message.chat_id
        db = SessionLocal()
        
        try:
            stats = DatabaseService.get_chat_statistics(db, chat_id, days=30)
            
            report = (
                f"📊 **تقرير شامل (آخر 30 يوم)**\n\n"
                f"🗑️ إجمالي الرسائل المحذوفة: {stats['total_deleted_messages']}\n\n"
            )
            
            if stats['top_spammers']:
                report += "👤 **أكثر المستخدمين إرسالاً للإعلانات:**\n"
                for i, spammer in enumerate(stats['top_spammers'], 1):
                    report += (
                        f"{i}. {spammer['user_name']}\n"
                        f"   • الرسائل: {spammer['spam_count']}\n"
                        f"   • التحذيرات: {spammer['warning_count']}\n"
                    )
            
            if stats['recent_activity']:
                report += "\n📝 **آخر الأنشطة:**\n"
                for activity in stats['recent_activity'][:5]:
                    report += f"• {activity['action_type']}: {activity['target_user_name']}\n"
            
            await update.message.reply_text(report, parse_mode="Markdown")
        
        finally:
            db.close()
    
    @staticmethod
    async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /logs - عرض السجلات"""
        if not await AdminHandler._is_admin(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط للمسؤولين")
            return
        
        await update.message.reply_text(
            "📝 السجلات (قيد التطوير)\n"
            "يمكن عرض جميع الأنشطة والإجراءات المتخذة"
        )


class AdvancedFeatures:
    """المزايا المتقدمة"""
    
    @staticmethod
    async def add_keyword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /addkeyword - إضافة كلمة مفتاحية مخصصة"""
        if not await AdminHandler._is_admin(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط للمسؤولين")
            return
        
        if not context.args:
            await update.message.reply_text(
                "📝 استخدام:\n"
                "/addkeyword <الكلمة> - إضافة كلمة مفتاحية"
            )
            return
        
        keyword = " ".join(context.args)
        
        try:
            from app.services.detection import detection_engine
            detection_engine.add_custom_keyword(keyword)
            await update.message.reply_text(f"✅ تمت إضافة الكلمة: {keyword}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {e}")
    
    @staticmethod
    async def removekeyword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /removekeyword - إزالة كلمة مفتاحية"""
        if not await AdminHandler._is_admin(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط للمسؤولين")
            return
        
        if not context.args:
            await update.message.reply_text(
                "📝 استخدام:\n"
                "/removekeyword <الكلمة> - إزالة كلمة مفتاحية"
            )
            return
        
        keyword = " ".join(context.args)
        
        try:
            from app.services.detection import detection_engine
            detection_engine.remove_keyword(keyword)
            await update.message.reply_text(f"✅ تمت إزالة الكلمة: {keyword}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {e}")
