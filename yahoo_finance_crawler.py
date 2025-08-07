#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yahoo Finance 해외 증시 데이터 크롤러
S&P500, NASDAQ, DOW 지수 데이터 수집
"""

import requests
import logging
from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
import re
import time
import random

logger = logging.getLogger(__name__)

class YahooFinanceCrawler:
    """Yahoo Finance 해외 증시 데이터 크롤러"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Yahoo Finance 심볼 매핑
        self.symbols = {
            'S&P500': '^GSPC',
            'NASDAQ': '^IXIC', 
            'DOW': '^DJI'
        }
    
    def get_overseas_market_data(self) -> Dict[str, Any]:
        """
        해외 증시 데이터 수집
        
        Returns:
            Dict[str, Any]: 해외 증시 데이터
        """
        try:
            logger.info("Yahoo Finance에서 해외 증시 데이터 수집 시작")
            
            market_data = {
                "indices": {},
                "changes": {},
                "source": "yahoo_finance"
            }
            
            for index_name, symbol in self.symbols.items():
                try:
                    data = self._get_index_data(symbol, index_name)
                    if data:
                        market_data["indices"][index_name] = data["price"]
                        market_data["changes"][index_name] = data["change"]
                        logger.info(f"{index_name}: {data['price']} ({data['change']:+.2f})")
                    else:
                        logger.warning(f"{index_name} 데이터 수집 실패")
                        
                except Exception as e:
                    logger.error(f"{index_name} 데이터 수집 중 오류: {e}")
                    continue
                
                # 요청 간 딜레이
                time.sleep(random.uniform(1, 3))
            
            success_count = len(market_data["indices"])
            logger.info(f"해외 증시 데이터 수집 완료: {success_count}/{len(self.symbols)}개 성공")
            
            return market_data
            
        except Exception as e:
            logger.error(f"해외 증시 데이터 수집 중 오류: {e}")
            return {"indices": {}, "changes": {}, "source": "yahoo_finance_error"}
    
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
            url = f"https://finance.yahoo.com/quote/{symbol}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 가격 추출
            price_element = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
            if not price_element:
                price_element = soup.find('span', {'data-reactid': re.compile(r'.*price.*')})
            
            if not price_element:
                logger.warning(f"{index_name}: 가격 요소를 찾을 수 없음")
                return None
            
            price_text = price_element.get_text().strip()
            price = self._parse_number(price_text)
            
            if price is None:
                logger.warning(f"{index_name}: 가격 파싱 실패 - {price_text}")
                return None
            
            # 변동폭 추출
            change_element = soup.find('fin-streamer', {'data-field': 'regularMarketChange'})
            if not change_element:
                change_element = soup.find('span', {'data-reactid': re.compile(r'.*change.*')})
            
            change = 0.0
            if change_element:
                change_text = change_element.get_text().strip()
                change = self._parse_number(change_text) or 0.0
            
            return {
                "price": price,
                "change": change
            }
            
        except Exception as e:
            logger.error(f"{index_name} 데이터 수집 중 오류: {e}")
            return None
    
    def _parse_number(self, text: str) -> Optional[float]:
        """
        텍스트에서 숫자 추출
        
        Args:
            text: 숫자가 포함된 텍스트
            
        Returns:
            Optional[float]: 추출된 숫자
        """
        try:
            # 쉼표 제거 후 숫자 추출
            cleaned = re.sub(r'[^\d.-]', '', text)
            if cleaned:
                return float(cleaned)
            return None
        except (ValueError, TypeError):
            return None

def test_yahoo_finance_crawler():
    """Yahoo Finance 크롤러 테스트"""
    crawler = YahooFinanceCrawler()
    
    print("=== Yahoo Finance 해외 증시 데이터 테스트 ===")
    data = crawler.get_overseas_market_data()
    
    print(f"수집된 데이터: {data}")
    
    if data.get("indices"):
        print("\n=== 수집 결과 ===")
        for index, price in data["indices"].items():
            change = data.get("changes", {}).get(index, 0)
            print(f"{index}: {price:,.2f} ({change:+.2f})")
    else:
        print("데이터 수집 실패")

if __name__ == "__main__":
    test_yahoo_finance_crawler()
