"""
نظام فحص أسماء المستخدمين المشبوهة
Username-Based Filtering System
"""

import re
import logging
from typing import Tuple
from sqlalchemy.orm import Session

from app.models.init_db import SuspiciousUsername
from app.services.obfuscation_detector import obfuscation_detector

logger = logging.getLogger(__name__)


class UsernameFilter:
    """فحص أسماء المستخدمين للكلمات المزعجة"""
    
    def __init__(self):
        """تهيئة الفلتر"""
        # الكلمات المزعجة الشائعة في أسماء المستخدمين
        self.spam_keywords = [
            'طبي', 'طب', 'مستشفى', 'مشفى', 'دكتور', 'دكتوره', 'طبيب', 'طبيبة',
            'اجازة', 'إجازة', 'مرض', 'مريض', 'مريضة', 'علاج', 'معالج',
            'استشارة', 'استشاره', 'تقرير', 'تقريرطبي', 'تقرير_طبي',
            'موثق', 'معتمد', 'معتمده', 'رسمي', 'رسمية', 'حكومي', 'حكومية',
            'غياب', 'حضور', 'موظف', 'موظفة', 'موارد', 'بشرية',
            'وسيط', 'وسيطة', 'وسيط_طبي', 'وسيط_اجازة',
            'تصديق', 'توثيق', 'توثيق_طبي', 'توثيق_اجازة',
            'خدمة', 'خدمات', 'خدمة_طبية', 'خدمات_طبية',
            'سريع', 'سريعة', 'فوري', 'فورية', 'بسرعة',
            'ضمان', 'مضمون', 'مضمونة', 'مضمون_100',
            'رخيص', 'رخيصة', 'بسعر', 'بسعر_منخفض',
            'اتصل', 'واتس', 'واتساب', 'تليجرام', 'تواصل',
            'للبيع', 'للايجار', 'للشراء', 'للتأجير',
            'عرض', 'عروض', 'خصم', 'تخفيف', 'تخفيض',
            'ربح', 'أرباح', 'دخل', 'كسب', 'كسب_سهل',
            'استثمار', 'استثمارات', 'فرصة', 'فرص',
            'عمل', 'وظيفة', 'وظائف', 'توظيف',
            'تجارة', 'تجار', 'بيع', 'بائع', 'بائعة',
            'شراء', 'مشتري', 'مشترية', 'عميل', 'عميلة',
            'إعلان', 'إعلانات', 'اعلان', 'اعلانات',
            'روابط', 'رابط', 'لينك', 'لينكات',
            'قروض', 'قرض', 'تمويل', 'تمويلات',
            'بطاقة', 'بطاقات', 'حساب', 'حسابات',
            'تحويل', 'تحويلات', 'أموال', 'مال',
            'سحب', 'إيداع', 'رصيد', 'رصيدك',
            'مكافأة', 'مكافآت', 'جائزة', 'جوائز',
            'يانصيب', 'اليانصيب', 'حظ', 'الحظ',
            'فيس', 'فيسبوك', 'انستا', 'انستجرام',
            'تويتر', 'سناب', 'سناب_شات', 'تيك_توك',
            'يوتيوب', 'يوتيوبر', 'مؤثر', 'مؤثرة',
            'متابع', 'متابعة', 'متابعين', 'متابعات',
            'لايك', 'لايكات', 'تعليق', 'تعليقات',
            'مشاهدات', 'مشاهدة', 'فيديو', 'فيديوهات',
            'صورة', 'صور', 'صوت', 'أصوات',
            'موسيقى', 'موسيقي', 'أغنية', 'أغاني',
            'فيلم', 'أفلام', 'مسلسل', 'مسلسلات',
            'لعبة', 'لعبات', 'ألعاب', 'لاعب', 'لاعبة',
            'رياضة', 'رياضي', 'رياضية', 'كرة', 'كرات',
            'فريق', 'فرق', 'نادي', 'أندية',
            'مباراة',             'مباريات', 'دوري', 'دوريات',
            'حكم', 'حكام', 'تحكيم', 'محكم',
            'فوز', 'خسارة', 'تعادل', 'نتيجة',
            'هدف', 'أهداف', 'ركلة', 'ركلات',
            'بطاقة_صفراء', 'بطاقة_حمراء', 'إقصاء', 'إيقاف',
        ]
        
        # تحويل إلى مجموعة للبحث السريع
        self.spam_keywords_set = set(self.spam_keywords)
    
    def normalize_username(self, username: str) -> str:
        """تطبيع اسم المستخدم"""
        if not username:
            return ""
        
        # تطبيع متقدم باستخدام كاشف التمويه
        normalized = obfuscation_detector.normalize_advanced(username)
        
        # إزالة الأرقام والرموز
        normalized = re.sub(r'[0-9_\-.]', '', normalized)
        
        return normalized.lower()
    
    def extract_keywords_from_username(self, username: str) -> list:
        """استخراج الكلمات من اسم المستخدم"""
        normalized = self.normalize_username(username)
        
        # تقسيم إلى كلمات
        words = re.findall(r'[\u0600-\u06FFa-z]+', normalized)
        
        return words
    
    def check_username_for_spam(self, username: str) -> Tuple[bool, list, float]:
        """
        فحص اسم المستخدم للكلمات المزعجة
        
        العودة:
            (is_spam, found_keywords, confidence_score)
        """
        if not username:
            return False, [], 0.0
        
        keywords = self.extract_keywords_from_username(username)
        found_keywords = []
        confidence_score = 0.0
        
        for keyword in keywords:
            if keyword in self.spam_keywords_set:
                found_keywords.append(keyword)
                confidence_score += 0.3
        
        # حساب درجة الثقة النهائية
        if found_keywords:
            confidence_score = min(confidence_score / len(keywords) if keywords else 0, 1.0)
            is_spam = confidence_score > 0.3
        else:
            is_spam = False
            confidence_score = 0.0
        
        return is_spam, found_keywords, confidence_score
    
    def check_username_obfuscation(self, username: str) -> Tuple[bool, float]:
        """فحص اسم المستخدم للتمويه"""
        obfuscation_score = obfuscation_detector.calculate_obfuscation_score(username)
        is_obfuscated = obfuscation_detector.is_heavily_obfuscated(username, threshold=0.4)
        
        return is_obfuscated, obfuscation_score
    
    def get_username_risk_score(self, username: str) -> Tuple[float, str]:
        """حساب درجة الخطر الكلية لاسم المستخدم"""
        if not username:
            return 0.0, "آمن"
        
        # فحص الكلمات المزعجة
        is_spam, keywords, spam_score = self.check_username_for_spam(username)
        
        # فحص التمويه
        is_obfuscated, obfuscation_score = self.check_username_obfuscation(username)
        
        # حساب الدرجة النهائية
        total_score = (spam_score * 0.6) + (obfuscation_score * 0.4)
        
        # تحديد مستوى الخطر
        if total_score >= 0.8:
            risk_level = "خطر جداً"
        elif total_score >= 0.6:
            risk_level = "خطر"
        elif total_score >= 0.4:
            risk_level = "مشبوه"
        elif total_score >= 0.2:
            risk_level = "محتمل"
        else:
            risk_level = "آمن"
        
        return total_score, risk_level
    
    def should_limit_user(self, username: str, threshold: float = 0.6) -> bool:
        """التحقق من أن المستخدم يجب تحديده"""
        risk_score, _ = self.get_username_risk_score(username)
        return risk_score >= threshold
    
    def save_suspicious_username(self, db: Session, chat_id: int, user_id: int, username: str, risk_score: float, reason: str):
        """حفظ اسم مستخدم مشبوه"""
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
            logger.info(f"تم حفظ اسم مستخدم مشبوه: {username} (درجة الخطر: {risk_score})")
        except Exception as e:
            logger.error(f"خطأ في حفظ اسم المستخدم المشبوه: {e}")
            db.rollback()


# إنشاء نسخة واحدة من الفلتر
username_filter = UsernameFilter()
