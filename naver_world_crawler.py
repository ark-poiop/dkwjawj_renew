#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 증권 해외 지수 크롤러
실시간 해외 시장 데이터 수집
"""

import requests
import logging
from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
import re
import time
import random

logger = logging.getLogger(__name__)

class NaverWorldCrawler:
    """네이버 증권 해외 지수 크롤러"""
    
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
        
        # 네이버 증권 해외 페이지 URL
        self.url = 'https://finance.naver.com/world/'
        
        # 해외 지수 매핑
        self.index_mapping = {
            'S&P500': 'S&P500',
            'NASDAQ': '나스닥',
            'DOW': '다우'
        }
    
    def get_overseas_market_data(self) -> Dict[str, Any]:
        """
        해외 시장 데이터 수집
        
        Returns:
            Dict[str, Any]: 해외 시장 데이터
        """
        try:
            logger.info("네이버 증권 해외 페이지에서 데이터 수집 시작")
            
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            
            # 인코딩 설정
            response.encoding = 'euc-kr'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            market_data = {
                "indices": {},
                "changes": {},
                "source": "naver_world"
            }
            
            # 해외 지수 데이터 추출
            for index_name, search_term in self.index_mapping.items():
                try:
                    data = self._extract_index_data(soup, search_term, index_name)
                    if data:
                        market_data["indices"][index_name] = data["price"]
                        market_data["changes"][index_name] = data["change"]
                        logger.info(f"{index_name}: {data['price']:,.2f} ({data['change']:+.2f})")
                    
                    # 요청 간 딜레이
                    time.sleep(random.uniform(0.1, 0.3))
                    
                except Exception as e:
                    logger.error(f"{index_name} 데이터 추출 실패: {e}")
                    continue
            
            success_count = len(market_data["indices"])
            logger.info(f"해외 시장 데이터 수집 완료: {success_count}개 지수")
            
            return market_data
            
        except Exception as e:
            logger.error(f"해외 시장 데이터 수집 중 오류: {e}")
            return {"indices": {}, "changes": {}, "source": "naver_world_error"}
    
    def _extract_index_data(self, soup: BeautifulSoup, search_term: str, index_name: str) -> Optional[Dict[str, float]]:
        """
        개별 지수 데이터 추출 (HTML 구조에서)
        
        Args:
            soup: BeautifulSoup 객체
            search_term: 검색할 지수명
            index_name: 지수 이름
            
        Returns:
            Optional[Dict[str, float]]: 가격과 변동폭
        """
        try:
            # HTML 구조에서 데이터 추출
            if index_name == 'S&P500':
                # S&P500 데이터 찾기
                point_status = soup.find('dd', {'class': 'point_status'})
                if point_status:
                    # 가격 추출
                    price_element = point_status.find('strong')
                    if price_element:
                        price_text = price_element.get_text().strip().replace(',', '')
                        price = float(price_text)
                        
                        # 변동폭 추출
                        change_element = point_status.find('em')
                        if change_element:
                            change_text = change_element.get_text().strip()
                            change = float(change_text)
                            
                            # 가격 범위 검증
                            if self._is_valid_price(price, index_name):
                                return {
                                    "price": price,
                                    "change": change
                                }
            
            elif index_name == 'NASDAQ':
                # 나스닥 데이터 찾기 (NAS@IXIC)
                nasdaq_elements = soup.find_all('dd', {'class': 'point_status'})
                for element in nasdaq_elements:
                    # 나스닥 관련 텍스트가 있는지 확인
                    parent = element.find_parent()
                    if parent and '나스닥' in str(parent):
                        price_element = element.find('strong')
                        if price_element:
                            price_text = price_element.get_text().strip().replace(',', '')
                            price = float(price_text)
                            
                            change_element = element.find('em')
                            if change_element:
                                change_text = change_element.get_text().strip()
                                change = float(change_text)
                                
                                if self._is_valid_price(price, index_name):
                                    return {
                                        "price": price,
                                        "change": change
                                    }
            
            elif index_name == 'DOW':
                # 다우 데이터 찾기 (DJI@DJI)
                dow_elements = soup.find_all('dd', {'class': 'point_status'})
                for element in dow_elements:
                    # 다우 관련 텍스트가 있는지 확인
                    parent = element.find_parent()
                    if parent and '다우' in str(parent):
                        price_element = element.find('strong')
                        if price_element:
                            price_text = price_element.get_text().strip().replace(',', '')
                            price = float(price_text)
                            
                            change_element = element.find('em')
                            if change_element:
                                change_text = change_element.get_text().strip()
                                change = float(change_text)
                                
                                if self._is_valid_price(price, index_name):
                                    return {
                                        "price": price,
                                        "change": change
                                    }
            
            logger.warning(f"{index_name} 데이터를 찾을 수 없음")
            return None
            
        except Exception as e:
            logger.error(f"{index_name} 데이터 추출 중 오류: {e}")
            return None
    
    def _is_valid_price(self, price: float, index_name: str) -> bool:
        """
        가격 유효성 검사
        
        Args:
            price: 가격
            index_name: 지수 이름
            
        Returns:
            bool: 유효성 여부
        """
        if index_name == 'S&P500':
            return 1000 <= price <= 10000  # S&P500 일반적인 범위
        elif index_name == 'NASDAQ':
            return 5000 <= price <= 30000  # NASDAQ 일반적인 범위
        elif index_name == 'DOW':
            return 10000 <= price <= 50000  # DOW 일반적인 범위
        return True

def test_naver_world_crawler():
    """네이버 해외 지수 크롤러 테스트"""
    crawler = NaverWorldCrawler()
    
    print("=== 네이버 증권 해외 지수 테스트 ===")
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
    test_naver_world_crawler()
