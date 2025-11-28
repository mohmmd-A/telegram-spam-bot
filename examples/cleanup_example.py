"""
مثال عملي: استخدام أمر cleanup_old
Example: Using cleanup_old command

هذا المثال يوضح كيفية استخدام أمر /cleanup_old لحذف الرسائل الأقدم من أسبوعين
"""

from telegram import Update
from telegram.ext import ContextTypes
from app.services.cleanup_service import CleanupService
from app.models.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# مثال 1: استخدام بسيط - حذف الرسائل الأقدم من 14 يوم
# ============================================================================

async def example_cleanup_two_weeks():
    """
    مثال بسيط: حذف الرسائل الأقدم من أسبوعين (14 يوم)
    
    الاستخدام في القروب:
    /cleanup_old 14
    """
    
    # معرف القروب (استبدل بمعرف قروبك الفعلي)
    chat_id = -1001234567890
    days = 14
    
    # إنشاء جلسة قاعدة البيانات
    db = SessionLocal()
    
    try:
        # استدعاء خدمة التنظيف
        result = await CleanupService.cleanup_old_messages(
            context=None,  # يمكن أن يكون None في هذا المثال
            db=db,
            chat_id=chat_id,
            days=days
        )
        
        # طباعة النتيجة
        print("✅ تم التنظيف بنجاح!")
        print(f"\n📊 الإحصائيات:")
        print(f"• تم حذف: {result['deleted_count']} رسالة")
        print(f"• فشل: {result['failed_count']} رسالة")
        print(f"• إجمالي المعالج: {result['total_processed']} رسالة")
        print(f"• الفترة: أكثر من {result['days']} يوم")
        
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
    
    finally:
        db.close()


# ============================================================================
# مثال 2: استخدام متقدم - حذف الرسائل مع معالجة الأخطاء
# ============================================================================

async def example_cleanup_with_error_handling():
    """
    مثال متقدم: حذف الرسائل مع معالجة شاملة للأخطاء
    """
    
    chat_id = -1001234567890
    days = 14
    
    db = SessionLocal()
    
    try:
        print(f"⏳ جاري تنظيف الرسائل الإعلانية القديمة (أكثر من {days} يوم)...")
        
        result = await CleanupService.cleanup_old_messages(
            context=None,
            db=db,
            chat_id=chat_id,
            days=days
        )
        
        # فحص النتيجة
        if result['deleted_count'] == 0:
            print("ℹ️ لا توجد رسائل قديمة للحذف")
        else:
            print("✅ تم التنظيف بنجاح!")
            print(f"\n📊 الإحصائيات:")
            print(f"• تم حذف: {result['deleted_count']} رسالة")
            print(f"• فشل: {result['failed_count']} رسالة")
            print(f"• إجمالي المعالج: {result['total_processed']} رسالة")
            
            # حساب نسبة النجاح
            if result['total_processed'] > 0:
                success_rate = (result['deleted_count'] / result['total_processed']) * 100
                print(f"• نسبة النجاح: {success_rate:.1f}%")
    
    except ValueError as e:
        print(f"❌ خطأ في القيم: {e}")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
    
    finally:
        db.close()


# ============================================================================
# مثال 3: استخدام في معالج الأوامر (كما يستخدم البوت)
# ============================================================================

async def example_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    مثال: معالج أمر /cleanup_old في البوت
    
    الاستخدام:
    /cleanup_old 14
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
        return
    
    # الحصول على عدد الأيام من الأمر
    days = 14  # القيمة الافتراضية
    if context.args and context.args[0].isdigit():
        days = int(context.args[0])
    
    # إرسال رسالة الانتظار
    status_msg = await update.message.reply_text(
        f"⏳ جاري تنظيف الرسائل الإعلانية القديمة (أكثر من {days} يوم)..."
    )
    
    db = SessionLocal()
    
    try:
        # تنفيذ التنظيف
        result = await CleanupService.cleanup_old_messages(
            context, db, update.effective_chat.id, days=days
        )
        
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
    
    finally:
        db.close()


# ============================================================================
# مثال 4: استخدام متعدد - حذف رسائل من فترات مختلفة
# ============================================================================

async def example_multiple_cleanups():
    """
    مثال: حذف رسائل من فترات زمنية مختلفة
    """
    
    chat_id = -1001234567890
    db = SessionLocal()
    
    cleanup_periods = [
        (7, "أسبوع واحد"),
        (14, "أسبوعان"),
        (30, "شهر واحد"),
    ]
    
    try:
        print("🧹 جاري تنظيف الرسائل من فترات مختلفة...\n")
        
        for days, period_name in cleanup_periods:
            print(f"📍 تنظيف الرسائل الأقدم من {period_name} ({days} يوم)...")
            
            result = await CleanupService.cleanup_old_messages(
                context=None,
                db=db,
                chat_id=chat_id,
                days=days
            )
            
            print(f"   ✅ تم حذف {result['deleted_count']} رسالة\n")
    
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    finally:
        db.close()


# ============================================================================
# مثال 5: جدولة التنظيف الدوري
# ============================================================================

def example_schedule_periodic_cleanup(application):
    """
    مثال: جدولة تنظيف دوري كل 24 ساعة
    """
    
    chat_id = -1001234567890
    
    # جدولة التنظيف الدوري
    CleanupService.schedule_periodic_cleanup(
        application,
        chat_id=chat_id,
        interval_hours=24  # كل 24 ساعة
    )
    
    print("✅ تم جدولة التنظيف الدوري (كل 24 ساعة)")


# ============================================================================
# مثال 6: مقارنة النتائج قبل وبعد
# ============================================================================

async def example_cleanup_comparison():
    """
    مثال: مقارنة عدد الرسائل قبل وبعد التنظيف
    """
    
    from app.models.database import DeletedMessage
    
    chat_id = -1001234567890
    days = 14
    
    db = SessionLocal()
    
    try:
        # عد الرسائل قبل التنظيف
        messages_before = db.query(DeletedMessage).filter(
            DeletedMessage.chat_id == chat_id
        ).count()
        
        print(f"📊 الرسائل قبل التنظيف: {messages_before}")
        
        # تنفيذ التنظيف
        result = await CleanupService.cleanup_old_messages(
            context=None,
            db=db,
            chat_id=chat_id,
            days=days
        )
        
        # عد الرسائل بعد التنظيف
        messages_after = db.query(DeletedMessage).filter(
            DeletedMessage.chat_id == chat_id
        ).count()
        
        print(f"📊 الرسائل بعد التنظيف: {messages_after}")
        print(f"📊 الفرق: {messages_before - messages_after} رسالة")
        print(f"\n✅ تم حذف {result['deleted_count']} رسالة بنجاح!")
    
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    finally:
        db.close()


# ============================================================================
# تشغيل الأمثلة
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    print("=" * 60)
    print("أمثلة عملية: استخدام أمر /cleanup_old")
    print("=" * 60)
    print()
    
    # تشغيل المثال الأول
    print("📌 المثال 1: استخدام بسيط")
    print("-" * 60)
    # asyncio.run(example_cleanup_two_weeks())
    print("(تم تعطيل التشغيل - استخدم في بيئة حقيقية)")
    print()
    
    # تشغيل المثال الثاني
    print("📌 المثال 2: استخدام متقدم")
    print("-" * 60)
    # asyncio.run(example_cleanup_with_error_handling())
    print("(تم تعطيل التشغيل - استخدم في بيئة حقيقية)")
    print()
    
    print("=" * 60)
    print("✅ للاستخدام الفعلي، استدعِ الدوال من البوت الرئيسي")
    print("=" * 60)
