# بوت تلقرام - سكريبت التثبيت على Windows (PowerShell)
# Telegram Bot - Windows Installation Script (PowerShell)

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "بوت حذف الإعلانات المزعجة" -ForegroundColor Green
Write-Host "Spam Bot Installer for Windows" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# تحديث pip
Write-Host "[1/4] تحديث pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { exit 1 }

# تحديث setuptools
Write-Host "[2/4] تحديث setuptools..." -ForegroundColor Yellow
pip install --upgrade setuptools wheel
if ($LASTEXITCODE -ne 0) { exit 1 }

# إنشاء بيئة افتراضية
Write-Host "[3/4] إنشاء بيئة افتراضية..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "البيئة الافتراضية موجودة بالفعل" -ForegroundColor Cyan
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# تفعيل البيئة الافتراضية
Write-Host "[4/4] تفعيل البيئة الافتراضية وتثبيت المكتبات..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# محاولة تثبيت من requirements_windows.txt
Write-Host ""
Write-Host "محاولة التثبيت من requirements_windows.txt..." -ForegroundColor Cyan
pip install -r requirements_windows.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "تحذير: فشل التثبيت من requirements_windows.txt" -ForegroundColor Yellow
    Write-Host "جاري محاولة التثبيت من requirements_minimal.txt..." -ForegroundColor Yellow
    pip install -r requirements_minimal.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "====================================" -ForegroundColor Red
        Write-Host "❌ حدث خطأ في التثبيت" -ForegroundColor Red
        Write-Host "====================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "جرّب الحلول التالية:" -ForegroundColor Yellow
        Write-Host "1. نقل المشروع من المسار العربي" -ForegroundColor White
        Write-Host "2. تحديث Python إلى أحدث إصدار" -ForegroundColor White
        Write-Host "3. تثبيت Visual C++ Build Tools" -ForegroundColor White
        Write-Host ""
        exit 1
    }
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host "✅ تم التثبيت بنجاح!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "الخطوة التالية:" -ForegroundColor Cyan
Write-Host "1. أنشئ ملف .env وأضف رمز البوت" -ForegroundColor White
Write-Host "2. شغّل: python main.py" -ForegroundColor White
Write-Host ""
