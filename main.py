#!/usr/bin/env python3
"""
بوت تلقرام لحذف الإعلانات المزعجة عن الإجازات المرضية
Telegram Bot for Removing Spam Ads about Medical Leave
"""

import asyncio
import logging
import sys
from pathlib import Path

# إضافة مسار المشروع
sys.path.insert(0, str(Path(__file__).parent))

from app.bot import create_bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main():
    """الدالة الرئيسية"""
    try:
        logger.info("🚀 جاري بدء بوت حذف الإعلانات المزعجة...")
        
        # إنشاء البوت
        bot = create_bot()
        bot.setup()
        
        # بدء البوت
        await bot.start()
        
        # الحفاظ على تشغيل البوت
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("🛑 تم إيقاف البوت من قبل المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
