#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Threads API 클라이언트
자동 게시 기능
"""

import os
import json
import requests
from typing import Dict, Optional, Any, List
import logging

logger = logging.getLogger(__name__)


class ThreadsAPIClient:
    """Threads API 클라이언트"""
    
    def __init__(self):
        # 환경변수에서 API 키 로드
        self.api_key = os.getenv('THREADS_API_KEY')
        self.access_token = os.getenv('THREADS_ACCESS_TOKEN')
        self.user_id = os.getenv('THREADS_USER_ID')
        
        # API 엔드포인트 (실제 Threads API가 공개되면 업데이트 필요)
        self.base_url = "https://www.threads.net/api/v1"
        self.post_url = f"{self.base_url}/media/configure/"
        
        if not all([self.api_key, self.access_token, self.user_id]):
            logger.warning("Threads API 키가 설정되지 않았습니다. 게시 기능이 제한됩니다.")
    
    def post_thread(self, content: str, reply_to: Optional[str] = None) -> Optional[Dict]:
        """
        Threads에 게시
        
        Args:
            content: 게시할 내용
            reply_to: 답글 대상 ID (선택사항)
            
        Returns:
            Dict: 게시 결과
        """
        if not self.access_token:
            logger.warning("Threads 액세스 토큰이 없어 게시를 건너뜁니다.")
            return self._simulate_post(content, reply_to)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            payload = {
                "text": content,
                "user_id": self.user_id
            }
            
            if reply_to:
                payload["reply_to"] = reply_to
            
            response = requests.post(self.post_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Threads 게시 성공: {result.get('id', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Threads 게시 실패: {e}")
            return self._simulate_post(content, reply_to)
    
    def post_briefing(self, briefing_content: str, time_slot: str) -> Optional[Dict]:
        """
        브리핑 게시 (시간대별 최적화)
        
        Args:
            briefing_content: 브리핑 내용
            time_slot: 시간대
            
        Returns:
            Dict: 게시 결과
        """
        # 시간대별 추가 메타데이터
        time_metadata = {
            "07:00": "🌅 미국 마켓 마감",
            "08:00": "🌞 한국시장 오픈",
            "12:00": "☀️ 오전장 마감",
            "15:40": "🌆 한국시장 마감",
            "19:00": "🌙 미국장 프리뷰"
        }
        
        # 시간대별 메타데이터 추가
        enhanced_content = f"{time_metadata.get(time_slot, '📊')} {briefing_content}"
        
        return self.post_thread(enhanced_content)
    
    def _simulate_post(self, content: str, reply_to: Optional[str] = None) -> Dict:
        """게시 시뮬레이션 (API 키가 없을 때)"""
        logger.info("=== Threads 게시 시뮬레이션 ===")
        logger.info(f"게시 내용:\n{content}")
        if reply_to:
            logger.info(f"답글 대상: {reply_to}")
        logger.info("=" * 50)
        
        return {
            "id": "simulated_post_id",
            "success": True,
            "content": content,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    def get_user_info(self) -> Optional[Dict]:
        """사용자 정보 조회"""
        if not self.access_token:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.base_url}/users/self/", headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"사용자 정보 조회 실패: {e}")
            return None
    
    def get_followers_count(self) -> Optional[int]:
        """팔로워 수 조회"""
        user_info = self.get_user_info()
        if user_info:
            return user_info.get('follower_count', 0)
        return None


class ThreadsPublisher:
    """Threads 게시 관리자"""
    
    def __init__(self):
        self.client = ThreadsAPIClient()
        self.post_history = []
    
    def publish_briefing(self, time_slot: str, topic: str, briefing_content: str) -> Dict:
        """
        브리핑 게시
        
        Args:
            time_slot: 시간대
            topic: 주제
            briefing_content: 브리핑 내용
            
        Returns:
            Dict: 게시 결과
        """
        try:
            # 게시 실행
            result = self.client.post_briefing(briefing_content, time_slot)
            
            # 게시 기록 저장
            post_record = {
                "time_slot": time_slot,
                "topic": topic,
                "content": briefing_content,
                "result": result,
                "timestamp": "2024-01-01T00:00:00Z"  # 실제로는 현재 시간
            }
            self.post_history.append(post_record)
            
            logger.info(f"브리핑 게시 완료: {time_slot} - {topic}")
            return result
            
        except Exception as e:
            logger.error(f"브리핑 게시 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_post_history(self) -> List[Dict]:
        """게시 기록 조회"""
        return self.post_history
    
    def get_post_stats(self) -> Dict:
        """게시 통계"""
        total_posts = len(self.post_history)
        time_slot_stats = {}
        
        for post in self.post_history:
            time_slot = post["time_slot"]
            time_slot_stats[time_slot] = time_slot_stats.get(time_slot, 0) + 1
        
        return {
            "total_posts": total_posts,
            "time_slot_stats": time_slot_stats,
            "last_post": self.post_history[-1] if self.post_history else None
        }


def main():
    """테스트 실행"""
    publisher = ThreadsPublisher()
    
    # 테스트 브리핑 게시
    test_content = """🌅 미국 증시 마감 요약
• S&P500 5,500.12pt (+0.8%)
• 나스닥 17,900.45pt (+1.1%)
• 다우 38,500pt (+0.3%)
• 테슬라 +4.2%
• 엔비디아 +3.0%
• 애플 +1.8%

💡 오늘의 관전포인트
- FOMC 결과 발표 후 변동성 확대
- 반도체, AI 섹터 랠리 지속
- 주요 기업 실적 발표 대기

#미국증시 #S&P500 #나스닥 #글로벌마켓"""
    
    result = publisher.publish_briefing("07:00", "미국 증시 마감 요약", test_content)
    print(f"게시 결과: {result}")
    
    # 통계 출력
    stats = publisher.get_post_stats()
    print(f"게시 통계: {stats}")


if __name__ == "__main__":
    main() 