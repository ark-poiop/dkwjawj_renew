#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시간대별 브리핑 타입 결정 테스트
"""

from datetime import datetime, time
from auto_briefing_system import AutoBriefingSystem

def test_briefing_type_determination():
    """시간대별 브리핑 타입 결정 테스트"""
    print("=== 시간대별 브리핑 타입 결정 테스트 ===")
    
    # 테스트할 시간대들
    test_cases = [
        ("09:30", "12:00"),  # 한국장 오전장
        ("12:30", "15:40"),  # 한국장 오후장
        ("15:45", "19:00"),  # 한국장 마감 후
        ("22:45", "19:00"),  # 미국장 개장 후
        ("04:30", "07:00"),  # 미국장 마감 전
        ("07:30", "08:00"),  # 아침 프리뷰
    ]
    
    for test_time, expected_type in test_cases:
        # 시간 파싱
        hour, minute = map(int, test_time.split(':'))
        test_datetime = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        print(f"\n--- 테스트 시간: {test_time} ---")
        print(f"예상 브리핑 타입: {expected_type}")
        
        # 장 시간 정의
        korea_open = time(9, 0)
        korea_close = time(15, 30)
        us_open = time(22, 30)
        us_close = time(5, 0)
        
        current_time = test_datetime.time()
        
        # 실제 로직 테스트
        if korea_open <= current_time <= korea_close:
            if current_time < time(12, 0):
                actual_type = "12:00"
            else:
                actual_type = "15:40"
        elif current_time >= us_open or current_time <= us_close:
            if current_time >= us_open:
                actual_type = "19:00"
            else:
                actual_type = "07:00"
        else:
            if us_close <= current_time < korea_open:
                actual_type = "08:00"
            else:
                actual_type = "19:00"
        
        print(f"실제 브리핑 타입: {actual_type}")
        print(f"결과: {'✅' if actual_type == expected_type else '❌'}")

def test_current_time_briefing():
    """현재 시간 브리핑 테스트"""
    print("\n=== 현재 시간 브리핑 테스트 ===")
    
    system = AutoBriefingSystem()
    current_type = system.get_current_briefing_type()
    
    print(f"현재 시간: {datetime.now().strftime('%H:%M:%S')}")
    print(f"선택된 브리핑 타입: {current_type}")
    
    # 브리핑 실행 테스트 (실제 게시는 하지 않음)
    print("\n브리핑 내용 미리보기:")
    try:
        result = system.run_briefing(current_type)
        if result['success']:
            content = result['briefing_content']
            print(content[:200] + "..." if len(content) > 200 else content)
        else:
            print(f"브리핑 생성 실패: {result.get('error')}")
    except Exception as e:
        print(f"테스트 중 오류: {e}")

if __name__ == "__main__":
    test_briefing_type_determination()
    test_current_time_briefing()
