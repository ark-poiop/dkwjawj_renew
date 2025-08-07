#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실시간 시장 데이터 수집기
여러 API 소스를 사용하여 실시간 데이터 수집
"""

import requests
import logging
import time
import random
from typing import Dict, Optional, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class RealTimeMarketData:
    """실시간 시장 데이터 수집기"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # API 키들
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', 'demo')
        
        # 지수 심볼들
        self.symbols = {
            'S&P500': 'SPY',
            'NASDAQ': 'QQQ', 
            'DOW': 'DIA',
            'KOSPI': '^KS11',
            'KOSDAQ': '^KQ11'
        }
    
    def get_real_time_data(self) -> Dict[str, Any]:
        """
        실시간 시장 데이터 수집
        
        Returns:
            Dict[str, Any]: 실시간 시장 데이터
        """
        try:
            logger.info("실시간 시장 데이터 수집 시작")
            
            market_data = {
                "indices": {},
                "changes": {},
                "source": "real_time",
                "timestamp": datetime.now().isoformat()
            }
            
            # 해외 지수 데이터 수집
            overseas_data = self._get_overseas_real_time()
            if overseas_data:
                market_data["indices"].update(overseas_data.get("indices", {}))
                market_data["changes"].update(overseas_data.get("changes", {}))
                logger.info(f"해외 실시간 데이터 수집 완료: {len(overseas_data.get('indices', {}))}개")
            
            # 요청 간 딜레이
            time.sleep(random.uniform(1, 2))
            
            # 국내 지수 데이터 수집
            domestic_data = self._get_domestic_real_time()
            if domestic_data:
                market_data["indices"].update(domestic_data.get("indices", {}))
                market_data["changes"].update(domestic_data.get("changes", {}))
                logger.info(f"국내 실시간 데이터 수집 완료: {len(domestic_data.get('indices', {}))}개")
            
            success_count = len(market_data["indices"])
            logger.info(f"실시간 데이터 수집 완료: {success_count}개 지수")
            
            return market_data
            
        except Exception as e:
            logger.error(f"실시간 데이터 수집 중 오류: {e}")
            return {"indices": {}, "changes": {}, "source": "real_time_error"}
    
    def _get_overseas_real_time(self) -> Optional[Dict[str, Any]]:
        """해외 실시간 데이터 수집 (yfinance 사용)"""
        try:
            # yfinance 클라이언트 사용
            from yfinance_client import YahooFinanceClient
            yahoo_client = YahooFinanceClient()
            
            overseas_data = yahoo_client.get_overseas_market_data()
            
            if overseas_data and overseas_data.get("indices"):
                logger.info(f"yfinance 해외 데이터 수집 성공: {len(overseas_data.get('indices', {}))}개")
                return overseas_data
            
            return None
            
        except Exception as e:
            logger.error(f"해외 실시간 데이터 수집 중 오류: {e}")
            return None
    
    def _get_iex_data(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        IEX Cloud API에서 데이터 수집
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            Optional[Dict[str, float]]: 가격과 변동폭
        """
        try:
            url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote"
            params = {
                'token': 'pk_test_TYooMQutg1sHg4dGiZtBLbk5FyXh4e4'  # 무료 테스트 토큰
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'latestPrice' in data:
                price = float(data['latestPrice'])
                change = float(data.get('change', 0))
                
                if price > 0:
                    return {
                        "price": price,
                        "change": change
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"IEX Cloud API 오류 ({symbol}): {e}")
            return None
    
    def _get_domestic_real_time(self) -> Optional[Dict[str, Any]]:
        """국내 실시간 데이터 수집"""
        try:
            domestic_data = {
                "indices": {},
                "changes": {}
            }
            
            # 한국투자증권 API 사용
            from kis_api_client import KISAPIClient
            kis_client = KISAPIClient()
            
            kis_data = kis_client.get_market_data()
            
            # 국내 지수만 추출
            for index_name in ['KOSPI', 'KOSDAQ']:
                if index_name in kis_data.get('indices', {}):
                    price = kis_data['indices'][index_name]
                    change = kis_data.get('changes', {}).get(index_name, 0)
                    
                    # 가격이 0이 아니면 사용
                    if price > 0:
                        domestic_data["indices"][index_name] = price
                        domestic_data["changes"][index_name] = change
                        logger.info(f"{index_name}: {price:,.2f} ({change:+.2f})")
            
            return domestic_data if domestic_data["indices"] else None
            
        except Exception as e:
            logger.error(f"국내 실시간 데이터 수집 중 오류: {e}")
            return None
    
    def _get_finnhub_data(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Finnhub API에서 데이터 수집
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            Optional[Dict[str, float]]: 가격과 변동폭
        """
        try:
            url = f"https://finnhub.io/api/v1/quote"
            params = {
                'symbol': symbol,
                'token': self.finnhub_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'c' in data: # Finnhub uses 'c' for current price
                price = float(data['c'])
                change = float(data['d']) # Finnhub uses 'd' for change
                
                if price > 0:
                    return {
                        "price": price,
                        "change": change
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Finnhub API 오류 ({symbol}): {e}")
            return None

def test_real_time_market_data():
    """실시간 시장 데이터 테스트"""
    data_collector = RealTimeMarketData()
    
    print("=== 실시간 시장 데이터 테스트 ===")
    data = data_collector.get_real_time_data()
    
    print(f"수집된 데이터: {data}")
    
    if data.get("indices"):
        print("\n=== 실시간 수집 결과 ===")
        for index, price in data["indices"].items():
            change = data.get("changes", {}).get(index, 0)
            print(f"{index}: {price:,.2f} ({change:+.2f})")
    else:
        print("실시간 데이터 수집 실패")

if __name__ == "__main__":
    test_real_time_market_data()
