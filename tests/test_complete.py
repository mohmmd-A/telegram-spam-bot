"""
اختبارات شاملة للبوت
Comprehensive Bot Tests
"""

import unittest
from app.services.detection import detection_engine
from app.services.database_service import DatabaseService
from app.models.init_db import SessionLocal, ChatSettings, DeletedMessage


class TestDetectionEngine(unittest.TestCase):
    """اختبارات محرك الكشف"""
    
    def test_normalize_text(self):
        """اختبار تطبيع النص"""
        text = "  إ جـــا زة  م ـــر ض ي ة  "
        normalized = detection_engine.normalize_text(text)
        self.assertEqual(normalized, "إجازة مرضية")
    
    def test_detect_spam_keywords(self):
        """اختبار كشف الكلمات المزعجة"""
        text = "تطلع إجازة طبية موثقة +966541904263"
        is_spam, confidence, keywords = detection_engine.detect_spam(text, 1, 1, 0.7)
        self.assertTrue(is_spam)
        self.assertGreater(confidence, 0.5)
        self.assertIn('إجازة', keywords)
    
    def test_detect_obfuscation(self):
        """اختبار كشف التمويه"""
        text = "ت.ق.ر.ي.ر ط.ب.ي"
        obfuscation_score, types = detection_engine.detect_obfuscation(text)
        self.assertGreater(obfuscation_score, 0)
        self.assertIn('dots', types)
    
    def test_detect_phone_numbers(self):
        """اختبار كشف أرقام الهاتف"""
        text = "للتواصل +966541904263 أو 0556789012"
        numbers = detection_engine.detect_phone_numbers(text)
        self.assertGreater(len(numbers), 0)
    
    def test_fuzzy_match(self):
        """اختبار المطابقة الضبابية"""
        result = detection_engine.fuzzy_match("إجاز", "إجازة", 0.8)
        self.assertTrue(result)
    
    def test_extract_keywords(self):
        """اختبار استخراج الكلمات"""
        text = "إجازة طبية موثقة"
        keywords = detection_engine.extract_keywords(text)
        self.assertIn('إجازة', keywords)
        self.assertIn('طبية', keywords)


class TestDatabaseService(unittest.TestCase):
    """اختبارات خدمة قاعدة البيانات"""
    
    def setUp(self):
        """إعداد الاختبار"""
        self.db = SessionLocal()
    
    def tearDown(self):
        """تنظيف بعد الاختبار"""
        self.db.close()
    
    def test_get_or_create_chat_settings(self):
        """اختبار الحصول على أو إنشاء إعدادات القروب"""
        settings = DatabaseService.get_or_create_chat_settings(
            self.db, 12345, "Test Chat"
        )
        self.assertIsNotNone(settings)
        self.assertEqual(settings.chat_id, 12345)
        self.assertTrue(settings.is_enabled)
    
    def test_set_chat_enabled(self):
        """اختبار تفعيل/تعطيل القروب"""
        DatabaseService.get_or_create_chat_settings(self.db, 12345, "Test")
        DatabaseService.set_chat_enabled(self.db, 12345, False)
        settings = DatabaseService.get_or_create_chat_settings(self.db, 12345)
        self.assertFalse(settings.is_enabled)
    
    def test_set_chat_sensitivity(self):
        """اختبار تعديل حساسية الكشف"""
        DatabaseService.get_or_create_chat_settings(self.db, 12345, "Test")
        DatabaseService.set_chat_sensitivity(self.db, 12345, 0.5)
        settings = DatabaseService.get_or_create_chat_settings(self.db, 12345)
        self.assertEqual(settings.detection_sensitivity, 0.5)
    
    def test_whitelist_operations(self):
        """اختبار عمليات القائمة البيضاء"""
        # إضافة مستخدم
        DatabaseService.add_user_to_whitelist(self.db, 12345, 67890, "testuser")
        
        # التحقق من الإضافة
        is_whitelisted = DatabaseService.is_user_whitelisted(self.db, 12345, 67890)
        self.assertTrue(is_whitelisted)
        
        # إزالة المستخدم
        DatabaseService.remove_user_from_whitelist(self.db, 12345, 67890)
        
        # التحقق من الحذف
        is_whitelisted = DatabaseService.is_user_whitelisted(self.db, 12345, 67890)
        self.assertFalse(is_whitelisted)
    
    def test_blacklist_operations(self):
        """اختبار عمليات القائمة السوداء"""
        # إضافة مستخدم
        DatabaseService.add_user_to_blacklist(self.db, 12345, 67890, "spammer")
        
        # التحقق من الإضافة
        is_blacklisted = DatabaseService.is_user_blacklisted(self.db, 12345, 67890)
        self.assertTrue(is_blacklisted)


class TestSpamDetectionExamples(unittest.TestCase):
    """اختبارات أمثلة الرسائل المزعجة"""
    
    def test_example_1_sick_leave_offer(self):
        """اختبار مثال 1: عرض إجازة مرضية"""
        text = "تطلع اعذار الطبية الموثق ب التطبيق\n+966541904263"
        is_spam, confidence, keywords = detection_engine.detect_spam(text, 1, 1, 0.7)
        self.assertTrue(is_spam, f"يجب أن تكون الرسالة مزعجة، confidence={confidence}")
    
    def test_example_2_obfuscated_leave(self):
        """اختبار مثال 2: إجازة مموهة"""
        text = "🌹تضبط سڰليف رسمي حتى لو كان الغياب قديم من مستشفيات حكومية\nوتساب:+966541904263"
        is_spam, confidence, keywords = detection_engine.detect_spam(text, 1, 1, 0.7)
        self.assertTrue(is_spam, f"يجب أن تكون الرسالة مزعجة، confidence={confidence}")
    
    def test_example_3_dotted_text(self):
        """اختبار مثال 3: نص بنقاط"""
        text = "نستقبل طلباتكم بكل ود إنجا.ز فوري معتم.د"
        is_spam, confidence, keywords = detection_engine.detect_spam(text, 1, 1, 0.7)
        self.assertTrue(is_spam, f"يجب أن تكون الرسالة مزعجة، confidence={confidence}")
    
    def test_example_4_numbered_list(self):
        """اختبار مثال 4: قائمة مرقمة"""
        text = "١- سكليف (أجازة مرضية)\n- تاريخ قديم - تاريخ جديد\nللتواصل عبر الواتس+966562937246"
        is_spam, confidence, keywords = detection_engine.detect_spam(text, 1, 1, 0.7)
        self.assertTrue(is_spam, f"يجب أن تكون الرسالة مزعجة، confidence={confidence}")


if __name__ == '__main__':
    unittest.main()
