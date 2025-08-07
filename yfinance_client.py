#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yahoo Finance API 클라이언트
yfinance 패키지를 사용한 실시간 해외 시장 데이터 수집
"""

import yfinance as yf
import logging
from typing import Dict, Optional, Any
import time
import random

logger = logging.getLogger(__name__)

class YahooFinanceClient:
    """Yahoo Finance API 클라이언트"""
    
    def __init__(self):
        # Yahoo Finance 심볼 매핑
        self.symbols = {
            'S&P500': '^GSPC',  # S&P 500
            'NASDAQ': '^IXIC',  # NASDAQ Composite
            'DOW': '^DJI'       # Dow Jones Industrial Average
        }
    
    def get_overseas_market_data(self) -> Dict[str, Any]:
        """
        해외 시장 데이터 수집 (yfinance 사용)
        
        Returns:
            Dict[str, Any]: 해외 시장 데이터
        """
        try:
            logger.info("Yahoo Finance API에서 실시간 데이터 수집 시작")
            
            market_data = {
                "indices": {},
                "changes": {},
                "source": "yfinance_api"
            }
            
            # 각 지수별 데이터 수집
            for index_name, symbol in self.symbols.items():
                try:
                    data = self._get_index_data(symbol, index_name)
                    if data:
                        market_data["indices"][index_name] = data["price"]
                        market_data["changes"][index_name] = data["change"]
                        logger.info(f"{index_name}: {data['price']:,.2f} ({data['change']:+.2f})")
                    
                    # API 제한 방지
                    time.sleep(random.uniform(0.5, 1.0))
                    
                except Exception as e:
                    logger.error(f"{index_name} 데이터 수집 실패: {e}")
                    continue
            
            success_count = len(market_data["indices"])
            logger.info(f"Yahoo Finance API 데이터 수집 완료: {success_count}개 지수")
            
            return market_data
            
        except Exception as e:
            logger.error(f"Yahoo Finance API 데이터 수집 중 오류: {e}")
            return {"indices": {}, "changes": {}, "source": "yfinance_api_error"}
    
    def _get_index_data(self, symbol: str, index_name: str) -> Optional[Dict[str, float]]:
        """
        개별 지수 데이터 수집
        
        Args:
            symbol: Yahoo Finance 심볼
            index_name: 지수 이름
            
        Returns:
            Optional[Dict[str, float]]: 가격과 변동폭
        """
        try:
            # Ticker 객체 생성
            ticker = yf.Ticker(symbol)
            
            # 실시간 정보 가져오기
            info = ticker.info
            
            # 현재가 추출
            current_price = info.get('regularMarketPrice')
            if current_price is None:
                logger.warning(f"{index_name}: 현재가를 찾을 수 없음")
                return None
            
            # 전일 종가
            previous_close = info.get('previousClose', current_price)
            
            # 변동폭 계산
            change = current_price - previous_close
            
            # 가격 범위 검증
            if not self._is_valid_price(current_price, index_name):
                logger.warning(f"{index_name}: 가격이 비정상적입니다 - {current_price}")
                return None
            
            return {
                "price": current_price,
                "change": change
            }
            
        except Exception as e:
            logger.error(f"{index_name} 데이터 수집 중 오류: {e}")
            return None
    
    def _is_valid_price(self, price: float, index_name: str) -> bool:
        """가격 유효성 검사"""
        if price <= 0:
            return False
            
        if index_name == 'S&P500':
            return 1000 <= price <= 10000  # S&P500 일반적인 범위
        elif index_name == 'NASDAQ':
            return 5000 <= price <= 30000  # NASDAQ 일반적인 범위
        elif index_name == 'DOW':
            return 10000 <= price <= 50000  # DOW 일반적인 범위
        return True
    
    def get_historical_data(self, symbol: str, period: str = "1d") -> Optional[Dict]:
        """
        과거 데이터 수집 (테스트용)
        
        Args:
            symbol: Yahoo Finance 심볼
            period: 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            Optional[Dict]: 과거 데이터
        """
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period)
            
            if history.empty:
                return None
            
            # 최신 데이터
            latest = history.iloc[-1]
            
            return {
                "open": latest['Open'],
                "high": latest['High'],
                "low": latest['Low'],
                "close": latest['Close'],
                "volume": latest['Volume']
            }
            
        except Exception as e:
            logger.error(f"과거 데이터 수집 중 오류: {e}")
            return None

def test_yfinance_client():
    """Yahoo Finance API 클라이언트 테스트"""
    client = YahooFinanceClient()
    
    print("=== Yahoo Finance API 테스트 ===")
    
    # 실시간 데이터 테스트
    print("\n1. 실시간 데이터 테스트:")
    data = client.get_overseas_market_data()
    
    if data.get("indices"):
        print("✅ 실시간 데이터 수집 성공:")
        for index, price in data["indices"].items():
            change = data.get("changes", {}).get(index, 0)
            print(f"  {index}: {price:,.2f} ({change:+.2f})")
    else:
        print("❌ 실시간 데이터 수집 실패")
    
    # 과거 데이터 테스트
    print("\n2. 과거 데이터 테스트 (S&P500):")
    historical = client.get_historical_data("^GSPC", "1d")
    if historical:
        print("✅ 과거 데이터 수집 성공:")
        print(f"  Open: {historical['open']:,.2f}")
        print(f"  High: {historical['high']:,.2f}")
        print(f"  Low: {historical['low']:,.2f}")
        print(f"  Close: {historical['close']:,.2f}")
        print(f"  Volume: {historical['volume']:,}")
    else:
        print("❌ 과거 데이터 수집 실패")

if __name__ == "__main__":
    test_yfinance_client()
