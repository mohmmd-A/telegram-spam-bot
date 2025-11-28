"""
محرك الكشف المحسّن والموحد
Optimized and Unified Detection Engine
"""

import re
import logging
from typing import Tuple, List
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class OptimizedDetectionEngine:
    """محرك كشف محسّن مع أداء عالي"""
    
    # الكلمات المزعجة الأساسية
    SPAM_KEYWORDS = {
        # الإجازات الطبية
        'إجازة': 0.9, 'اجازة': 0.9, 'إجاز': 0.85, 'اجاز': 0.85,
        'سكليف': 0.95, 'سكليفات': 0.95, 'تصليف': 0.95, 'تصاليف': 0.95,
        'مرضية': 0.9, 'مرضي': 0.85, 'طبية': 0.8, 'طبي': 0.75,
        'إجازات': 0.9, 'اجازات': 0.9, 'اعذار': 0.9, 'اعتذار': 0.85,
        'غياب': 0.85, 'غيبة': 0.85, 'تضبط': 0.85, 'تصدر': 0.8,
        
        # الشهادات والموثقة
        'موثق': 0.85, 'موثقة': 0.85, 'معتمد': 0.85, 'معتمدة': 0.85,
        'معتم': 0.8, 'موثوق': 0.8, 'رسمي': 0.85, 'رسمية': 0.85,
        'حكومية': 0.8, 'حكومي': 0.8, 'مستشفى': 0.85, 'مستشفيات': 0.85,
        'مستشفي': 0.85, 'تطبيق': 0.75,
        
        # الخدمات والعروض
        'نطلع': 0.9, 'نتقدم': 0.85, 'نستقبل': 0.85, 'نوفر': 0.8,
        'خدمة': 0.7, 'عرض': 0.7, 'فوري': 0.8, 'سريع': 0.75,
        'إنجاز': 0.85, 'انجاز': 0.85, 'تسليم': 0.8,
        'تضبط': 0.85, 'تصدر': 0.8, 'تصدير': 0.8,
        
        # التواصل والأرقام
        'واتس': 0.9, 'واتساب': 0.9, 'تلفون': 0.85, 'رقم': 0.7,
        'اتصل': 0.8, 'تواصل': 0.8, 'للتواصل': 0.85, 'وتساب': 0.9,
        'جوال': 0.75, 'موبايل': 0.75,
    }
    
    # الأحرف البديلة والمشابهة
    CHAR_REPLACEMENTS = {
        'ا': ['ا', 'آ', 'أ', 'ى'],
        'ه': ['ه', 'ة', 'ۀ'],
        'ي': ['ي', 'ى', 'ئ'],
        'س': ['س', 'ص', 'ث', 'ڰ'],
        'ع': ['ع', 'غ'],
        'ح': ['ح', 'خ'],
        'ط': ['ط', 'ض'],
        'ق': ['ق', 'غ'],
        'ن': ['ن', 'م'],
        'ل': ['ل', 'ا'],
        'r': ['r', 'ر'],
        'o': ['o', 'ه', 'ۆ'],
    }
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """تطبيع النص - مع الحفاظ على المسافات"""
        # إزالة الحركات العربية
        text = re.sub(r'[\u064B-\u065F]', '', text)
        
        # إزالة النقاط والشرطات بين الأحرف
        text = re.sub(r'([ا-ي])[\.-_]+([ا-ي])', r'\1\2', text)
        
        # تحويل إلى أحرف صغيرة
        text = text.lower()
        
        # تطبيع المسافات المتعددة
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """استخراج الكلمات من النص - مع الحفاظ على المسافات"""
        # تقسيم النص إلى كلمات بناءً على المسافات
        words = text.split()
        # تصفية الكلمات الفارغة والأرقام فقط
        words = [w for w in words if w and re.search(r'[\u0600-\u06FFa-z]', w)]
        return words
    
    @staticmethod
    def fuzzy_match(word: str, keyword: str, threshold: float = 0.8) -> bool:
        """مطابقة ضبابية للكلمات"""
        ratio = SequenceMatcher(None, word, keyword).ratio()
        return ratio >= threshold
    
    @staticmethod
    def detect_obfuscation(text: str) -> Tuple[float, List[str]]:
        """كشف التمويه في النص"""
        obfuscation_score = 0.0
        obfuscation_types = []
        
        # كشف النقاط بين الأحرف
        if re.search(r'[ا-ي]\.[ا-ي]', text):
            obfuscation_score += 0.2
            obfuscation_types.append('dots')
        
        # كشف المسافات بين الأحرف
        if re.search(r'[ا-ي]\s{2,}[ا-ي]', text):
            obfuscation_score += 0.2
            obfuscation_types.append('spaces')
        
        # كشف الشرطات بين الأحرف
        if re.search(r'[ا-ي]-[ا-ي]', text):
            obfuscation_score += 0.15
            obfuscation_types.append('dashes')
        
        # كشف الأحرف الخاصة
        if re.search(r'[ا-ي][_\-\.][ا-ي]', text):
            obfuscation_score += 0.15
            obfuscation_types.append('special_chars')
        
        # كشف الخليط من اللغات
        has_arabic = bool(re.search(r'[\u0600-\u06FF]', text))
        has_latin = bool(re.search(r'[a-z]', text))
        if has_arabic and has_latin:
            obfuscation_score += 0.1
            obfuscation_types.append('mixed_languages')
        
        return min(obfuscation_score, 1.0), obfuscation_types
    
    @staticmethod
    def detect_phone_numbers(text: str) -> List[str]:
        """كشف أرقام الهاتف"""
        # أرقام سعودية
        saudi_pattern = r'\+?966\d{9}|05\d{8}'
        # أرقام عامة
        general_pattern = r'\+?\d{10,}'
        
        saudi_numbers = re.findall(saudi_pattern, text)
        general_numbers = re.findall(general_pattern, text)
        
        return list(set(saudi_numbers + general_numbers))
    
    @staticmethod
    def detect_spam(
        text: str,
        user_id: int,
        chat_id: int,
        sensitivity: float = 0.7
    ) -> Tuple[bool, float, List[str]]:
        """
        كشف الرسائل المزعجة
        
        العودة:
            (is_spam, confidence_score, detected_keywords)
        """
        try:
            # تطبيع النص
            normalized_text = OptimizedDetectionEngine.normalize_text(text)
            
            # استخراج الكلمات
            words = OptimizedDetectionEngine.extract_keywords(normalized_text)
            
            # كشف التمويه
            obfuscation_score, obfuscation_types = OptimizedDetectionEngine.detect_obfuscation(text)
            
            # كشف أرقام الهاتف
            phone_numbers = OptimizedDetectionEngine.detect_phone_numbers(text)
            
            # البحث عن الكلمات المزعجة
            detected_keywords = []
            total_score = 0.0
            
            for word in words:
                for keyword, keyword_score in OptimizedDetectionEngine.SPAM_KEYWORDS.items():
                    # مطابقة دقيقة
                    if word == keyword:
                        detected_keywords.append(keyword)
                        total_score += keyword_score
                    # مطابقة ضبابية
                    elif OptimizedDetectionEngine.fuzzy_match(word, keyword, 0.75):
                        detected_keywords.append(f"{keyword}*")
                        total_score += keyword_score * 0.9
            
            # إضافة درجة التمويه
            if obfuscation_score > 0:
                total_score += obfuscation_score * 0.5
            
            # إضافة درجة أرقام الهاتف
            if phone_numbers:
                total_score += len(phone_numbers) * 0.3
            
            # حساب درجة الثقة النهائية
            if detected_keywords or phone_numbers:
                confidence = min(total_score / max(len(detected_keywords), 1), 1.0)
            else:
                confidence = 0.0
            
            # تطبيق حساسية الكشف
            threshold = 1.0 - sensitivity
            is_spam = confidence >= threshold
            
            logger.debug(
                f"Detection: text='{text[:50]}...', "
                f"confidence={confidence:.2f}, "
                f"threshold={threshold:.2f}, "
                f"is_spam={is_spam}, "
                f"keywords={detected_keywords}, "
                f"obfuscation={obfuscation_types}"
            )
            
            return is_spam, confidence, detected_keywords
        
        except Exception as e:
            logger.error(f"خطأ في الكشف: {e}")
            return False, 0.0, []


# إنشاء نسخة واحدة من المحرك
detection_engine = OptimizedDetectionEngine()
