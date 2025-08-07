#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동 시장 브리핑 시스템
한국투자증권 API + Threads 자동 게시
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# .env 파일 로드 (로컬 개발용)
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.info(".env 파일 로드 완료")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.info("python-dotenv가 설치되지 않았습니다. 시스템 환경변수를 사용합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('briefing_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 모듈 import
from market_data_strategy import MarketDataStrategy
from market_briefing_generator import MarketBriefingGenerator
from threads_api_client import ThreadsPublisher


class AutoBriefingSystem:
    """자동 브리핑 시스템"""
    
    def __init__(self):
        self.market_strategy = MarketDataStrategy()
        self.briefing_generator = MarketBriefingGenerator()
        self.threads_publisher = ThreadsPublisher()
        
        # 시간대별 주제 매핑
        self.time_topics = {
            "07:00": "미국 증시 마감 요약",
            "08:00": "오늘의 한국시장 전망",
            "12:00": "오전장 시황 요약",
            "15:40": "한국시장 마감 요약",
            "19:00": "미국장 개장 전 체크",
            "now": "현재 시황 브리핑"
        }
        
        logger.info("자동 브리핑 시스템 초기화 완료")
    
    def get_current_briefing_type(self) -> str:
        """
        현재 시간에 따른 브리핑 타입 결정
        
        Returns:
            str: 브리핑 타입 (07:00, 08:00, 12:00, 15:40, 19:00)
        """
        from datetime import datetime, time
        
        now = datetime.now()
        current_time = now.time()
        
        # 장 시간 정의
        korea_open = time(9, 0)
        korea_close = time(15, 30)
        us_open = time(22, 30)  # KST 기준
        us_close = time(5, 0)   # KST 기준 (다음날)
        
        # 한국장 시간 (09:00-15:30)
        if korea_open <= current_time <= korea_close:
            # 오전장 (09:00-12:00)
            if current_time < time(12, 0):
                return "12:00"  # 오전장 시황
            # 오후장 (12:00-15:30)
            else:
                return "15:40"  # 마감 브리핑
        
        # 미국장 시간 (22:30-05:00, 다음날)
        elif current_time >= us_open or current_time <= us_close:
            if current_time >= us_open:  # 22:30 이후
                return "19:00"  # 미국장 프리뷰
            else:  # 05:00 이전
                return "07:00"  # 미국 마켓 마감
        
        # 장 외 시간
        else:
            # 아침 (05:00-09:00)
            if us_close <= current_time < korea_open:
                return "08:00"  # 한국시장 프리뷰
            # 저녁 (15:30-22:30)
            else:
                return "19:00"  # 미국장 프리뷰
    
    def run_current_briefing(self) -> Dict[str, Any]:
        """
        현재 시황에 맞는 브리핑 실행
        
        Returns:
            Dict: 실행 결과
        """
        current_type = self.get_current_briefing_type()
        logger.info(f"현재 시황 브리핑 타입 결정: {current_type}")
        
        return self.run_briefing(current_type)
    
    def run_briefing(self, time_slot: str) -> Dict[str, Any]:
        """
        브리핑 실행 (전체 워크플로우)
        
        Args:
            time_slot: 시간대 (07:00, 08:00, 12:00, 15:40, 19:00)
            
        Returns:
            Dict: 실행 결과
        """
        try:
            logger.info(f"브리핑 실행 시작: {time_slot}")
            
            # 1. 전략적 시장 데이터 수집
            logger.info("1단계: 전략적 시장 데이터 수집")
            market_data = self.market_strategy.get_market_data_with_strategy(time_slot)
            
            if not market_data:
                raise Exception("시장 데이터 수집 실패")
            
            logger.info(f"데이터 수집 완료: {len(market_data.get('indices', {}))}개 지수 (소스: {market_data.get('source', 'unknown')})")
            
            # 2. 브리핑 생성
            logger.info("2단계: 브리핑 생성")
            topic = self.time_topics.get(time_slot, "시장 브리핑")
            briefing = self.briefing_generator.generate_briefing(time_slot, topic, market_data)
            
            # 3. Threads 포맷으로 변환
            formatted_content = self.briefing_generator.format_for_threads(briefing)
            
            # 4. Threads 게시
            logger.info("3단계: Threads 게시")
            publish_result = self.threads_publisher.publish_briefing(
                time_slot, topic, formatted_content
            )
            
            # 5. 결과 정리
            result = {
                "success": True,
                "time_slot": time_slot,
                "topic": topic,
                "market_data": market_data,
                "briefing_content": formatted_content,
                "publish_result": publish_result,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"브리핑 실행 완료: {time_slot}")
            return result
            
        except Exception as e:
            logger.error(f"브리핑 실행 실패: {e}")
            return {
                "success": False,
                "time_slot": time_slot,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_all_briefings(self) -> Dict[str, Any]:
        """모든 시간대 브리핑 실행"""
        results = {}
        
        for time_slot in self.time_topics.keys():
            logger.info(f"=== {time_slot} 브리핑 실행 ===")
            result = self.run_briefing(time_slot)
            results[time_slot] = result
            
            # API 호출 제한을 위한 대기
            import time
            time.sleep(2)
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "kis_api_available": bool(self.market_strategy.kis_client.trenv),
            "threads_api_available": bool(self.threads_publisher.client.access_token),
            "total_posts": len(self.threads_publisher.get_post_history()),
            "last_post": self.threads_publisher.get_post_stats().get("last_post"),
            "system_time": datetime.now().isoformat()
        }
    
    def save_briefing_data(self, result: Dict[str, Any], filename: Optional[str] = None):
        """브리핑 데이터 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"briefing_data_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"브리핑 데이터 저장 완료: {filename}")
        except Exception as e:
            logger.error(f"브리핑 데이터 저장 실패: {e}")


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="자동 시장 브리핑 시스템")
    parser.add_argument(
        '--time', '-t',
        choices=['07:00', '08:00', '12:00', '15:40', '19:00', 'now'],
        help='실행할 시간대 (now: 현재 시황에 맞는 브리핑)'
    )
    parser.add_argument(
        '--save', '-s',
        action='store_true',
        help='결과를 파일로 저장'
    )
    parser.add_argument(
        '--status', '-i',
        action='store_true',
        help='시스템 상태 조회'
    )
    
    args = parser.parse_args()
    
    # 시스템 초기화
    system = AutoBriefingSystem()
    
    # 시스템 상태 조회
    if args.status:
        status = system.get_system_status()
        print("=== 시스템 상태 ===")
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return
    
    # 브리핑 실행
    if args.time == 'now':
        print("=== 현재 시황 브리핑 실행 ===")
        result = system.run_current_briefing()
        
        if result['success']:
            print(f"✅ 성공: {result['topic']}")
            print(f"선택된 브리핑 타입: {result['time_slot']}")
            print("\n=== 생성된 브리핑 ===")
            print(result['briefing_content'])
            print(f"\n게시 결과: {result['publish_result'].get('success', False)}")
            
            if args.save:
                system.save_briefing_data(result, f"briefing_now_{result['time_slot'].replace(':', '')}.json")
        else:
            print(f"❌ 실패: {result.get('error', 'Unknown error')}")
    
    elif args.time:
        print(f"=== {args.time} 브리핑 실행 ===")
        result = system.run_briefing(args.time)
        
        if result['success']:
            print(f"✅ 성공: {result['topic']}")
            print("\n=== 생성된 브리핑 ===")
            print(result['briefing_content'])
            print(f"\n게시 결과: {result['publish_result'].get('success', False)}")
            
            if args.save:
                system.save_briefing_data(result, f"briefing_{args.time.replace(':', '')}.json")
        else:
            print(f"❌ 실패: {result.get('error', 'Unknown error')}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 