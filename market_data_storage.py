#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시장 데이터 저장 및 관리 시스템
장 마감 직전 데이터 수집 및 일별 데이터 관리
"""

import json
import os
import logging
from datetime import datetime, date
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class MarketDataStorage:
    """시장 데이터 저장 및 관리 클래스"""
    
    def __init__(self, data_dir: str = "market_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def save_market_data(self, market_data: Dict[str, Any], data_type: str = "closing") -> bool:
        """
        시장 데이터 저장
        
        Args:
            market_data: 저장할 시장 데이터
            data_type: 데이터 타입 ('closing', 'opening', 'midday')
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            today = date.today().isoformat()
            filename = f"{today}_{data_type}.json"
            filepath = self.data_dir / filename
            
            # 저장할 데이터에 메타데이터 추가
            save_data = {
                "date": today,
                "data_type": data_type,
                "collected_at": datetime.now().isoformat(),
                "market_data": market_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"시장 데이터 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"시장 데이터 저장 실패: {e}")
            return False
    
    def load_market_data(self, target_date: Optional[str] = None, data_type: str = "closing") -> Optional[Dict[str, Any]]:
        """
        저장된 시장 데이터 로드
        
        Args:
            target_date: 대상 날짜 (YYYY-MM-DD), None이면 오늘
            data_type: 데이터 타입 ('closing', 'opening', 'midday')
            
        Returns:
            Dict: 로드된 시장 데이터 또는 None
        """
        try:
            if target_date is None:
                target_date = date.today().isoformat()
            
            filename = f"{target_date}_{data_type}.json"
            filepath = self.data_dir / filename
            
            if not filepath.exists():
                logger.warning(f"데이터 파일이 없습니다: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"시장 데이터 로드 완료: {filepath}")
            return data.get("market_data")
            
        except Exception as e:
            logger.error(f"시장 데이터 로드 실패: {e}")
            return None
    
    def get_latest_market_data(self, data_type: str = "closing") -> Optional[Dict[str, Any]]:
        """
        가장 최근의 시장 데이터 로드
        
        Args:
            data_type: 데이터 타입
            
        Returns:
            Dict: 최근 시장 데이터 또는 None
        """
        try:
            # 해당 타입의 모든 파일 찾기
            pattern = f"*_{data_type}.json"
            files = list(self.data_dir.glob(pattern))
            
            if not files:
                logger.warning(f"{data_type} 타입의 데이터 파일이 없습니다")
                return None
            
            # 가장 최근 파일 찾기
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"최근 시장 데이터 로드 완료: {latest_file}")
            return data.get("market_data")
            
        except Exception as e:
            logger.error(f"최근 시장 데이터 로드 실패: {e}")
            return None
    
    def list_available_data(self) -> Dict[str, list]:
        """
        사용 가능한 데이터 목록 조회
        
        Returns:
            Dict: 날짜별 사용 가능한 데이터 타입 목록
        """
        try:
            available_data = {}
            
            for filepath in self.data_dir.glob("*.json"):
                filename = filepath.name
                # YYYY-MM-DD_type.json 형식 파싱
                parts = filename.replace('.json', '').split('_')
                if len(parts) >= 2:
                    date_str = parts[0]
                    data_type = parts[1]
                    
                    if date_str not in available_data:
                        available_data[date_str] = []
                    available_data[date_str].append(data_type)
            
            return available_data
            
        except Exception as e:
            logger.error(f"데이터 목록 조회 실패: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """
        오래된 데이터 정리
        
        Args:
            days_to_keep: 보관할 일수
            
        Returns:
            int: 삭제된 파일 수
        """
        try:
            from datetime import timedelta
            
            cutoff_date = date.today() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            for filepath in self.data_dir.glob("*.json"):
                filename = filepath.name
                parts = filename.replace('.json', '').split('_')
                
                if len(parts) >= 2:
                    try:
                        file_date = datetime.strptime(parts[0], '%Y-%m-%d').date()
                        if file_date < cutoff_date:
                            filepath.unlink()
                            deleted_count += 1
                            logger.info(f"오래된 데이터 삭제: {filename}")
                    except ValueError:
                        continue
            
            logger.info(f"데이터 정리 완료: {deleted_count}개 파일 삭제")
            return deleted_count
            
        except Exception as e:
            logger.error(f"데이터 정리 실패: {e}")
            return 0


def main():
    """테스트 실행"""
    storage = MarketDataStorage()
    
    # 테스트 데이터
    test_data = {
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
        },
        "source": "kis_api_closing"
    }
    
    # 데이터 저장 테스트
    print("=== 데이터 저장 테스트 ===")
    success = storage.save_market_data(test_data, "closing")
    print(f"저장 성공: {success}")
    
    # 데이터 로드 테스트
    print("\n=== 데이터 로드 테스트 ===")
    loaded_data = storage.load_market_data(data_type="closing")
    print(f"로드된 데이터: {loaded_data}")
    
    # 사용 가능한 데이터 목록
    print("\n=== 사용 가능한 데이터 목록 ===")
    available = storage.list_available_data()
    print(f"사용 가능한 데이터: {available}")


if __name__ == "__main__":
    main()
