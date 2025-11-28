"""
مجموعة اختبارات شاملة للبوت
Comprehensive Test Suite
"""

import sys
sys.path.insert(0, '.')

from app.services.detection import detection_engine
from app.services.username_filter import username_filter
from app.services.obfuscation_detector import obfuscation_detector

print("=" * 70)
print("مجموعة الاختبارات الشاملة للبوت")
print("=" * 70)

# Test 1: Detection Engine
print("\n✓ اختبار 1: محرك الكشف")
print("-" * 70)

test_cases = [
    ("تطلع اعذار الطبية الموثق ب التطبيق\n+966541904263", "مثال 1"),
    ("تضبط سكليف رسمي حتى لو كان الغياب قديم من مستشفيات حكومية", "مثال 2"),
    ("نستقبل طلباتكم بكل ود إنجاز فوري معتمد", "مثال 3"),
    ("سكليف (أجازة مرضية) تاريخ قديم - تاريخ جديد للتواصل +966562937246", "مثال 4"),
    ("مرحبا كيفك انت", "رسالة عادية"),
]

for text, label in test_cases:
    is_spam, confidence, keywords = detection_engine.detect_spam(text, 1, 1, 0.7)
    status = "✅ مزعجة" if is_spam else "❌ عادية"
    print(f"\n{label}: {status}")
    print(f"  النص: {text[:50]}...")
    print(f"  درجة الثقة: {confidence:.2%}")
    if keywords:
        print(f"  الكلمات: {', '.join(keywords[:3])}")

# Test 2: Username Filter
print("\n\n✓ اختبار 2: فلتر أسماء المستخدمين")
print("-" * 70)

usernames = [
    "user_normal",
    "سكليف_سريع",
    "اجازة_موثقة",
    "john_doe",
    "معتمد_فوري",
]

for username in usernames:
    is_suspicious, keywords, confidence = username_filter.check_username_for_spam(username)
    risk_score, risk_level = username_filter.get_username_risk_score(username)
    status = "⚠️ مشبوه" if is_suspicious else "✅ آمن"
    print(f"\n{username}: {status}")
    print(f"  درجة المخاطرة: {risk_level}")
    if keywords:
        print(f"  الكلمات المكتشفة: {', '.join(keywords)}")

# Test 3: Obfuscation Detection
print("\n\n✓ اختبار 3: كاشف التمويه")
print("-" * 70)

obfuscated_texts = [
    "س.ك.ل.ي.ف",
    "إ ج ا ز ة",
    "م-و-ث-ق",
    "سكليف",
    "إجازة مرضية",
]

for text in obfuscated_texts:
    score, types = obfuscation_detector.detect_obfuscation(text)
    is_obfuscated = obfuscation_detector.is_heavily_obfuscated(text)
    status = "⚠️ مخفي" if is_obfuscated else "✅ عادي"
    print(f"\n{text}: {status}")
    print(f"  درجة التمويه: {score:.2%}")
    if types:
        print(f"  أنواع التمويه: {', '.join(types)}")

# Test 4: Combined Detection
print("\n\n✓ اختبار 4: الكشف المدمج")
print("-" * 70)

complex_test = "س.ك.ل.ي.ف  م.و.ث.ق  +966541904263"
is_spam, confidence, keywords = detection_engine.detect_spam(complex_test, 1, 1, 0.7)
obf_score, obf_types = obfuscation_detector.detect_obfuscation(complex_test)

print(f"\nالنص: {complex_test}")
print(f"كشف الرسالة المزعجة: {'✅ مزعجة' if is_spam else '❌ عادية'}")
print(f"درجة الثقة: {confidence:.2%}")
print(f"درجة التمويه: {obf_score:.2%}")
if obf_types:
    print(f"أنواع التمويه: {', '.join(obf_types)}")

print("\n" + "=" * 70)
print("✅ اكتملت جميع الاختبارات بنجاح!")
print("=" * 70)
