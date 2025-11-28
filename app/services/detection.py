import json
import re
from typing import Dict, List, Tuple
from difflib import SequenceMatcher
import os
from datetime import datetime, timedelta


class SpamDetectionEngine:
    """محرك الكشف الذكي عن الإعلانات المزعجة"""
    
    def __init__(self, keywords_file: str = "keywords.json"):
        self.keywords_file = keywords_file
        self.load_keywords()
        self.message_history = {}  # لتخزين سجل الرسائل
        
    def load_keywords(self):
        """تحميل الكلمات المفتاحية من الملف"""
        try:
            with open(self.keywords_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.medical_keywords = data.get('medical_keywords', [])
                self.suspicious_patterns = data.get('suspicious_patterns', [])
                self.spam_indicators = data.get('spam_indicators', [])
                self.admin_keywords = data.get('admin_keywords', [])
        except FileNotFoundError:
            print(f"تحذير: لم يتم العثور على ملف {self.keywords_file}")
            self.medical_keywords = []
            self.suspicious_patterns = []
            self.spam_indicators = []
            self.admin_keywords = []
    
    def detect_spam(self, message: str, user_id: int, chat_id: int, 
                   sensitivity: float = 0.7) -> Tuple[bool, float, List[str]]:
        """
        كشف ما إذا كانت الرسالة إعلان مزعج
        
        Args:
            message: نص الرسالة
            user_id: معرف المستخدم
            chat_id: معرف القروب
            sensitivity: مستوى الحساسية (0-1)
            
        Returns:
            (is_spam, confidence_score, detected_keywords)
        """
        if not message:
            return False, 0.0, []
        
        message_lower = message.lower()
        detected_keywords = []
        confidence_score = 0.0
        
        # 1. فحص الكلمات المفتاحية الطبية
        medical_score, medical_keywords = self._check_medical_keywords(message_lower)
        detected_keywords.extend(medical_keywords)
        confidence_score += medical_score * 0.3
        
        # 2. فحص الأنماط المريبة (أرقام هواتف، روابط)
        suspicious_score, suspicious_items = self._check_suspicious_patterns(message)
        detected_keywords.extend(suspicious_items)
        confidence_score += suspicious_score * 0.35
        
        # 3. فحص مؤشرات الإعلانات
        spam_indicator_score, indicators = self._check_spam_indicators(message_lower)
        detected_keywords.extend(indicators)
        confidence_score += spam_indicator_score * 0.2
        
        # 4. فحص الرسائل المكررة
        duplicate_score = self._check_duplicate_messages(user_id, chat_id, message)
        confidence_score += duplicate_score * 0.15
        
        # تطبيع النتيجة
        confidence_score = min(confidence_score, 1.0)
        
        # إزالة التكرارات
        detected_keywords = list(set(detected_keywords))
        
        # تحديد ما إذا كانت إعلان بناءً على مستوى الحساسية
        is_spam = confidence_score >= sensitivity
        
        return is_spam, confidence_score, detected_keywords
    
    def _check_medical_keywords(self, message: str) -> Tuple[float, List[str]]:
        """فحص الكلمات المفتاحية الطبية"""
        score = 0.0
        found_keywords = []
        
        for keyword in self.medical_keywords:
            if keyword in message:
                score += 0.2
                found_keywords.append(keyword)
        
        # تطبيع النتيجة
        if found_keywords:
            score = min(score, 1.0)
        
        return score, found_keywords
    
    def _check_suspicious_patterns(self, message: str) -> Tuple[float, List[str]]:
        """فحص الأنماط المريبة مثل أرقام الهواتف والروابط"""
        score = 0.0
        found_patterns = []
        
        for pattern in self.suspicious_patterns:
            try:
                matches = re.findall(pattern, message)
                if matches:
                    score += 0.3 * len(matches)
                    found_patterns.extend(matches)
            except re.error:
                continue
        
        # تطبيع النتيجة
        if found_patterns:
            score = min(score, 1.0)
        
        return score, found_patterns
    
    def _check_spam_indicators(self, message: str) -> Tuple[float, List[str]]:
        """فحص مؤشرات الإعلانات"""
        score = 0.0
        found_indicators = []
        
        for indicator in self.spam_indicators:
            if indicator in message:
                score += 0.15
                found_indicators.append(indicator)
        
        # تطبيع النتيجة
        if found_indicators:
            score = min(score, 1.0)
        
        return score, found_indicators
    
    def _check_duplicate_messages(self, user_id: int, chat_id: int, message: str) -> float:
        """فحص الرسائل المكررة"""
        key = f"{chat_id}_{user_id}"
        current_time = datetime.now()
        
        if key not in self.message_history:
            self.message_history[key] = []
        
        # تنظيف الرسائل القديمة (أكثر من 5 دقائق)
        self.message_history[key] = [
            (msg, timestamp) for msg, timestamp in self.message_history[key]
            if (current_time - timestamp).seconds < 300
        ]
        
        # البحث عن رسائل متشابهة
        similarity_score = 0.0
        for prev_message, _ in self.message_history[key]:
            similarity = SequenceMatcher(None, message, prev_message).ratio()
            if similarity > 0.8:  # تشابه أكثر من 80%
                similarity_score = 0.4
                break
        
        # إضافة الرسالة الحالية للسجل
        self.message_history[key].append((message, current_time))
        
        return similarity_score
    
    def add_custom_keyword(self, keyword: str, category: str = "medical"):
        """إضافة كلمة مفتاحية مخصصة"""
        if category == "medical":
            if keyword not in self.medical_keywords:
                self.medical_keywords.append(keyword)
        elif category == "spam_indicator":
            if keyword not in self.spam_indicators:
                self.spam_indicators.append(keyword)
        
        self._save_keywords()
    
    def remove_keyword(self, keyword: str):
        """إزالة كلمة مفتاحية"""
        self.medical_keywords = [k for k in self.medical_keywords if k != keyword]
        self.spam_indicators = [k for k in self.spam_indicators if k != keyword]
        self._save_keywords()
    
    def _save_keywords(self):
        """حفظ الكلمات المفتاحية في الملف"""
        try:
            data = {
                'medical_keywords': self.medical_keywords,
                'suspicious_patterns': self.suspicious_patterns,
                'spam_indicators': self.spam_indicators,
                'admin_keywords': self.admin_keywords
            }
            with open(self.keywords_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطأ في حفظ الكلمات المفتاحية: {e}")
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات الكشف"""
        return {
            "total_medical_keywords": len(self.medical_keywords),
            "total_suspicious_patterns": len(self.suspicious_patterns),
            "total_spam_indicators": len(self.spam_indicators),
            "message_history_size": len(self.message_history)
        }


# إنشاء مثيل عام من محرك الكشف
detection_engine = SpamDetectionEngine()
