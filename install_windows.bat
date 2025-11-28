@echo off
REM بوت تلقرام - سكريبت التثبيت على Windows
REM Telegram Bot - Windows Installation Script

echo.
echo ====================================
echo بوت حذف الإعلانات المزعجة
echo Spam Bot Installer for Windows
echo ====================================
echo.

REM تحديث pip
echo [1/4] تحديث pip...
python -m pip install --upgrade pip
if errorlevel 1 goto error

REM تحديث setuptools
echo [2/4] تحديث setuptools...
pip install --upgrade setuptools wheel
if errorlevel 1 goto error

REM إنشاء بيئة افتراضية
echo [3/4] إنشاء بيئة افتراضية...
if exist venv (
    echo البيئة الافتراضية موجودة بالفعل
) else (
    python -m venv venv
    if errorlevel 1 goto error
)

REM تفعيل البيئة الافتراضية
echo [4/4] تفعيل البيئة الافتراضية وتثبيت المكتبات...
call venv\Scripts\activate.bat

REM محاولة تثبيت من requirements_windows.txt
echo.
echo محاولة التثبيت من requirements_windows.txt...
pip install -r requirements_windows.txt
if errorlevel 1 (
    echo.
    echo تحذير: فشل التثبيت من requirements_windows.txt
    echo جاري محاولة التثبيت من requirements_minimal.txt...
    pip install -r requirements_minimal.txt
    if errorlevel 1 goto error
)

echo.
echo ====================================
echo ✅ تم التثبيت بنجاح!
echo ====================================
echo.
echo الخطوة التالية:
echo 1. أنشئ ملف .env وأضف رمز البوت
echo 2. شغّل: python main.py
echo.
pause
goto end

:error
echo.
echo ====================================
echo ❌ حدث خطأ في التثبيت
echo ====================================
echo.
echo جرّب الحلول التالية:
echo 1. نقل المشروع من المسار العربي
echo 2. تحديث Python إلى أحدث إصدار
echo 3. تثبيت Visual C++ Build Tools
echo.
pause
goto end

:end
