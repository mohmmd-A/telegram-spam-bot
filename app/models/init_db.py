"""
تهيئة قاعدة البيانات وإنشاء الجداول
Database Initialization Module
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# إنشاء Base للنماذج
Base = declarative_base()

# مسار قاعدة البيانات
DB_PATH = os.path.join(os.path.dirname(__file__), '../../data')
os.makedirs(DB_PATH, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DB_PATH, 'bot.db')}"

# إنشاء محرك قاعدة البيانات
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ChatSettings(Base):
    """إعدادات القروب"""
    __tablename__ = "chat_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, unique=True, index=True)
    chat_name = Column(String(255))
    is_enabled = Column(Boolean, default=True)
    detection_sensitivity = Column(Float, default=0.7)
    auto_delete = Column(Boolean, default=True)
    notify_admins = Column(Boolean, default=True)
    max_warnings = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DeletedMessage(Base):
    """الرسائل المحذوفة"""
    __tablename__ = "deleted_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    message_id = Column(Integer)
    user_id = Column(Integer)
    user_name = Column(String(255))
    message_text = Column(Text)
    detected_keywords = Column(Text)  # JSON
    confidence_score = Column(Float)
    deleted_at = Column(DateTime, default=datetime.utcnow)


class WhitelistUser(Base):
    """المستخدمون في القائمة البيضاء"""
    __tablename__ = "whitelist_users"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    user_id = Column(Integer)
    user_name = Column(String(255))
    added_at = Column(DateTime, default=datetime.utcnow)


class BlacklistUser(Base):
    """المستخدمون في القائمة السوداء"""
    __tablename__ = "blacklist_users"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    user_id = Column(Integer)
    user_name = Column(String(255))
    added_at = Column(DateTime, default=datetime.utcnow)


class Keyword(Base):
    """الكلمات المفتاحية"""
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    keyword = Column(String(255))
    is_custom = Column(Boolean, default=False)
    added_at = Column(DateTime, default=datetime.utcnow)


class ActivityLog(Base):
    """سجل النشاطات"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    action = Column(String(255))
    user_id = Column(Integer)
    user_name = Column(String(255))
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


def init_db():
    """إنشاء جميع الجداول"""
    try:
        logger.info("جاري إنشاء جداول قاعدة البيانات...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ تم إنشاء جميع الجداول بنجاح")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء الجداول: {e}")
        return False


def get_db():
    """الحصول على جلسة قاعدة البيانات"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
