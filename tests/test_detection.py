"""
اختبارات نظام الكشف الذكي عن الإعلانات
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.detection import SpamDetectionEngine


def test_medical_keywords():
    """اختبار كشف الكلمات المفتاحية الطبية"""
    engine = SpamDetectionEngine()
    
    # رسالة تحتوي على كلمات طبية
    message = "لدي إجازة مرضية وأحتاج تقرير طبي"
    is_spam, score, keywords = engine.detect_spam(message, 123, 456)
    
    print(f"✓ اختبار الكلمات الطبية:")
    print(f"  الرسالة: {message}")
    print(f"  هل إعلان: {is_spam}")
    print(f"  درجة الثقة: {score:.2%}")
    print(f"  الكلمات المكتشفة: {keywords}\n")
    
    assert len(keywords) > 0, "يجب اكتشاف كلمات طبية"


def test_phone_numbers():
    """اختبار كشف أرقام الهواتف"""
    engine = SpamDetectionEngine()
    
    # رسالة تحتوي على رقم هاتف
    message = "استشارة طبية - اتصل بنا على +966541904263"
    is_spam, score, keywords = engine.detect_spam(message, 123, 456)
    
    print(f"✓ اختبار أرقام الهواتف:")
    print(f"  الرسالة: {message}")
    print(f"  هل إعلان: {is_spam}")
    print(f"  درجة الثقة: {score:.2%}")
    print(f"  الأنماط المكتشفة: {keywords}\n")
    
    assert any('+966' in k or '0' in k for k in keywords), "يجب اكتشاف رقم هاتف"


def test_spam_indicators():
    """اختبار كشف مؤشرات الإعلانات"""
    engine = SpamDetectionEngine()
    
    # رسالة تحتوي على مؤشرات إعلانية
    message = "عرض خاص - اضغط هنا للمزيد من المعلومات"
    is_spam, score, keywords = engine.detect_spam(message, 123, 456)
    
    print(f"✓ اختبار مؤشرات الإعلانات:")
    print(f"  الرسالة: {message}")
    print(f"  هل إعلان: {is_spam}")
    print(f"  درجة الثقة: {score:.2%}")
    print(f"  المؤشرات المكتشفة: {keywords}\n")


def test_combined_spam():
    """اختبار الكشف المدمج"""
    engine = SpamDetectionEngine()
    
    # رسالة تحتوي على عدة مؤشرات
    message = "إجازة مرضية - تقرير طبي - اتصل بنا +966541904263 - اضغط هنا"
    is_spam, score, keywords = engine.detect_spam(message, 123, 456, sensitivity=0.5)
    
    print(f"✓ اختبار الكشف المدمج:")
    print(f"  الرسالة: {message}")
    print(f"  هل إعلان: {is_spam}")
    print(f"  درجة الثقة: {score:.2%}")
    print(f"  جميع المؤشرات: {keywords}\n")
    
    assert is_spam, "يجب اكتشاف الرسالة كإعلان"


def test_legitimate_message():
    """اختبار الرسائل الشرعية"""
    engine = SpamDetectionEngine()
    
    # رسالة عادية
    message = "السلام عليكم، كيف حالكم؟"
    is_spam, score, keywords = engine.detect_spam(message, 123, 456)
    
    print(f"✓ اختبار الرسائل الشرعية:")
    print(f"  الرسالة: {message}")
    print(f"  هل إعلان: {is_spam}")
    print(f"  درجة الثقة: {score:.2%}\n")
    
    assert not is_spam, "يجب عدم اكتشاف الرسالة كإعلان"


def test_sensitivity_levels():
    """اختبار مستويات الحساسية المختلفة"""
    engine = SpamDetectionEngine()
    
    message = "استشارة طبية متاحة"
    
    print(f"✓ اختبار مستويات الحساسية:")
    print(f"  الرسالة: {message}\n")
    
    for sensitivity in [0.3, 0.5, 0.7, 0.9]:
        is_spam, score, keywords = engine.detect_spam(message, 123, 456, sensitivity=sensitivity)
        print(f"  حساسية {sensitivity:.1%}: إعلان={is_spam}, درجة={score:.2%}")


def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("=" * 60)
    print("🧪 اختبارات نظام الكشف الذكي")
    print("=" * 60 + "\n")
    
    try:
        test_medical_keywords()
        test_phone_numbers()
        test_spam_indicators()
        test_combined_spam()
        test_legitimate_message()
        test_sensitivity_levels()
        
        print("\n" + "=" * 60)
        print("✅ جميع الاختبارات نجحت!")
        print("=" * 60)
    
    except AssertionError as e:
        print(f"\n❌ فشل الاختبار: {e}")
        return False
    
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
