"""
كاشف التمويه في الرسائل
Obfuscation Detector Service
"""

import re
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)


class ObfuscationDetector:
    """كاشف التمويه والرسائل المخفية"""
    
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
    def is_heavily_obfuscated(text: str) -> bool:
        """التحقق من أن النص مخفي بشكل كبير"""
        score, types = ObfuscationDetector.detect_obfuscation(text)
        return score >= 0.5


# إنشاء نسخة واحدة من الكاشف
obfuscation_detector = ObfuscationDetector()
