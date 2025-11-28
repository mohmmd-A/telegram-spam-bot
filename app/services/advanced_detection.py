"""
نظام الكشف المتقدم للنصوص المموهة والمشوهة
Advanced Detection System for Obfuscated and Disguised Text
"""

import re
import unicodedata
from typing import Tuple, List
from difflib import SequenceMatcher


class TextNormalizer:
    """معالج تطبيع النصوص المموهة"""
    
    # أحرف عربية بديلة وتشابهات
    ARABIC_DIACRITICS = [
        '\u064B',  # FATHATAN
        '\u064C',  # DAMMATAN
        '\u064D',  # KASRATAN
        '\u064E',  # FATHA
        '\u064F',  # DAMMA
        '\u0650',  # KASRA
        '\u0651',  # SHADDA
        '\u0652',  # SUKUN
        '\u0653',  # MADDAH ABOVE
        '\u0654',  # HAMZA ABOVE
        '\u0655',  # HAMZA BELOW
        '\u0656',  # SUBSCRIPT ALEF
        '\u0657',  # INVERTED DAMMA
        '\u0658',  # MARK NOON GHUNNA
        '\u0670',  # SUPERSCRIPT ALEF
    ]
    
    # أحرف عربية متشابهة
    SIMILAR_CHARS = {
        'ا': ['آ', 'أ', 'إ', 'ء'],  # ALEF variations
        'ه': ['ة'],  # HEH variations
        'ي': ['ى'],  # YEH variations
        'ك': ['گ'],  # KAF variations
        'ل': ['لا'],  # LAM variations
    }
    
    @staticmethod
    def remove_diacritics(text: str) -> str:
        """إزالة الحركات العربية"""
        for diacritic in TextNormalizer.ARABIC_DIACRITICS:
            text = text.replace(diacritic, '')
        return text
    
    @staticmethod
    def remove_extra_spaces(text: str) -> str:
        """إزالة المسافات الزائدة والفواصل"""
        # إزالة المسافات بين الأحرف
        text = re.sub(r'\s+', ' ', text)
        # إزالة المسافات حول الأحرف
        text = re.sub(r'(?<=\w)\s+(?=\w)', '', text)
        return text.strip()
    
    @staticmethod
    def remove_special_chars(text: str) -> str:
        """إزالة الأحرف الخاصة والخطوط"""
        # إزالة الخطوط والفواصل
        text = re.sub(r'[_\-\-\—\–\|\/\\]', '', text)
        # إزالة الرموز الخاصة
        text = re.sub(r'[^\u0600-\u06FF\w\s]', '', text)
        return text
    
    @staticmethod
    def normalize_similar_chars(text: str) -> str:
        """تطبيع الأحرف المتشابهة"""
        for original, variations in TextNormalizer.SIMILAR_CHARS.items():
            for variation in variations:
                text = text.replace(variation, original)
        return text
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """تطبيع النص بشكل شامل"""
        # إزالة الحركات
        text = TextNormalizer.remove_diacritics(text)
        
        # إزالة الأحرف الخاصة
        text = TextNormalizer.remove_special_chars(text)
        
        # تطبيع الأحرف المتشابهة
        text = TextNormalizer.normalize_similar_chars(text)
        
        # إزالة المسافات الزائدة
        text = TextNormalizer.remove_extra_spaces(text)
        
        # تحويل إلى أحرف صغيرة
        text = text.lower()
        
        return text


class AdvancedSpamDetector:
    """كاشف الإعلانات المتقدم للنصوص المموهة"""
    
    def __init__(self):
        self.text_normalizer = TextNormalizer()
    
    def detect_obfuscated_spam(self, message: str, keywords: List[str]) -> Tuple[bool, float, str]:
        """
        كشف الإعلانات المموهة
        
        Args:
            message: الرسالة الأصلية
            keywords: قائمة الكلمات المفتاحية
            
        Returns:
            (is_spam, confidence_score, normalized_message)
        """
        # تطبيع الرسالة
        normalized = self.text_normalizer.normalize_text(message)
        
        # البحث عن الكلمات المفتاحية في النص المطبّع
        found_keywords = []
        confidence = 0.0
        
        for keyword in keywords:
            normalized_keyword = self.text_normalizer.normalize_text(keyword)
            
            # البحث المباشر
            if normalized_keyword in normalized:
                found_keywords.append(keyword)
                confidence += 0.25
            
            # البحث الضبابي (Fuzzy matching)
            else:
                similarity = self._fuzzy_match(normalized_keyword, normalized)
                if similarity > 0.75:  # تشابه أكثر من 75%
                    found_keywords.append(f"{keyword} (تشابه: {similarity:.0%})")
                    confidence += 0.2 * similarity
        
        # تطبيع النتيجة
        confidence = min(confidence, 1.0)
        is_spam = len(found_keywords) > 0 and confidence > 0.2
        
        return is_spam, confidence, normalized
    
    def _fuzzy_match(self, keyword: str, text: str) -> float:
        """
        البحث الضبابي عن الكلمة المفتاحية
        """
        words = text.split()
        max_similarity = 0.0
        
        for word in words:
            similarity = SequenceMatcher(None, keyword, word).ratio()
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def detect_character_distribution(self, message: str) -> float:
        """
        كشف توزيع الأحرف غير الطبيعي (مؤشر على التمويه)
        """
        # حساب نسبة المسافات والأحرف الخاصة
        total_chars = len(message)
        if total_chars == 0:
            return 0.0
        
        spaces = message.count(' ')
        special_chars = len(re.findall(r'[_\-\—\–\|\/\\]', message))
        diacritics = len(re.findall(r'[\u064B-\u0670]', message))
        
        # إذا كانت نسبة المسافات والأحرف الخاصة عالية = احتمال تمويه
        obfuscation_ratio = (spaces + special_chars + diacritics) / total_chars
        
        return min(obfuscation_ratio, 1.0)
    
    def get_obfuscation_indicators(self, message: str) -> dict:
        """الحصول على مؤشرات التمويه"""
        return {
            'has_extra_spaces': bool(re.search(r'\s{2,}', message)),
            'has_special_chars': bool(re.search(r'[_\-\—\–\|\/\\]', message)),
            'has_diacritics': bool(re.search(r'[\u064B-\u0670]', message)),
            'obfuscation_score': self.detect_character_distribution(message),
        }


# إنشاء مثيل عام
advanced_detector = AdvancedSpamDetector()
