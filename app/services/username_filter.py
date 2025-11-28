"""
خدمة فحص أسماء المستخدمين المشبوهة
Username Filter Service
"""

import logging
from typing import Tuple, List
from app.models.init_db import SessionLocal, SuspiciousUsername

logger = logging.getLogger(__name__)


class UsernameFilter:
    """فلتر أسماء المستخدمين"""
    
    # الكلمات المشبوهة في أسماء المستخدمين
    SUSPICIOUS_KEYWORDS = {
        'سكليف': 0.9, 'اجازة': 0.9, 'موثق': 0.8, 'معتمد': 0.8,
        'فوري': 0.7, 'سريع': 0.7, 'خدمة': 0.6, 'عرض': 0.6,
    }
    
    @staticmethod
    def check_username_for_spam(username: str) -> Tuple[bool, List[str], float]:
        """فحص اسم المستخدم للكلمات المشبوهة"""
        username_lower = username.lower()
        detected_keywords = []
        confidence = 0.0
        
        for keyword in UsernameFilter.SUSPICIOUS_KEYWORDS.keys():
            if keyword in username_lower:
                detected_keywords.append(keyword)
                confidence += UsernameFilter.SUSPICIOUS_KEYWORDS[keyword]
        
        is_suspicious = len(detected_keywords) > 0
        if detected_keywords:
            confidence = min(confidence / len(detected_keywords), 1.0)
        
        return is_suspicious, detected_keywords, confidence
    
    @staticmethod
    def get_username_risk_score(username: str) -> Tuple[float, str]:
        """حساب درجة المخاطرة لاسم المستخدم"""
        is_suspicious, keywords, confidence = UsernameFilter.check_username_for_spam(username)
        
        if confidence >= 0.8:
            risk_level = "عالي جداً"
        elif confidence >= 0.6:
            risk_level = "عالي"
        elif confidence >= 0.4:
            risk_level = "متوسط"
        else:
            risk_level = "منخفض"
        
        return confidence, risk_level
    
    @staticmethod
    def save_suspicious_username(db, chat_id: int, user_id: int, username: str, risk_score: float, reason: str):
        """حفظ اسم مستخدم مشبوه في قاعدة البيانات"""
        try:
            suspicious = SuspiciousUsername(
                chat_id=chat_id,
                user_id=user_id,
                username=username,
                risk_score=risk_score,
                reason=reason
            )
            db.add(suspicious)
            db.commit()
            logger.info(f"تم حفظ اسم مستخدم مشبوه: {username}")
        except Exception as e:
            logger.error(f"خطأ في حفظ اسم المستخدم المشبوه: {e}")
            db.rollback()


# إنشاء نسخة واحدة من الفلتر
username_filter = UsernameFilter()
