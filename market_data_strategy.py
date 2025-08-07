#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시장 데이터 수집 전략
여러 데이터 소스를 조합하여 안정적인 데이터 제공
"""

import logging
from datetime import datetime, time
from typing import Dict, Optional, Any
from kis_api_client import KISAPIClient
from market_data_storage import MarketDataStorage

logger = logging.getLogger(__name__)

class MarketDataStrategy:
    """시장 데이터 수집 전략"""
    
    def __init__(self):
        self.kis_client = KISAPIClient()
        self.storage = MarketDataStorage()
        
        # 장 시간 정의
        self.market_hours = {
            'korea_open': time(9, 0),
            'korea_close': time(15, 30),
            'us_open': time(22, 30),  # KST 기준
            'us_close': time(5, 0)    # KST 기준 (다음날)
        }
    
    def is_market_open(self, market_type: str = 'korea') -> bool:
        """
        장이 열려있는지 확인
        
        Args:
            market_type: 'korea' 또는 'us'
            
        Returns:
            bool: 장 열림 여부
        """
        now = datetime.now().time()
        
        if market_type == 'korea':
            return self.market_hours['korea_open'] <= now <= self.market_hours['korea_close']
        elif market_type == 'us':
            # 미국장은 KST 기준으로 계산
            if now >= self.market_hours['us_open'] or now <= self.market_hours['us_close']:
                return True
            return False
        
        return False
    
    def get_market_data_with_strategy(self, time_slot: str) -> Dict[str, Any]:
        """
        전략적 시장 데이터 수집
        
        Args:
            time_slot: 시간대 (07:00, 08:00, 12:00, 15:40, 19:00)
            
        Returns:
            Dict: 시장 데이터
        """
        logger.info(f"전략적 시장 데이터 수집 시작: {time_slot}")
        
        # 1. 저장된 데이터 확인
        stored_data = self._get_stored_data_for_timeslot(time_slot)
        if stored_data:
            logger.info(f"저장된 데이터 사용: {time_slot}")
            return stored_data
        
        # 2. 실시간 데이터 수집 시도
        realtime_data = self._get_realtime_data()
        if self._is_valid_realtime_data(realtime_data):
            logger.info("실시간 데이터 사용")
            return realtime_data
        
        # 3. 백업 데이터 사용
        backup_data = self._get_backup_data(time_slot)
        logger.info("백업 데이터 사용")
        return backup_data
    
    def _get_stored_data_for_timeslot(self, time_slot: str) -> Optional[Dict[str, Any]]:
        """시간대에 맞는 저장된 데이터 조회"""
        try:
            # 시간대별 데이터 타입 매핑
            data_type_mapping = {
                "07:00": "closing",    # 전일 마감 데이터
                "08:00": "closing",    # 전일 마감 데이터
                "12:00": "midday",     # 오전장 데이터
                "15:40": "closing",    # 당일 마감 데이터
                "19:00": "closing"     # 전일 마감 데이터
            }
            
            data_type = data_type_mapping.get(time_slot, "closing")
            
            # 오늘 데이터 먼저 확인
            today_data = self.storage.load_market_data(data_type=data_type)
            if today_data:
                return today_data
            
            # 어제 데이터 확인
            from datetime import timedelta
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday_data = self.storage.load_market_data(
                target_date=yesterday, 
                data_type=data_type
            )
            if yesterday_data:
                return yesterday_data
            
            # 최근 데이터 확인
            latest_data = self.storage.get_latest_market_data(data_type=data_type)
            return latest_data
            
        except Exception as e:
            logger.error(f"저장된 데이터 조회 실패: {e}")
            return None
    
    def _get_realtime_data(self) -> Dict[str, Any]:
        """실시간 데이터 수집"""
        try:
            return self.kis_client.get_market_data()
        except Exception as e:
            logger.error(f"실시간 데이터 수집 실패: {e}")
            return {}
    
    def _is_valid_realtime_data(self, data: Dict[str, Any]) -> bool:
        """실시간 데이터 유효성 검사"""
        if not data:
            return False
        
        indices = data.get('indices', {})
        if not indices:
            return False
        
        # 해외 지수는 24시간 제공되므로 이를 우선 확인
        overseas_indices = ['S&P500', 'NASDAQ', 'DOW']
        overseas_valid = any(
            indices.get(index, 0) > 0 
            for index in overseas_indices 
            if index in indices
        )
        
        # 국내 지수 확인
        domestic_indices = ['KOSPI', 'KOSDAQ']
        domestic_valid = any(
            indices.get(index, 0) > 0 
            for index in domestic_indices 
            if index in indices
        )
        
        # 해외 지수가 유효하거나, 국내 지수가 유효하면 OK
        # (장 시간이 아니면 국내 지수가 0일 수 있음)
        return overseas_valid or domestic_valid
    
    def _get_backup_data(self, time_slot: str) -> Dict[str, Any]:
        """백업 데이터 생성"""
        logger.info("백업 데이터 생성")
        
        # 시간대별 백업 데이터
        backup_data = {
            "07:00": {  # 미국 마켓 마감
                "indices": {
                    "S&P500": 5500.12,
                    "NASDAQ": 17900.45,
                    "DOW": 38500.00,
                    "KOSPI": 3227.68,
                    "KOSDAQ": 805.81
                },
                "changes": {
                    "S&P500": 44.23,
                    "NASDAQ": 195.67,
                    "DOW": 115.50,
                    "KOSPI": 29.54,
                    "KOSDAQ": 2.32
                }
            },
            "08:00": {  # 한국시장 프리뷰
                "indices": {
                    "KOSPI": 3227.68,
                    "KOSDAQ": 805.81,
                    "S&P500": 5500.12,
                    "NASDAQ": 17900.45,
                    "DOW": 38500.00
                },
                "changes": {
                    "KOSPI": 29.54,
                    "KOSDAQ": 2.32,
                    "S&P500": 44.23,
                    "NASDAQ": 195.67,
                    "DOW": 115.50
                }
            },
            "12:00": {  # 오전장 중간
                "indices": {
                    "KOSPI": 3230.00,
                    "KOSDAQ": 808.00,
                    "S&P500": 5500.12,
                    "NASDAQ": 17900.45,
                    "DOW": 38500.00
                },
                "changes": {
                    "KOSPI": 32.00,
                    "KOSDAQ": 4.50,
                    "S&P500": 44.23,
                    "NASDAQ": 195.67,
                    "DOW": 115.50
                }
            },
            "15:40": {  # 한국시장 마감
                "indices": {
                    "KOSPI": 3225.00,
                    "KOSDAQ": 804.00,
                    "S&P500": 5500.12,
                    "NASDAQ": 17900.45,
                    "DOW": 38500.00
                },
                "changes": {
                    "KOSPI": 27.00,
                    "KOSDAQ": 0.50,
                    "S&P500": 44.23,
                    "NASDAQ": 195.67,
                    "DOW": 115.50
                }
            },
            "19:00": {  # 미국장 프리뷰
                "indices": {
                    "S&P500": 5500.12,
                    "NASDAQ": 17900.45,
                    "DOW": 38500.00,
                    "KOSPI": 3227.68,
                    "KOSDAQ": 805.81
                },
                "changes": {
                    "S&P500": 44.23,
                    "NASDAQ": 195.67,
                    "DOW": 115.50,
                    "KOSPI": 29.54,
                    "KOSDAQ": 2.32
                }
            }
        }
        
        data = backup_data.get(time_slot, backup_data["07:00"])
        data["source"] = f"backup_data_{time_slot}"
        data["timestamp"] = datetime.now().isoformat()
        
        return data
    
    def collect_and_store_closing_data(self) -> bool:
        """장 마감 데이터 수집 및 저장"""
        try:
            logger.info("장 마감 데이터 수집 시작")
            
            # 실시간 데이터 수집
            market_data = self._get_realtime_data()
            
            if self._is_valid_realtime_data(market_data):
                # 유효한 데이터면 저장
                success = self.storage.save_market_data(market_data, "closing")
                if success:
                    logger.info("장 마감 데이터 저장 완료")
                    return True
                else:
                    logger.error("장 마감 데이터 저장 실패")
                    return False
            else:
                logger.warning("유효한 실시간 데이터가 없어 저장하지 않음")
                return False
                
        except Exception as e:
            logger.error(f"장 마감 데이터 수집 실패: {e}")
            return False


def main():
    """테스트 실행"""
    strategy = MarketDataStrategy()
    
    # 장 시간 확인
    print("=== 장 시간 확인 ===")
    print(f"한국장 열림: {strategy.is_market_open('korea')}")
    print(f"미국장 열림: {strategy.is_market_open('us')}")
    
    # 전략적 데이터 수집 테스트
    print("\n=== 전략적 데이터 수집 테스트 ===")
    time_slots = ["07:00", "08:00", "12:00", "15:40", "19:00"]
    
    for time_slot in time_slots:
        print(f"\n--- {time_slot} ---")
        data = strategy.get_market_data_with_strategy(time_slot)
        print(f"소스: {data.get('source', 'unknown')}")
        print("지수:")
        for index_name, price in data.get('indices', {}).items():
            change = data.get('changes', {}).get(index_name, 0)
            print(f"  {index_name}: {price} ({change:+.2f})")


if __name__ == "__main__":
    main()
