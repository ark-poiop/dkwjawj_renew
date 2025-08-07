#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIS API 데이터 제공 시간 테스트
"""

import time
from datetime import datetime
from domestic_stock_functions import get_kospi_price, get_kosdaq_price
from kis_api_client import KISAPIClient

def test_market_data_availability():
    """시장 데이터 가용성 테스트"""
    print("=== KIS API 데이터 제공 시간 테스트 ===")
    print(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # KIS API 클라이언트
    client = KISAPIClient()
    
    # 코스피 테스트
    print("\n--- 코스피 데이터 테스트 ---")
    kospi_data = get_kospi_price()
    if kospi_data:
        print(f"현재가: {kospi_data.get('stck_prpr', 'N/A')}")
        print(f"전일대비: {kospi_data.get('prdy_vrss', 'N/A')}")
        print(f"등락률: {kospi_data.get('prdy_ctrt', 'N/A')}")
        print(f"거래량: {kospi_data.get('acml_vol', 'N/A')}")
    else:
        print("코스피 데이터 조회 실패")
    
    # 코스닥 테스트
    print("\n--- 코스닥 데이터 테스트 ---")
    kosdaq_data = get_kosdaq_price()
    if kosdaq_data:
        print(f"현재가: {kosdaq_data.get('stck_prpr', 'N/A')}")
        print(f"전일대비: {kosdaq_data.get('prdy_vrss', 'N/A')}")
        print(f"등락률: {kosdaq_data.get('prdy_ctrt', 'N/A')}")
        print(f"거래량: {kosdaq_data.get('acml_vol', 'N/A')}")
    else:
        print("코스닥 데이터 조회 실패")
    
    # 전체 시장 데이터 테스트
    print("\n--- 전체 시장 데이터 테스트 ---")
    market_data = client.get_market_data()
    print(f"데이터 소스: {market_data.get('source', 'unknown')}")
    print("지수 데이터:")
    for index_name, price in market_data.get('indices', {}).items():
        change = market_data.get('changes', {}).get(index_name, 0)
        print(f"  {index_name}: {price} ({change:+.2f})")

def test_data_persistence():
    """데이터 지속성 테스트 (여러 번 호출)"""
    print("\n=== 데이터 지속성 테스트 ===")
    
    for i in range(3):
        print(f"\n--- 테스트 {i+1} ---")
        print(f"시간: {datetime.now().strftime('%H:%M:%S')}")
        
        kospi_data = get_kospi_price()
        if kospi_data:
            price = kospi_data.get('stck_prpr', 0)
            change = kospi_data.get('prdy_vrss', 0)
            print(f"코스피: {price} ({change:+.2f})")
        else:
            print("코스피: 조회 실패")
        
        time.sleep(2)  # 2초 대기

if __name__ == "__main__":
    test_market_data_availability()
    test_data_persistence()
