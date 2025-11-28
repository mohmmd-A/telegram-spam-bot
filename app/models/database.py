from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spam_bot.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DeletedMessage(Base):
    """نموذج الرسائل المحذوفة"""
    __tablename__ = "deleted_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    message_id = Column(Integer)
    user_id = Column(Integer)
    user_name = Column(String)
    message_text = Column(Text)
    detected_keywords = Column(String)  # JSON format
    confidence_score = Column(Float)
    deletion_reason = Column(String)
    deleted_at = Column(DateTime, default=datetime.utcnow)
    is_restored = Column(Boolean, default=False)


class UserStatistics(Base):
    """نموذج إحصائيات المستخدمين"""
    __tablename__ = "user_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    user_name = Column(String)
    spam_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    is_blocked = Column(Boolean, default=False)
    last_spam_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatSettings(Base):
    """نموذج إعدادات القروب"""
    __tablename__ = "chat_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, unique=True, index=True)
    chat_name = Column(String)
    is_enabled = Column(Boolean, default=True)
    detection_sensitivity = Column(Float, default=0.7)
    auto_delete = Column(Boolean, default=True)
    notify_admins = Column(Boolean, default=True)
    max_warnings = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WhitelistEntry(Base):
    """نموذج القائمة البيضاء"""
    __tablename__ = "whitelist"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    user_id = Column(Integer, nullable=True)
    keyword = Column(String, nullable=True)
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class BlacklistEntry(Base):
    """نموذج القائمة السوداء"""
    __tablename__ = "blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    user_id = Column(Integer, nullable=True)
    keyword = Column(String, nullable=True)
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class ActivityLog(Base):
    """نموذج سجل الأنشطة"""
    __tablename__ = "activity_log"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    action_type = Column(String)  # delete, warn, block, unblock, etc.
    target_user_id = Column(Integer, nullable=True)
    target_user_name = Column(String, nullable=True)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """إنشاء جميع الجداول"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """الحصول على جلسة قاعدة البيانات"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
