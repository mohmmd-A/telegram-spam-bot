"""
خدمة التحليلات لتتبع أنماط الرسائل المزعجة
Analytics Service for Tracking Spam Patterns
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class AnalyticsService:
    """خدمة التحليلات"""
    
    def __init__(self):
        self.spam_count = 0
        self.legitimate_count = 0
        self.keyword_frequency: Dict[str, int] = defaultdict(int)
        self.hourly_stats: Dict[str, int] = defaultdict(int)
        self.user_stats: Dict[int, Dict] = defaultdict(lambda: {'spam': 0, 'legitimate': 0})
    
    def record_spam(self, chat_id: int, user_id: int, keywords: List[str]) -> None:
        """Record spam message"""
        self.spam_count += 1
        
        # Record keywords
        for keyword in keywords:
            self.keyword_frequency[keyword] += 1
        
        # Record hourly stats
        hour_key = datetime.now().strftime("%Y-%m-%d %H:00")
        self.hourly_stats[hour_key] += 1
        
        # Record user stats
        self.user_stats[user_id]['spam'] += 1
    
    def record_legitimate(self, user_id: int) -> None:
        """Record legitimate message"""
        self.legitimate_count += 1
        self.user_stats[user_id]['legitimate'] += 1
    
    def get_stats(self) -> Dict:
        """Get overall statistics"""
        total = self.spam_count + self.legitimate_count
        spam_rate = (self.spam_count / total * 100) if total > 0 else 0
        
        return {
            'total_messages': total,
            'spam_count': self.spam_count,
            'legitimate_count': self.legitimate_count,
            'spam_rate': f"{spam_rate:.2f}%",
            'top_keywords': self.get_top_keywords(10),
            'hourly_distribution': dict(sorted(self.hourly_stats.items())[-24:]),
        }
    
    def get_top_keywords(self, limit: int = 10) -> List[tuple]:
        """Get top spam keywords"""
        return sorted(
            self.keyword_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        stats = self.user_stats.get(user_id, {'spam': 0, 'legitimate': 0})
        total = stats['spam'] + stats['legitimate']
        spam_rate = (stats['spam'] / total * 100) if total > 0 else 0
        
        return {
            'user_id': user_id,
            'spam_count': stats['spam'],
            'legitimate_count': stats['legitimate'],
            'total': total,
            'spam_rate': f"{spam_rate:.2f}%",
            'risk_level': self._calculate_risk_level(stats['spam'], total)
        }
    
    def _calculate_risk_level(self, spam_count: int, total: int) -> str:
        """Calculate user risk level"""
        if total == 0:
            return "unknown"
        
        spam_rate = spam_count / total
        if spam_rate >= 0.8:
            return "critical"
        elif spam_rate >= 0.5:
            return "high"
        elif spam_rate >= 0.2:
            return "medium"
        else:
            return "low"
    
    def reset_stats(self) -> None:
        """Reset all statistics"""
        self.spam_count = 0
        self.legitimate_count = 0
        self.keyword_frequency.clear()
        self.hourly_stats.clear()
        self.user_stats.clear()
        logger.info("تم إعادة تعيين الإحصائيات")


# Global analytics instance
analytics = AnalyticsService()
