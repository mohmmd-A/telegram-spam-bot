"""
خدمة تنظيف وحذف الرسائل القديمة
Message Cleanup Service
"""

from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from telegram.ext import ContextTypes
from telegram.error import TelegramError
import logging

from app.models.database import DeletedMessage, ActivityLog

logger = logging.getLogger(__name__)


class CleanupService:
    """خدمة تنظيف الرسائل القديمة"""
    
    @staticmethod
    async def cleanup_old_messages(
        context: ContextTypes.DEFAULT_TYPE,
        db: Session,
        chat_id: int,
        days: int = 30
    ) -> Dict:
        """
        حذف الرسائل الإعلانية القديمة من القروب
        
        Args:
            context: سياق البوت
            db: جلسة قاعدة البيانات
            chat_id: معرف القروب
            days: عدد الأيام (حذف الرسائل الأقدم من هذا العدد)
            
        Returns:
            قاموس بإحصائيات الحذف
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # الحصول على الرسائل المحذوفة القديمة
        old_messages = db.query(DeletedMessage).filter(
            DeletedMessage.chat_id == chat_id,
            DeletedMessage.deleted_at < cutoff_date,
            DeletedMessage.is_restored == False
        ).all()
        
        deleted_count = 0
        failed_count = 0
        
        for msg in old_messages:
            try:
                # محاولة حذف الرسالة من القروب (إذا كانت موجودة)
                await context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=msg.message_id
                )
                deleted_count += 1
                
                # تسجيل الحذف
                msg.is_restored = True
                db.commit()
                
            except TelegramError as e:
                # الرسالة قد تكون محذوفة بالفعل أو انتهت صلاحيتها
                failed_count += 1
                logger.debug(f"لم يتمكن من حذف الرسالة {msg.message_id}: {e}")
        
        # تسجيل النشاط
        from app.services.database_service import DatabaseService
        DatabaseService.log_activity(
            db, chat_id, "cleanup_old_messages",
            f"تم تنظيف {deleted_count} رسالة قديمة (فشل: {failed_count})"
        )
        
        return {
            "deleted_count": deleted_count,
            "failed_count": failed_count,
            "total_processed": len(old_messages),
            "cutoff_date": cutoff_date.isoformat(),
            "days": days
        }
    
    @staticmethod
    async def cleanup_by_user(
        context: ContextTypes.DEFAULT_TYPE,
        db: Session,
        chat_id: int,
        user_id: int
    ) -> Dict:
        """
        حذف جميع الرسائل الإعلانية لمستخدم معين
        """
        messages = db.query(DeletedMessage).filter(
            DeletedMessage.chat_id == chat_id,
            DeletedMessage.user_id == user_id,
            DeletedMessage.is_restored == False
        ).all()
        
        deleted_count = 0
        
        for msg in messages:
            try:
                await context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=msg.message_id
                )
                deleted_count += 1
                msg.is_restored = True
                db.commit()
            except TelegramError:
                pass
        
        from app.services.database_service import DatabaseService
        DatabaseService.log_activity(
            db, chat_id, "cleanup_user_messages",
            f"تم حذف {deleted_count} رسالة للمستخدم {user_id}"
        )
        
        return {
            "deleted_count": deleted_count,
            "user_id": user_id
        }
    
    @staticmethod
    def schedule_periodic_cleanup(application, chat_id: int, interval_hours: int = 24):
        """
        جدولة تنظيف دوري للرسائل
        """
        async def cleanup_job(context):
            db = None
            try:
                from app.models.init_db import SessionLocal
                db = SessionLocal()
                
                result = await CleanupService.cleanup_old_messages(
                    context, db, chat_id, days=30
                )
                
                logger.info(f"تم تنظيف دوري: {result}")
            
            except Exception as e:
                logger.error(f"خطأ في التنظيف الدوري: {e}")
            
            finally:
                if db:
                    db.close()
        
        # جدولة المهمة
        application.job_queue.run_repeating(
            cleanup_job,
            interval=interval_hours * 3600,
            first=interval_hours * 3600
        )


class MessageArchiver:
    """أرشيف الرسائل المحذوفة"""
    
    @staticmethod
    def get_archive_summary(db: Session, chat_id: int, days: int = 7) -> Dict:
        """الحصول على ملخص الرسائل المحذوفة"""
        since = datetime.utcnow() - timedelta(days=days)
        
        messages = db.query(DeletedMessage).filter(
            DeletedMessage.chat_id == chat_id,
            DeletedMessage.deleted_at >= since
        ).all()
        
        # تجميع الإحصائيات
        by_user = {}
        by_keyword = {}
        
        for msg in messages:
            # حسب المستخدم
            if msg.user_name not in by_user:
                by_user[msg.user_name] = 0
            by_user[msg.user_name] += 1
            
            # حسب الكلمات المفتاحية
            if msg.detected_keywords:
                import json
                keywords = json.loads(msg.detected_keywords)
                for kw in keywords:
                    if kw not in by_keyword:
                        by_keyword[kw] = 0
                    by_keyword[kw] += 1
        
        return {
            "total_messages": len(messages),
            "by_user": by_user,
            "by_keyword": by_keyword,
            "period_days": days,
            "period_start": since.isoformat()
        }
    
    @staticmethod
    def export_archive(db: Session, chat_id: int, format: str = "json") -> str:
        """تصدير أرشيف الرسائل"""
        messages = db.query(DeletedMessage).filter(
            DeletedMessage.chat_id == chat_id
        ).all()
        
        if format == "json":
            import json
            data = []
            for msg in messages:
                data.append({
                    "message_id": msg.message_id,
                    "user_name": msg.user_name,
                    "text": msg.message_text,
                    "keywords": json.loads(msg.detected_keywords),
                    "confidence": msg.confidence_score,
                    "deleted_at": msg.deleted_at.isoformat()
                })
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        elif format == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Message ID", "User", "Text", "Confidence", "Deleted At"])
            
            for msg in messages:
                writer.writerow([
                    msg.message_id,
                    msg.user_name,
                    msg.message_text[:50],
                    f"{msg.confidence_score:.2%}",
                    msg.deleted_at
                ])
            
            return output.getvalue()
        
        return ""
