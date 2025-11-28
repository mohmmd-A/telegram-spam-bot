@echo off
REM بوت حذف الإعلانات المزعجة - سكريبت التثبيت للـ Windows
REM Telegram Spam Killer Bot - Windows Setup Script

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo 🚀 بوت حذف الإعلانات المزعجة - سكريبت التثبيت
echo ======================================================================
echo.

REM التحقق من Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطأ: Python غير مثبت على جهازك
    echo.
    echo 📥 الحل:
    echo 1. اذهب إلى https://www.python.org/downloads/
    echo 2. حمّل Python 3.8 أو أحدث
    echo 3. أثناء التثبيت، تأكد من تحديد "Add Python to PATH"
    echo 4. أعد تشغيل هذا السكريبت
    echo.
    pause
    exit /b 1
)

echo ✅ تم اكتشاف Python
python --version
echo.

REM إنشاء بيئة افتراضية
echo 📦 جاري إنشاء بيئة افتراضية...
if exist venv (
    echo ℹ️ البيئة الافتراضية موجودة بالفعل
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ فشل إنشاء البيئة الافتراضية
        pause
        exit /b 1
    )
    echo ✅ تم إنشاء البيئة الافتراضية
)
echo.

REM تفعيل البيئة الافتراضية
echo 🔧 جاري تفعيل البيئة الافتراضية...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ فشل تفعيل البيئة الافتراضية
    pause
    exit /b 1
)
echo ✅ تم تفعيل البيئة الافتراضية
echo.

REM تحديث pip
echo 📥 جاري تحديث pip...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ تم تحديث pip
echo.

REM تثبيت المكتبات
echo 📚 جاري تثبيت المكتبات المطلوبة...
echo (هذا قد يستغرق دقيقة أو دقيقتين)
echo.

if exist requirements_windows.txt (
    pip install -r requirements_windows.txt
) else (
    pip install -r requirements.txt
)

if errorlevel 1 (
    echo ❌ فشل تثبيت المكتبات
    echo.
    echo 💡 الحل البديل:
    echo pip install -r requirements_minimal.txt
    echo.
    pause
    exit /b 1
)

echo ✅ تم تثبيت جميع المكتبات
echo.

REM إنشاء ملف .env
echo 📝 جاري إعداد ملف الإعدادات...
if exist .env (
    echo ℹ️ ملف .env موجود بالفعل
) else (
    if exist .env.example (
        copy .env.example .env >nul
        echo ✅ تم إنشاء ملف .env
    ) else (
        echo ❌ ملف .env.example غير موجود
    )
)
echo.

REM إظهار التعليمات
echo ======================================================================
echo ✅ تم التثبيت بنجاح!
echo ======================================================================
echo.
echo 📝 الخطوة التالية:
echo 1. افتح ملف .env بمحرر نصوص
echo 2. أضف رمز البوت:
echo    TELEGRAM_BOT_TOKEN=your_token_here
echo 3. استبدل your_token_here برمز البوت الحقيقي
echo.
echo 💡 للحصول على رمز البوت:
echo 1. افتح تلقرام وابحث عن @BotFather
echo 2. أرسل: /newbot
echo 3. اتبع التعليمات
echo 4. انسخ الرمز
echo.
echo 🚀 لتشغيل البوت:
echo python main.py
echo.
echo 📖 للمساعدة:
echo اقرأ ملف README_USER.md
echo.
echo ======================================================================
echo.

pause
