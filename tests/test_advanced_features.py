"""
اختبارات المزايا المتقدمة
Advanced Features Tests
"""

import unittest
from app.services.advanced_detection import TextNormalizer, AdvancedSpamDetector


class TestTextNormalizer(unittest.TestCase):
    """اختبارات معالج تطبيع النصوص"""
    
    def test_remove_diacritics(self):
        """اختبار إزالة الحركات"""
        text = "إِجَازَة مَرَضِيَّة"
        normalized = TextNormalizer.remove_diacritics(text)
        self.assertEqual(normalized, "إجازة مرضية")
    
    def test_remove_extra_spaces(self):
        """اختبار إزالة المسافات الزائدة"""
        text = "إ جـــا  زة  م ـــر ـــض ـــي ـــة"
        normalized = TextNormalizer.remove_extra_spaces(text)
        self.assertNotIn("  ", normalized)
    
    def test_remove_special_chars(self):
        """اختبار إزالة الأحرف الخاصة"""
        text = "إ_جـــا_زة-م-ـــر-ـــض"
        normalized = TextNormalizer.remove_special_chars(text)
        self.assertNotIn("_", normalized)
        self.assertNotIn("-", normalized)
    
    def test_normalize_similar_chars(self):
        """اختبار تطبيع الأحرف المتشابهة"""
        text = "آجازة أجازة إجازة"
        normalized = TextNormalizer.normalize_similar_chars(text)
        self.assertEqual(normalized.count("ا"), 3)
    
    def test_full_normalization(self):
        """اختبار التطبيع الشامل"""
        text = "إِ جـــا  زة  م َرَ ـــض ـــي ـــة"
        normalized = TextNormalizer.normalize_text(text)
        self.assertEqual(normalized, "اجازة مرضية")


class TestAdvancedSpamDetector(unittest.TestCase):
    """اختبارات كاشف الإعلانات المتقدم"""
    
    def setUp(self):
        self.detector = AdvancedSpamDetector()
    
    def test_detect_obfuscated_spam(self):
        """اختبار كشف الإعلانات المموهة"""
        message = "إ جـــا  زة  م ـــر ـــض ـــي ـــة"
        keywords = ["إجازة مرضية", "اجازة"]
        
        is_spam, confidence, normalized = self.detector.detect_obfuscated_spam(
            message, keywords
        )
        
        self.assertTrue(is_spam)
        self.assertGreater(confidence, 0.5)
        self.assertEqual(normalized, "اجازة مرضية")
    
    def test_detect_character_distribution(self):
        """اختبار كشف توزيع الأحرف غير الطبيعي"""
        message = "إ جـــا  زة  م ـــر ـــض ـــي ـــة"
        score = self.detector.detect_character_distribution(message)
        
        self.assertGreater(score, 0.3)  # درجة تمويه عالية
    
    def test_get_obfuscation_indicators(self):
        """اختبار الحصول على مؤشرات التمويه"""
        message = "إ_جـــا_زة-م-ـــر"
        indicators = self.detector.get_obfuscation_indicators(message)
        
        self.assertTrue(indicators['has_extra_spaces'])
        self.assertTrue(indicators['has_special_chars'])
        self.assertGreater(indicators['obfuscation_score'], 0)
    
    def test_legitimate_message(self):
        """اختبار الرسائل الشرعية"""
        message = "السلام عليكم ورحمة الله وبركاته"
        keywords = ["إجازة مرضية"]
        
        is_spam, confidence, _ = self.detector.detect_obfuscated_spam(
            message, keywords
        )
        
        self.assertFalse(is_spam)
        self.assertLess(confidence, 0.3)


if __name__ == '__main__':
    unittest.main()
