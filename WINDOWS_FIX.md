# 🪟 حل مشاكل التثبيت على Windows

## المشكلة: خطأ في تثبيت Pillow

```
ERROR: Failed to build 'Pillow' when getting requirements to build wheel
KeyError: '__version__'
```

هذا الخطأ يحدث عند محاولة بناء مكتبة Pillow من المصدر على Windows.

---

## ✅ الحل 1: استخدام ملف requirements محسّن (الأسهل)

### الخطوات:

1. **احذف البيئة الافتراضية الحالية:**
```bash
deactivate
rmdir /s venv
```

2. **أنشئ بيئة افتراضية جديدة:**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **ثبّت المكتبات باستخدام الملف المحسّن:**
```bash
pip install -r requirements_windows.txt
```

---

## ✅ الحل 2: تثبيت Pillow بشكل منفصل

إذا استمرت المشكلة، جرّب هذا:

```bash
# أولاً، ثبّت Pillow من عجلات محسّنة مسبقاً
pip install --only-binary :all: Pillow

# ثم ثبّت باقي المكتبات
pip install python-telegram-bot==20.7
pip install fastapi==0.109.0
pip install uvicorn==0.27.0
pip install sqlalchemy==2.0.23
pip install pydantic==2.5.0
pip install python-dotenv==1.0.0
pip install aiohttp==3.9.1
pip install pytesseract==0.3.10
pip install regex==2023.12.25
```

---

## ✅ الحل 3: حذف Pillow من requirements (إذا لم تحتجها)

إذا كنت لا تستخدم معالجة الصور، يمكنك حذف Pillow:

```bash
# استخدم هذا الملف بدلاً من requirements.txt
pip install -r requirements_minimal.txt
```

**ملف requirements_minimal.txt:**
```
python-telegram-bot==20.7
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-dotenv==1.0.0
aiohttp==3.9.1
regex==2023.12.25
```

---

## ✅ الحل 4: تحديث pip و setuptools

أحياناً المشكلة تكون في أدوات البناء:

```bash
# تحديث pip
python -m pip install --upgrade pip

# تحديث setuptools
pip install --upgrade setuptools wheel

# ثم جرّب التثبيت مرة أخرى
pip install -r requirements.txt
```

---

## ✅ الحل 5: استخدام نسخة أقدم من Pillow

إذا استمرت المشكلة، جرّب نسخة أقدم:

```bash
pip install Pillow==9.5.0
```

---

## 🔍 استكشاف إضافي

### تحقق من إصدار Python:
```bash
python --version
```
تأكد من استخدام Python 3.8 أو أحدث.

### تحقق من وجود Visual C++ Build Tools:
على Windows، قد تحتاج إلى:
- **Visual Studio Build Tools**
- أو **Microsoft C++ Build Tools**

[تحميل من هنا](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### إذا كان المسار يحتوي على أحرف عربية:

المشكلة قد تكون أيضاً بسبب المسار الذي يحتوي على أحرف عربية:
```
C:\Users\mohmm\Downloads\بوت لحذف الإعلانات المزعجة في قروب التلقرام\...
```

**الحل:** انقل المشروع إلى مسار بدون أحرف عربية:
```bash
# انقل المشروع إلى:
C:\Users\mohmm\Downloads\telegram_spam_bot\
```

---

## ✅ الحل النهائي (الموصى به)

إذا فشلت جميع الحلول السابقة:

1. **احذف كل شيء:**
```bash
deactivate
rmdir /s venv
del requirements.txt
```

2. **استخدم ملف requirements_windows.txt:**
```bash
# أنشئ بيئة جديدة
python -m venv venv
venv\Scripts\activate

# ثبّت من الملف المحسّن
pip install -r requirements_windows.txt
```

3. **إذا استمرت المشكلة، استخدم الملف الأدنى:**
```bash
pip install -r requirements_minimal.txt
```

---

## 📞 إذا استمرت المشكلة

جرّب هذا الأمر للحصول على معلومات تفصيلية:

```bash
pip install -r requirements.txt -v
```

ثم شارك الرسالة الكاملة لنساعدك بشكل أفضل.

---

## ✅ التحقق من التثبيت الناجح

بعد التثبيت، تحقق من أن كل شيء يعمل:

```bash
python -c "import telegram; print('✅ python-telegram-bot OK')"
python -c "import fastapi; print('✅ fastapi OK')"
python -c "import sqlalchemy; print('✅ sqlalchemy OK')"
python -c "import pydantic; print('✅ pydantic OK')"
```

---

**نصيحة:** استخدم الحل 1 أولاً، وإذا لم ينجح، جرّب الحل 2 أو 3.
