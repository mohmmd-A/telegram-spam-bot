"""
معالج أوامر المسؤولين - النسخة الكاملة
Admin Commands Handler - Complete Version
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from app.models.database import SessionLocal
from app.services.database_service import DatabaseService
import logging

logger = logging.getLogger(__name__)


class AdminHandler:
    """معالج أوامر المسؤولين"""
    
    @staticmethod
    async def enable_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تفعيل البوت"""
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        if not await AdminHandler._check_admin(update, context):
            return
        
        db = SessionLocal()
        try:
            chat_id = update.effective_chat.id
            DatabaseService.set_chat_enabled(db, chat_id, True)
            
            await update.message.reply_text(
                "✅ تم تفعيل البوت بنجاح!\n\n"
                "🤖 البوت الآن يراقب الرسائل ويحذف الإعلانات المزعجة."
            )
        except Exception as e:
            logger.error(f"خطأ في تفعيل البوت: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    async def disable_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تعطيل البوت"""
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        if not await AdminHandler._check_admin(update, context):
            return
        
        db = SessionLocal()
        try:
            chat_id = update.effective_chat.id
            DatabaseService.set_chat_enabled(db, chat_id, False)
            
            await update.message.reply_text(
                "❌ تم تعطيل البوت.\n\n"
                "🔇 البوت الآن لن يراقب الرسائل أو يحذفها."
            )
        except Exception as e:
            logger.error(f"خطأ في تعطيل البوت: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    async def set_sensitivity(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تعديل حساسية الكشف"""
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        if not await AdminHandler._check_admin(update, context):
            return
        
        if not context.args or not context.args[0]:
            await update.message.reply_text(
                "❌ الاستخدام: /sensitivity <رقم من 0.1 إلى 1.0>\n\n"
                "أمثلة:\n"
                "  /sensitivity 0.5  (حساسية منخفضة)\n"
                "  /sensitivity 0.7  (حساسية متوسطة)\n"
                "  /sensitivity 0.9  (حساسية عالية)"
            )
            return
        
        try:
            sensitivity = float(context.args[0])
            
            if not 0.1 <= sensitivity <= 1.0:
                await update.message.reply_text(
                    "❌ الرقم يجب أن يكون بين 0.1 و 1.0"
                )
                return
            
            db = SessionLocal()
            DatabaseService.set_chat_sensitivity(db, update.effective_chat.id, sensitivity)
            db.close()
            
            await update.message.reply_text(
                f"✅ تم تعديل حساسية الكشف إلى {sensitivity * 100:.0f}%\n\n"
                f"📊 التفسير:\n"
                f"  • 0.1 = حساسية منخفضة جداً (قد تفوت بعض الإعلانات)\n"
                f"  • 0.5 = حساسية متوسطة (متوازن)\n"
                f"  • 1.0 = حساسية عالية جداً (قد تحذف رسائل عادية)"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ الرجاء إدخال رقم صحيح (مثل 0.5 أو 0.7)"
            )
    
    @staticmethod
    async def manage_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدارة القائمة البيضاء"""
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        if not await AdminHandler._check_admin(update, context):
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ الاستخدام: /whitelist <user_id>\n\n"
                "مثال: /whitelist 123456789\n\n"
                "💡 المستخدمون في القائمة البيضاء لن يتم حذف رسائلهم."
            )
            return
        
        try:
            user_id = int(context.args[0])
            db = SessionLocal()
            
            DatabaseService.add_user_to_whitelist(
                db, update.effective_chat.id, user_id
            )
            db.close()
            
            await update.message.reply_text(
                f"✅ تم إضافة المستخدم {user_id} إلى القائمة البيضاء\n\n"
                f"🔐 رسائل هذا المستخدم لن يتم حذفها."
            )
        except ValueError:
            await update.message.reply_text(
                "❌ الرجاء إدخال معرف مستخدم صحيح (أرقام فقط)"
            )
        except Exception as e:
            logger.error(f"خطأ في إضافة المستخدم للقائمة البيضاء: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
    
    @staticmethod
    async def manage_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدارة القائمة السوداء"""
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        if not await AdminHandler._check_admin(update, context):
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ الاستخدام: /blacklist <user_id>\n\n"
                "مثال: /blacklist 123456789\n\n"
                "⚠️ رسائل المستخدمين في القائمة السوداء سيتم حذفها تلقائياً."
            )
            return
        
        try:
            user_id = int(context.args[0])
            db = SessionLocal()
            
            DatabaseService.add_user_to_blacklist(
                db, update.effective_chat.id, user_id
            )
            db.close()
            
            await update.message.reply_text(
                f"✅ تم إضافة المستخدم {user_id} إلى القائمة السوداء\n\n"
                f"⚠️ جميع رسائل هذا المستخدم ستُحذف تلقائياً."
            )
        except ValueError:
            await update.message.reply_text(
                "❌ الرجاء إدخال معرف مستخدم صحيح (أرقام فقط)"
            )
        except Exception as e:
            logger.error(f"خطأ في إضافة المستخدم للقائمة السوداء: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
    
    @staticmethod
    async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """توليد تقرير شامل"""
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        if not await AdminHandler._check_admin(update, context):
            return
        
        db = SessionLocal()
        try:
            chat_id = update.effective_chat.id
            stats = DatabaseService.get_chat_statistics(db, chat_id)
            
            report = f"""
📊 **تقرير شامل للقروب**

📈 **الإحصائيات العامة:**
• الرسائل المكتشفة: {stats.get('detected_count', 0)}
• الرسائل المحذوفة: {stats.get('deleted_count', 0)}
• نسبة الحذف: {stats.get('deletion_rate', 0):.1f}%

👥 **المستخدمون:**
• إجمالي المرسلين: {stats.get('user_count', 0)}
• في القائمة البيضاء: {stats.get('whitelist_count', 0)}
• في القائمة السوداء: {stats.get('blacklist_count', 0)}

🔑 **الكلمات المفتاحية:**
• الأكثر تكراراً: {stats.get('top_keyword', 'لا توجد')}
• عدد الكلمات المستخدمة: {stats.get('keyword_count', 0)}

⏰ **آخر تحديث:** الآن
"""
            
            await update.message.reply_text(report, parse_mode="Markdown")
        
        except Exception as e:
            logger.error(f"خطأ في توليد التقرير: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        
        finally:
            db.close()
    
    @staticmethod
    async def show_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض السجلات"""
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        if not await AdminHandler._check_admin(update, context):
            return
        
        days = 7
        if context.args and context.args[0].isdigit():
            days = int(context.args[0])
        
        db = SessionLocal()
        try:
            chat_id = update.effective_chat.id
            logs = DatabaseService.get_activity_logs(db, chat_id, days)
            
            if not logs:
                await update.message.reply_text(
                    f"ℹ️ لا توجد سجلات في آخر {days} يوم"
                )
                db.close()
                return
            
            logs_text = f"📝 **السجلات (آخر {days} يوم):**\n\n"
            
            for log in logs[:10]:  # آخر 10 سجلات
                logs_text += f"• {log.get('action', 'N/A')}\n"
                logs_text += f"  المستخدم: {log.get('user_name', 'N/A')}\n"
                logs_text += f"  الوقت: {log.get('timestamp', 'N/A')}\n\n"
            
            await update.message.reply_text(logs_text, parse_mode="Markdown")
        
        except Exception as e:
            logger.error(f"خطأ في عرض السجلات: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        
        finally:
            db.close()
    
    @staticmethod
    async def _check_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """التحقق من أن المستخدم مسؤول"""
        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id,
                update.effective_user.id
            )
            
            if not member.status in ['creator', 'administrator']:
                await update.message.reply_text(
                    "❌ عذراً، هذا الأمر متاح فقط للمسؤولين."
                )
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"خطأ في التحقق من الصلاحيات: {e}")
            await update.message.reply_text(
                "❌ خطأ في التحقق من الصلاحيات."
            )
            return False


class AdvancedFeatures:
    """معالج الميزات المتقدمة"""
    
    @staticmethod
    async def add_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة كلمة مفتاحية"""
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        if not await AdminHandler._check_admin(update, context):
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ الاستخدام: /addkeyword <الكلمة>\n\n"
                "مثال: /addkeyword إجازة مرضية"
            )
            return
        
        keyword = ' '.join(context.args)
        
        db = SessionLocal()
        try:
            DatabaseService.add_keyword(
                db, update.effective_chat.id, keyword
            )
            
            await update.message.reply_text(
                f"✅ تم إضافة الكلمة المفتاحية:\n"
                f"'{keyword}'\n\n"
                f"🔍 البوت الآن سيكتشف هذه الكلمة تلقائياً."
            )
        except Exception as e:
            logger.error(f"خطأ في إضافة الكلمة: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    async def remove_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إزالة كلمة مفتاحية"""
        if not update.message or not update.effective_chat:
            return
        
        # التحقق من الصلاحيات
        if not await AdminHandler._check_admin(update, context):
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ الاستخدام: /removekeyword <الكلمة>\n\n"
                "مثال: /removekeyword إجازة مرضية"
            )
            return
        
        keyword = ' '.join(context.args)
        
        db = SessionLocal()
        try:
            DatabaseService.remove_keyword(
                db, update.effective_chat.id, keyword
            )
            
            await update.message.reply_text(
                f"✅ تم إزالة الكلمة المفتاحية:\n"
                f"'{keyword}'"
            )
        except Exception as e:
            logger.error(f"خطأ في إزالة الكلمة: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    async def list_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الكلمات المفتاحية"""
        if not update.message or not update.effective_chat:
            return
        
        db = SessionLocal()
        try:
            chat_id = update.effective_chat.id
            keywords = DatabaseService.get_keywords(db, chat_id)
            
            if not keywords:
                await update.message.reply_text(
                    "📚 لا توجد كلمات مفتاحية مخصصة للقروب."
                )
                db.close()
                return
            
            keywords_text = "📚 **الكلمات المفتاحية المستخدمة:**\n\n"
            
            for i, keyword in enumerate(keywords, 1):
                keywords_text += f"{i}. {keyword}\n"
            
            await update.message.reply_text(keywords_text, parse_mode="Markdown")
        
        except Exception as e:
            logger.error(f"خطأ في عرض الكلمات: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        
        finally:
            db.close()
