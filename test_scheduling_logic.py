#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시간대별 브리핑 분기 로직 테스트
"""

from datetime import datetime, time

def get_briefing_type_for_time(test_time: time) -> str:
    """시간대별 브리핑 타입 결정 (auto_briefing_system.py와 동일한 로직)"""
    
    # 장 시간 정의
    korea_open = time(9, 0)
    korea_close = time(15, 30)
    us_open = time(22, 30)  # KST 기준
    us_close = time(5, 0)   # KST 기준 (다음날)
    
    # 한국장 시간 (09:00-15:30)
    if korea_open <= test_time <= korea_close:
        # 오전장 (09:00-12:00)
        if test_time < time(12, 0):
            return "12:00"  # 오전장 시황
        # 오후장 (12:00-15:30)
        else:
            return "15:40"  # 마감 브리핑
    
    # 미국장 시간 (22:30-05:00, 다음날)
    elif test_time >= us_open or test_time <= us_close:
        if test_time >= us_open:  # 22:30 이후
            return "19:00"  # 미국장 프리뷰
        else:  # 05:00 이전
            return "07:00"  # 미국 마켓 마감
    
    # 장 외 시간
    else:
        # 아침 (05:00-09:00)
        if us_close <= test_time < korea_open:
            return "08:00"  # 한국시장 프리뷰
        # 저녁 (15:30-22:30)
        else:
            return "19:00"  # 미국장 프리뷰

def test_scheduling_logic():
    """스케줄링 분기 로직 테스트"""
    
    print("=== 시간대별 브리핑 분기 로직 테스트 ===")
    print()
    
    # 테스트할 시간들
    test_times = [
        time(7, 0),   # 07:00 - 아침
        time(8, 0),   # 08:00 - 한국시장 프리뷰
        time(9, 0),   # 09:00 - 한국장 시작
        time(10, 0),  # 10:00 - 한국장 중
        time(12, 0),  # 12:00 - 점심
        time(14, 0),  # 14:00 - 한국장 중
        time(15, 30), # 15:30 - 한국장 마감
        time(16, 0),  # 16:00 - 장 외
        time(19, 0),  # 19:00 - 저녁
        time(22, 30), # 22:30 - 미국장 시작
        time(23, 0),  # 23:00 - 미국장 중
        time(0, 0),   # 00:00 - 자정
        time(5, 0),   # 05:00 - 미국장 마감
    ]
    
    print("시간대별 분기 결과:")
    print("-" * 50)
    
    for test_time in test_times:
        briefing_type = get_briefing_type_for_time(test_time)
        time_str = test_time.strftime("%H:%M")
        
        # 설명 추가
        description = ""
        if briefing_type == "07:00":
            description = "(미국 마켓 마감)"
        elif briefing_type == "08:00":
            description = "(한국시장 프리뷰)"
        elif briefing_type == "12:00":
            description = "(오전장 시황)"
        elif briefing_type == "15:40":
            description = "(마감 브리핑)"
        elif briefing_type == "19:00":
            description = "(미국장 프리뷰)"
        
        print(f"{time_str} → {briefing_type} {description}")
    
    print()
    print("=== GitHub Actions 스케줄링 매핑 ===")
    print()
    
    # GitHub Actions cron 스케줄과 매핑
    cron_mapping = {
        "22": "07:00",  # UTC 22:00 = KST 07:00
        "23": "08:00",  # UTC 23:00 = KST 08:00
        "3": "12:00",   # UTC 03:00 = KST 12:00
        "6": "15:40",   # UTC 06:40 = KST 15:40
        "10": "19:00",  # UTC 10:00 = KST 19:00
        "12": "19:00",  # UTC 12:00 = KST 21:00
    }
    
    print("GitHub Actions cron → KST 시간대:")
    print("-" * 40)
    for utc_hour, kst_slot in cron_mapping.items():
        kst_hour = int(utc_hour) + 9  # UTC+9
        if kst_hour >= 24:
            kst_hour -= 24
        print(f"UTC {utc_hour}:00 → KST {kst_hour:02d}:00 → {kst_slot}")
    
    print()
    print("=== 현재 시간 테스트 ===")
    print()
    
    # 현재 시간 테스트
    now = datetime.now()
    current_time = now.time()
    current_briefing = get_briefing_type_for_time(current_time)
    
    print(f"현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"선택된 브리핑: {current_briefing}")
    
    # 시장 상태 확인
    korea_open = time(9, 0)
    korea_close = time(15, 30)
    us_open = time(22, 30)
    us_close = time(5, 0)
    
    if korea_open <= current_time <= korea_close:
        print("시장 상태: 🇰🇷 한국장 운영 중")
    elif current_time >= us_open or current_time <= us_close:
        print("시장 상태: 🇺🇸 미국장 운영 중")
    else:
        print("시장 상태: 🔒 장 외 시간")

if __name__ == "__main__":
    test_scheduling_logic()
