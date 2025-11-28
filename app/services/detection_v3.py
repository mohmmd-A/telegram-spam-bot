"""
محرك الكشف المحسّن مع التعلم الذاتي
Enhanced Detection Engine with Self-Learning
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Tuple, List, Dict
from difflib import SequenceMatcher
from app.models.init_db import SessionLocal, Keyword, DeletedMessage

logger = logging.getLogger(__name__)


class EnhancedDetectionEngine:
    """محرك كشف محسّن مع قدرات التعلم الذاتي"""
    
    def __init__(self):
        """تهيئة المحرك"""
        self.base_keywords = {
            # الكلمات الطبية
            'إجازة مرضية': 0.95,
            'مرضي': 0.9,
            'طبي': 0.85,
            'عيادة': 0.8,
            'مستشفى': 0.85,
            'دكتور': 0.7,
            'طبيب': 0.7,
            'علاج': 0.7,
            'دواء': 0.65,
            'تقرير طبي': 0.95,
            'شهادة طبية': 0.95,
            'فحص طبي': 0.9,
            'موعد طبي': 0.85,
            'حجز موعد': 0.75,
            'استشارة طبية': 0.85,
            
            # الكلمات المتعلقة بالغياب
            'غياب': 0.8,
            'عطلة': 0.7,
            'إجازة': 0.75,
            'عدم الحضور': 0.85,
            'عذر': 0.7,
            'تغيب': 0.8,
            
            # كلمات مشبوهة
            'موثوق': 0.8,
            'معتمد': 0.75,
            'حكومي': 0.7,
            'رسمي': 0.7,
            'شهادة': 0.8,
            'تقرير': 0.75,
        }
        
        # أنماط regex للكشف المتقدم
        self.patterns = {
            'phone': re.compile(r'(\+\d{1,3}[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{4}'),
            'email': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            'url': re.compile(r'https?://[^\s]+|www\.[^\s]+'),
            'numbers': re.compile(r'\d{7,}'),  # أرقام طويلة
            'special_chars': re.compile(r'[^\w\s\u0600-\u06FF]'),
        }
        
        # قاموس التحسن الذاتي
        self.learning_data = {
            'detected_keywords': {},
            'false_positives': [],
            'false_negatives': [],
            'improvement_history': []
        }
        
        self.load_learning_data()
    
    def load_learning_data(self):
        """تحميل بيانات التعلم من الملف"""
        try:
            import os
            learning_file = os.path.join(
                os.path.dirname(__file__),
                '../../data/learning_data.json'
            )
            if os.path.exists(learning_file):
                with open(learning_file, 'r', encoding='utf-8') as f:
                    self.learning_data = json.load(f)
                logger.info("✅ تم تحميل بيانات التعلم الذاتي")
        except Exception as e:
            logger.warning(f"تحذير: لم يتم تحميل بيانات التعلم: {e}")
    
    def save_learning_data(self):
        """حفظ بيانات التعلم إلى الملف"""
        try:
            import os
            data_dir = os.path.join(os.path.dirname(__file__), '../../data')
            os.makedirs(data_dir, exist_ok=True)
            
            learning_file = os.path.join(data_dir, 'learning_data.json')
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
            logger.info("✅ تم حفظ بيانات التعلم الذاتي")
        except Exception as e:
            logger.warning(f"تحذير: لم يتم حفظ بيانات التعلم: {e}")
    
    def normalize_text(self, text: str) -> str:
        """تطبيع النص بإزالة الحركات والمسافات الزائدة"""
        # إزالة الحركات العربية
        text = re.sub(r'[\u064B-\u0652]', '', text)
        
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text)
        
        # تحويل إلى أحرف صغيرة
        text = text.lower().strip()
        
        return text
    
    def extract_keywords(self, text: str) -> List[Tuple[str, float]]:
        """استخراج الكلمات المفتاحية من النص"""
        normalized = self.normalize_text(text)
        found_keywords = []
        
        # البحث عن الكلمات الأساسية
        for keyword, score in self.base_keywords.items():
            if keyword in normalized:
                found_keywords.append((keyword, score))
                # تسجيل الكلمة المكتشفة
                if keyword not in self.learning_data['detected_keywords']:
                    self.learning_data['detected_keywords'][keyword] = 0
                self.learning_data['detected_keywords'][keyword] += 1
        
        # البحث عن كلمات متشابهة (fuzzy matching)
        words = normalized.split()
        for word in words:
            if len(word) > 3:
                for keyword in self.base_keywords.keys():
                    similarity = SequenceMatcher(None, word, keyword).ratio()
                    if 0.75 < similarity < 1.0:  # كلمات متشابهة لكن ليست متطابقة
                        score = self.base_keywords[keyword] * similarity * 0.8
                        found_keywords.append((keyword, score))
        
        return found_keywords
    
    def calculate_obfuscation_score(self, text: str) -> float:
        """حساب درجة التمويه (كم مرة حاول المرسل إخفاء الرسالة)"""
        score = 0.0
        
        # وجود مسافات بين الأحرف
        if re.search(r'\w\s+\w', text):
            score += 0.15
        
        # وجود أحرف خاصة كثيرة
        special_count = len(re.findall(self.patterns['special_chars'], text))
        if special_count > len(text) * 0.2:
            score += 0.2
        
        # وجود أرقام
        if re.search(self.patterns['numbers'], text):
            score += 0.15
        
        # وجود روابط أو بريد إلكتروني
        if re.search(self.patterns['url'], text) or re.search(self.patterns['email'], text):
            score += 0.25
        
        # وجود أرقام هواتف
        if re.search(self.patterns['phone'], text):
            score += 0.25
        
        # نسبة الأحرف الكبيرة
        if text and len(text) > 0:
            upper_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if upper_ratio > 0.5:
                score += 0.1
        
        return min(score, 1.0)
    
    def detect_spam(
        self,
        text: str,
        user_id: int = None,
        chat_id: int = None,
        sensitivity: float = 0.7
    ) -> Tuple[bool, float, List[str]]:
        """
        كشف الرسائل المزعجة مع التعلم الذاتي
        
        Returns:
            (is_spam, confidence, keywords)
        """
        if not text or len(text.strip()) == 0:
            return False, 0.0, []
        
        # استخراج الكلمات المفتاحية
        keywords = self.extract_keywords(text)
        
        if not keywords:
            return False, 0.0, []
        
        # حساب درجة الثقة من الكلمات المفتاحية
        keyword_score = max([score for _, score in keywords]) if keywords else 0.0
        
        # حساب درجة التمويه
        obfuscation_score = self.calculate_obfuscation_score(text)
        
        # الدرجة النهائية = متوسط درجة الكلمات + درجة التمويه
        final_score = (keyword_score * 0.7) + (obfuscation_score * 0.3)
        
        # تطبيق حساسية المستخدم
        threshold = 1.0 - sensitivity
        is_spam = final_score >= threshold
        
        # استخراج أسماء الكلمات فقط
        keyword_names = [kw for kw, _ in keywords]
        
        # تسجيل النتيجة للتعلم الذاتي
        if is_spam:
            self.learning_data['improvement_history'].append({
                'timestamp': datetime.now().isoformat(),
                'text': text[:50],
                'score': final_score,
                'keywords': keyword_names
            })
        
        return is_spam, final_score, keyword_names
    
    def add_false_positive(self, text: str, keywords: List[str]):
        """تسجيل إيجابي خاطئ (رسالة تم حذفها بالخطأ)"""
        self.learning_data['false_positives'].append({
            'timestamp': datetime.now().isoformat(),
            'text': text[:100],
            'keywords': keywords
        })
        
        # تقليل درجة الكلمات الخاطئة
        for keyword in keywords:
            if keyword in self.base_keywords:
                self.base_keywords[keyword] *= 0.95
        
        logger.info(f"📝 تم تسجيل إيجابي خاطئ: {keywords}")
        self.save_learning_data()
    
    def add_false_negative(self, text: str, keywords: List[str]):
        """تسجيل سلبي خاطئ (رسالة مزعجة لم يتم اكتشافها)"""
        self.learning_data['false_negatives'].append({
            'timestamp': datetime.now().isoformat(),
            'text': text[:100],
            'keywords': keywords
        })
        
        # زيادة درجة الكلمات الصحيحة
        for keyword in keywords:
            if keyword in self.base_keywords:
                self.base_keywords[keyword] = min(self.base_keywords[keyword] * 1.05, 1.0)
        
        logger.info(f"📝 تم تسجيل سلبي خاطئ: {keywords}")
        self.save_learning_data()
    
    def get_learning_stats(self) -> Dict:
        """الحصول على إحصائيات التعلم الذاتي"""
        return {
            'total_detections': len(self.learning_data['improvement_history']),
            'false_positives': len(self.learning_data['false_positives']),
            'false_negatives': len(self.learning_data['false_negatives']),
            'top_keywords': sorted(
                self.learning_data['detected_keywords'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'accuracy': self._calculate_accuracy()
        }
    
    def _calculate_accuracy(self) -> float:
        """حساب دقة الكشف"""
        total = (
            len(self.learning_data['improvement_history']) +
            len(self.learning_data['false_positives']) +
            len(self.learning_data['false_negatives'])
        )
        
        if total == 0:
            return 0.0
        
        correct = len(self.learning_data['improvement_history'])
        return (correct / total) * 100 if total > 0 else 0.0


# إنشاء نسخة واحدة من المحرك
detection_engine = EnhancedDetectionEngine()
