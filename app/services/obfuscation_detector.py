"""
كاشف التمويه المتقدم
Advanced Obfuscation Detector
"""

import re
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)


class ObfuscationDetector:
    """كاشف متقدم للرسائل المموهة والمشوهة"""
    
    # خريطة الأحرف البديلة
    CHAR_REPLACEMENTS = {
        # أحرف عربية بديلة
        'ا': ['ا', 'آ', 'أ', 'إ'],
        'ب': ['ب', 'ٮ', 'ٯ'],
        'ت': ['ت', 'ٺ', 'ٻ'],
        'ث': ['ث', 'ٽ'],
        'ج': ['ج', 'ٺ'],
        'ح': ['ح', 'ه'],
        'خ': ['خ'],
        'د': ['د', 'ڈ'],
        'ذ': ['ذ'],
        'ر': ['ر', 'ڈ'],
        'ز': ['ز', 'ڈ'],
        'س': ['س', 'ص', 'ش', 'ڰ', 'ٹ'],
        'ش': ['ش', 'س', 'ص'],
        'ص': ['ص', 'س', 'ش'],
        'ض': ['ض'],
        'ط': ['ط', 'ٹ'],
        'ظ': ['ظ'],
        'ع': ['ع', 'غ'],
        'غ': ['غ', 'ع'],
        'ف': ['ف', 'ڤ'],
        'ق': ['ق', 'ٯ'],
        'ك': ['ك', 'ک', 'ڪ'],
        'ل': ['ل', 'ڵ'],
        'م': ['م', 'ۻ'],
        'ن': ['ن', 'ں'],
        'ه': ['ه', 'ة', 'ۀ'],
        'و': ['و', 'ۆ'],
        'ي': ['ي', 'ی', 'ئ'],
    }
    
    # الأحرف اللاتينية التي تشبه الأحرف العربية
    LOOKALIKE_CHARS = {
        'o': 'ه',
        'O': 'ه',
        '0': 'ه',
        'l': 'ل',
        'I': 'ل',
        '1': 'ل',
        'i': 'ي',
        'e': 'ع',
        'a': 'ا',
        'u': 'و',
    }
    
    def __init__(self):
        """تهيئة الكاشف"""
        self.patterns = {
            'dots': re.compile(r'\.+'),  # النقاط
            'dashes': re.compile(r'-+'),  # الشرطات
            'underscores': re.compile(r'_+'),  # الخطوط السفلية
            'spaces': re.compile(r'\s+'),  # المسافات
            'mixed_scripts': re.compile(r'[\u0600-\u06FF][a-zA-Z0-9]|[a-zA-Z0-9][\u0600-\u06FF]'),  # خليط من العربية واللاتينية
        }
    
    def normalize_advanced(self, text: str) -> str:
        """تطبيع متقدم للنص مع معالجة التمويه"""
        # إزالة النقاط والشرطات والخطوط بين الأحرف
        text = re.sub(r'([a-zA-Z\u0600-\u06FF])[\.\-_]+(?=[a-zA-Z\u0600-\u06FF])', r'\1', text)
        
        # إزالة المسافات بين الأحرف
        text = re.sub(r'([a-zA-Z\u0600-\u06FF])\s+(?=[a-zA-Z\u0600-\u06FF])', r'\1', text)
        
        # استبدال الأحرف اللاتينية المشابهة بالعربية
        for latin, arabic in self.LOOKALIKE_CHARS.items():
            text = text.replace(latin, arabic)
            text = text.replace(latin.upper(), arabic)
        
        # توحيد الأحرف العربية البديلة
        for main_char, variants in self.CHAR_REPLACEMENTS.items():
            for variant in variants:
                if variant != main_char:
                    text = text.replace(variant, main_char)
        
        # إزالة الحركات
        text = re.sub(r'[\u064B-\u0652]', '', text)
        
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text.lower()
    
    def calculate_obfuscation_score(self, text: str) -> float:
        """حساب درجة التمويه (0-1)"""
        if not text:
            return 0.0
        
        score = 0.0
        max_score = 0.0
        
        # 1. النقاط والشرطات والخطوط (0.25)
        if re.search(r'[.\-_]', text):
            dots_count = len(re.findall(r'[.\-_]', text))
            if dots_count > len(text) * 0.1:
                score += 0.25
            else:
                score += 0.1
        max_score += 0.25
        
        # 2. المسافات بين الأحرف (0.25)
        if re.search(r'[a-zA-Z\u0600-\u06FF]\s+[a-zA-Z\u0600-\u06FF]', text):
            spaces_count = len(re.findall(r'\s+', text))
            if spaces_count > 3:
                score += 0.25
            else:
                score += 0.15
        max_score += 0.25
        
        # 3. الخليط من العربية واللاتينية (0.2)
        if re.search(self.patterns['mixed_scripts'], text):
            score += 0.2
        max_score += 0.2
        
        # 4. أحرف خاصة كثيرة (0.15)
        special_chars = len(re.findall(r'[^a-zA-Z0-9\u0600-\u06FF\s]', text))
        if special_chars > len(text) * 0.15:
            score += 0.15
        max_score += 0.15
        
        # 5. أرقام كثيرة (0.15)
        numbers = len(re.findall(r'\d', text))
        if numbers > len(text) * 0.2:
            score += 0.15
        max_score += 0.15
        
        return min(score / max_score if max_score > 0 else 0, 1.0)
    
    def detect_obfuscation_patterns(self, text: str) -> List[str]:
        """كشف أنماط التمويه المحددة"""
        patterns_found = []
        
        # نقاط بين الأحرف
        if re.search(r'[a-zA-Z\u0600-\u06FF]\.[a-zA-Z\u0600-\u06FF]', text):
            patterns_found.append('dots_between_chars')
        
        # مسافات بين الأحرف
        if re.search(r'[a-zA-Z\u0600-\u06FF]\s+[a-zA-Z\u0600-\u06FF]', text):
            patterns_found.append('spaces_between_chars')
        
        # شرطات بين الأحرف
        if re.search(r'[a-zA-Z\u0600-\u06FF]-[a-zA-Z\u0600-\u06FF]', text):
            patterns_found.append('dashes_between_chars')
        
        # خليط عربي-لاتيني
        if re.search(self.patterns['mixed_scripts'], text):
            patterns_found.append('mixed_scripts')
        
        # أحرف لاتينية في نص عربي
        if re.search(r'[a-zA-Z]', text) and re.search(r'[\u0600-\u06FF]', text):
            patterns_found.append('latin_in_arabic')
        
        # أرقام كثيرة
        if len(re.findall(r'\d', text)) > 3:
            patterns_found.append('many_numbers')
        
        return patterns_found
    
    def is_heavily_obfuscated(self, text: str, threshold: float = 0.5) -> bool:
        """التحقق من أن الرسالة مموهة بشكل كبير"""
        score = self.calculate_obfuscation_score(text)
        return score >= threshold
    
    def get_obfuscation_details(self, text: str) -> dict:
        """الحصول على تفاصيل التمويه"""
        return {
            'original_text': text,
            'normalized_text': self.normalize_advanced(text),
            'obfuscation_score': self.calculate_obfuscation_score(text),
            'patterns': self.detect_obfuscation_patterns(text),
            'is_heavily_obfuscated': self.is_heavily_obfuscated(text),
        }


# إنشاء نسخة واحدة من الكاشف
obfuscation_detector = ObfuscationDetector()
