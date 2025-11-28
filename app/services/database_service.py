"""
خدمة إدارة قاعدة البيانات - النسخة الكاملة
Database Service - Complete Version
"""

from sqlalchemy.orm import Session
from app.models.init_db import (
    ChatSettings, DeletedMessage, WhitelistUser, BlacklistUser, Keyword, ActivityLog
)
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """خدمة إدارة قاعدة البيانات"""
    
    # ===== إدارة إعدادات القروب =====
    
    @staticmethod
    def get_or_create_chat_settings(db: Session, chat_id: int, chat_name: str = ""):
        """الحصول على أو إنشاء إعدادات القروب"""
        settings = db.query(ChatSettings).filter(ChatSettings.chat_id == chat_id).first()
        
        if not settings:
            settings = ChatSettings(
                chat_id=chat_id,
                chat_name=chat_name,
                is_enabled=True,
                detection_sensitivity=0.7
            )
            db.add(settings)
            db.commit()
            logger.info(f"✅ تم إنشاء إعدادات جديدة للقروب {chat_id}")
        
        return settings
    
    @staticmethod
    def set_chat_enabled(db: Session, chat_id: int, enabled: bool):
        """تفعيل/تعطيل البوت في القروب"""
        settings = DatabaseService.get_or_create_chat_settings(db, chat_id)
        settings.is_enabled = enabled
        db.commit()
        return settings
    
    @staticmethod
    def set_chat_sensitivity(db: Session, chat_id: int, sensitivity: float):
        """تعديل حساسية الكشف"""
        settings = DatabaseService.get_or_create_chat_settings(db, chat_id)
        settings.detection_sensitivity = max(0.1, min(1.0, sensitivity))
        db.commit()
        return settings
    
    # ===== إدارة الرسائل المحذوفة =====
    
    @staticmethod
    def log_deleted_message(
        db: Session,
        chat_id: int,
        message_id: int,
        user_id: int,
        user_name: str,
        message_text: str,
        keywords: list,
        confidence: float
    ):
        """تسجيل رسالة محذوفة"""
        deleted_msg = DeletedMessage(
            chat_id=chat_id,
            message_id=message_id,
            user_id=user_id,
            user_name=user_name,
            message_text=message_text[:500],  # أول 500 حرف فقط
            detected_keywords=json.dumps(keywords),
            confidence_score=confidence
        )
        db.add(deleted_msg)
        db.commit()
        return deleted_msg
    
    @staticmethod
    def get_deleted_messages(db: Session, chat_id: int, days: int = 7):
        """الحصول على الرسائل المحذوفة"""
        since = datetime.utcnow() - timedelta(days=days)
        messages = db.query(DeletedMessage).filter(
            DeletedMessage.chat_id == chat_id,
            DeletedMessage.deleted_at >= since
        ).all()
        return messages
    
    # ===== إدارة القوائم البيضاء والسوداء =====
    
    @staticmethod
    def add_user_to_whitelist(db: Session, chat_id: int, user_id: int, user_name: str = ""):
        """إضافة مستخدم للقائمة البيضاء"""
        # التحقق من عدم وجوده بالفعل
        existing = db.query(WhitelistUser).filter(
            WhitelistUser.chat_id == chat_id,
            WhitelistUser.user_id == user_id
        ).first()
        
        if existing:
            return existing
        
        whitelist = WhitelistUser(
            chat_id=chat_id,
            user_id=user_id,
            user_name=user_name
        )
        db.add(whitelist)
        db.commit()
        return whitelist
    
    @staticmethod
    def remove_user_from_whitelist(db: Session, chat_id: int, user_id: int):
        """إزالة مستخدم من القائمة البيضاء"""
        db.query(WhitelistUser).filter(
            WhitelistUser.chat_id == chat_id,
            WhitelistUser.user_id == user_id
        ).delete()
        db.commit()
    
    @staticmethod
    def is_user_whitelisted(db: Session, chat_id: int, user_id: int) -> bool:
        """التحقق من وجود مستخدم في القائمة البيضاء"""
        result = db.query(WhitelistUser).filter(
            WhitelistUser.chat_id == chat_id,
            WhitelistUser.user_id == user_id
        ).first()
        return result is not None
    
    @staticmethod
    def add_user_to_blacklist(db: Session, chat_id: int, user_id: int, user_name: str = ""):
        """إضافة مستخدم للقائمة السوداء"""
        existing = db.query(BlacklistUser).filter(
            BlacklistUser.chat_id == chat_id,
            BlacklistUser.user_id == user_id
        ).first()
        
        if existing:
            return existing
        
        blacklist = BlacklistUser(
            chat_id=chat_id,
            user_id=user_id,
            user_name=user_name
        )
        db.add(blacklist)
        db.commit()
        return blacklist
    
    @staticmethod
    def remove_user_from_blacklist(db: Session, chat_id: int, user_id: int):
        """إزالة مستخدم من القائمة السوداء"""
        db.query(BlacklistUser).filter(
            BlacklistUser.chat_id == chat_id,
            BlacklistUser.user_id == user_id
        ).delete()
        db.commit()
    
    @staticmethod
    def is_user_blacklisted(db: Session, chat_id: int, user_id: int) -> bool:
        """التحقق من وجود مستخدم في القائمة السوداء"""
        result = db.query(BlacklistUser).filter(
            BlacklistUser.chat_id == chat_id,
            BlacklistUser.user_id == user_id
        ).first()
        return result is not None
    
    # ===== إدارة الكلمات المفتاحية =====
    
    @staticmethod
    def add_keyword(db: Session, chat_id: int, keyword: str, is_custom: bool = True):
        """إضافة كلمة مفتاحية"""
        existing = db.query(Keyword).filter(
            Keyword.chat_id == chat_id,
            Keyword.keyword == keyword.lower()
        ).first()
        
        if existing:
            return existing
        
        kw = Keyword(
            chat_id=chat_id,
            keyword=keyword.lower(),
            is_custom=is_custom
        )
        db.add(kw)
        db.commit()
        return kw
    
    @staticmethod
    def remove_keyword(db: Session, chat_id: int, keyword: str):
        """إزالة كلمة مفتاحية"""
        db.query(Keyword).filter(
            Keyword.chat_id == chat_id,
            Keyword.keyword == keyword.lower()
        ).delete()
        db.commit()
    
    @staticmethod
    def get_keywords(db: Session, chat_id: int) -> list:
        """الحصول على الكلمات المفتاحية"""
        keywords = db.query(Keyword).filter(Keyword.chat_id == chat_id).all()
        return [kw.keyword for kw in keywords]
    
    # ===== سجل النشاطات =====
    
    @staticmethod
    def log_activity(
        db: Session,
        chat_id: int,
        action: str,
        user_id: int = None,
        user_name: str = "",
        details: str = ""
    ):
        """تسجيل نشاط"""
        log = ActivityLog(
            chat_id=chat_id,
            action=action,
            user_id=user_id,
            user_name=user_name,
            details=details
        )
        db.add(log)
        db.commit()
        return log
    
    @staticmethod
    def get_activity_logs(db: Session, chat_id: int, days: int = 7) -> list:
        """الحصول على سجل النشاطات"""
        since = datetime.utcnow() - timedelta(days=days)
        logs = db.query(ActivityLog).filter(
            ActivityLog.chat_id == chat_id,
            ActivityLog.timestamp >= since
        ).order_by(ActivityLog.timestamp.desc()).all()
        
        return [
            {
                'action': log.action,
                'user_name': log.user_name,
                'timestamp': log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'details': log.details
            }
            for log in logs
        ]
    
    # ===== الإحصائيات =====
    
    @staticmethod
    def get_chat_statistics(db: Session, chat_id: int) -> dict:
        """الحصول على إحصائيات القروب"""
        deleted_count = db.query(DeletedMessage).filter(
            DeletedMessage.chat_id == chat_id
        ).count()
        
        whitelist_count = db.query(WhitelistUser).filter(
            WhitelistUser.chat_id == chat_id
        ).count()
        
        blacklist_count = db.query(BlacklistUser).filter(
            BlacklistUser.chat_id == chat_id
        ).count()
        
        keyword_count = db.query(Keyword).filter(
            Keyword.chat_id == chat_id
        ).count()
        
        return {
            'deleted_count': deleted_count,
            'detected_count': deleted_count,
            'deletion_rate': 100.0 if deleted_count > 0 else 0,
            'user_count': db.query(DeletedMessage.user_id).filter(
                DeletedMessage.chat_id == chat_id
            ).distinct().count(),
            'whitelist_count': whitelist_count,
            'blacklist_count': blacklist_count,
            'keyword_count': keyword_count,
            'top_keyword': 'لا توجد',
        }
