from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json

from app.models.database import (
    DeletedMessage, UserStatistics, ChatSettings, 
    WhitelistEntry, BlacklistEntry, ActivityLog
)


class DatabaseService:
    """خدمة إدارة قاعدة البيانات"""
    
    @staticmethod
    def log_deleted_message(
        db: Session,
        chat_id: int,
        message_id: int,
        user_id: int,
        user_name: str,
        message_text: str,
        detected_keywords: List[str],
        confidence_score: float,
        deletion_reason: str = "spam_detected"
    ) -> DeletedMessage:
        """تسجيل رسالة محذوفة"""
        deleted_msg = DeletedMessage(
            chat_id=chat_id,
            message_id=message_id,
            user_id=user_id,
            user_name=user_name,
            message_text=message_text,
            detected_keywords=json.dumps(detected_keywords, ensure_ascii=False),
            confidence_score=confidence_score,
            deletion_reason=deletion_reason
        )
        db.add(deleted_msg)
        db.commit()
        db.refresh(deleted_msg)
        return deleted_msg
    
    @staticmethod
    def update_user_statistics(
        db: Session,
        chat_id: int,
        user_id: int,
        user_name: str,
        increment_spam: bool = True,
        increment_warning: bool = False
    ) -> UserStatistics:
        """تحديث إحصائيات المستخدم"""
        stats = db.query(UserStatistics).filter(
            UserStatistics.chat_id == chat_id,
            UserStatistics.user_id == user_id
        ).first()
        
        if not stats:
            stats = UserStatistics(
                chat_id=chat_id,
                user_id=user_id,
                user_name=user_name,
                spam_count=1 if increment_spam else 0,
                warning_count=1 if increment_warning else 0,
                last_spam_at=datetime.utcnow() if increment_spam else None
            )
            db.add(stats)
        else:
            if increment_spam:
                stats.spam_count += 1
                stats.last_spam_at = datetime.utcnow()
            if increment_warning:
                stats.warning_count += 1
            stats.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(stats)
        return stats
    
    @staticmethod
    def get_chat_settings(db: Session, chat_id: int) -> ChatSettings:
        """الحصول على إعدادات القروب"""
        settings = db.query(ChatSettings).filter(
            ChatSettings.chat_id == chat_id
        ).first()
        
        if not settings:
            settings = ChatSettings(chat_id=chat_id)
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return settings
    
    @staticmethod
    def update_chat_settings(
        db: Session,
        chat_id: int,
        **kwargs
    ) -> ChatSettings:
        """تحديث إعدادات القروب"""
        settings = DatabaseService.get_chat_settings(db, chat_id)
        
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        settings.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(settings)
        return settings
    
    @staticmethod
    def add_to_whitelist(
        db: Session,
        chat_id: int,
        reason: str,
        user_id: Optional[int] = None,
        keyword: Optional[str] = None
    ) -> WhitelistEntry:
        """إضافة مدخل إلى القائمة البيضاء"""
        entry = WhitelistEntry(
            chat_id=chat_id,
            user_id=user_id,
            keyword=keyword,
            reason=reason
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def add_to_blacklist(
        db: Session,
        chat_id: int,
        reason: str,
        user_id: Optional[int] = None,
        keyword: Optional[str] = None
    ) -> BlacklistEntry:
        """إضافة مدخل إلى القائمة السوداء"""
        entry = BlacklistEntry(
            chat_id=chat_id,
            user_id=user_id,
            keyword=keyword,
            reason=reason
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def is_user_whitelisted(db: Session, chat_id: int, user_id: int) -> bool:
        """التحقق من أن المستخدم في القائمة البيضاء"""
        return db.query(WhitelistEntry).filter(
            WhitelistEntry.chat_id == chat_id,
            WhitelistEntry.user_id == user_id
        ).first() is not None
    
    @staticmethod
    def is_user_blacklisted(db: Session, chat_id: int, user_id: int) -> bool:
        """التحقق من أن المستخدم في القائمة السوداء"""
        return db.query(BlacklistEntry).filter(
            BlacklistEntry.chat_id == chat_id,
            BlacklistEntry.user_id == user_id
        ).first() is not None
    
    @staticmethod
    def is_keyword_whitelisted(db: Session, chat_id: int, keyword: str) -> bool:
        """التحقق من أن الكلمة المفتاحية في القائمة البيضاء"""
        return db.query(WhitelistEntry).filter(
            WhitelistEntry.chat_id == chat_id,
            WhitelistEntry.keyword == keyword
        ).first() is not None
    
    @staticmethod
    def log_activity(
        db: Session,
        chat_id: int,
        action_type: str,
        details: str,
        target_user_id: Optional[int] = None,
        target_user_name: Optional[str] = None
    ) -> ActivityLog:
        """تسجيل نشاط"""
        log_entry = ActivityLog(
            chat_id=chat_id,
            action_type=action_type,
            target_user_id=target_user_id,
            target_user_name=target_user_name,
            details=details
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    
    @staticmethod
    def get_chat_statistics(db: Session, chat_id: int, days: int = 7) -> Dict:
        """الحصول على إحصائيات القروب"""
        since = datetime.utcnow() - timedelta(days=days)
        
        total_deleted = db.query(DeletedMessage).filter(
            DeletedMessage.chat_id == chat_id,
            DeletedMessage.deleted_at >= since
        ).count()
        
        top_spammers = db.query(UserStatistics).filter(
            UserStatistics.chat_id == chat_id
        ).order_by(UserStatistics.spam_count.desc()).limit(5).all()
        
        recent_activity = db.query(ActivityLog).filter(
            ActivityLog.chat_id == chat_id,
            ActivityLog.created_at >= since
        ).order_by(ActivityLog.created_at.desc()).limit(10).all()
        
        return {
            "total_deleted_messages": total_deleted,
            "top_spammers": [
                {
                    "user_id": s.user_id,
                    "user_name": s.user_name,
                    "spam_count": s.spam_count,
                    "warning_count": s.warning_count
                }
                for s in top_spammers
            ],
            "recent_activity": [
                {
                    "action_type": a.action_type,
                    "target_user_name": a.target_user_name,
                    "details": a.details,
                    "created_at": a.created_at.isoformat()
                }
                for a in recent_activity
            ],
            "period_days": days
        }
    
    @staticmethod
    def get_user_statistics(db: Session, chat_id: int, user_id: int) -> Optional[UserStatistics]:
        """الحصول على إحصائيات المستخدم"""
        return db.query(UserStatistics).filter(
            UserStatistics.chat_id == chat_id,
            UserStatistics.user_id == user_id
        ).first()
    
    @staticmethod
    def remove_from_whitelist(db: Session, entry_id: int) -> bool:
        """إزالة مدخل من القائمة البيضاء"""
        entry = db.query(WhitelistEntry).filter(WhitelistEntry.id == entry_id).first()
        if entry:
            db.delete(entry)
            db.commit()
            return True
        return False
    
    @staticmethod
    def remove_from_blacklist(db: Session, entry_id: int) -> bool:
        """إزالة مدخل من القائمة السوداء"""
        entry = db.query(BlacklistEntry).filter(BlacklistEntry.id == entry_id).first()
        if entry:
            db.delete(entry)
            db.commit()
            return True
        return False
